#!/usr/bin/env python3
from random import choice as random_choice
from secrets import token_hex
from aiofiles.os import makedirs
from asyncio import Event, sleep, create_task, CancelledError
from mega import MegaApi, MegaListener, MegaRequest, MegaTransfer, MegaError

try:
    from mega import MegaProxy
    _MEGA_PROXY_AVAILABLE = True
except ImportError:
    _MEGA_PROXY_AVAILABLE = False

from bot import LOGGER, config_dict, download_dict_lock, download_dict, non_queued_dl, queue_dict_lock, mega_proxy_list
from bot.helper.telegram_helper.message_utils import sendMessage, sendStatusMessage
from bot.helper.ext_utils.bot_utils import get_mega_link_type, async_to_sync, sync_to_async
from bot.helper.mirror_utils.status_utils.mega_download_status import MegaDownloadStatus
from bot.helper.mirror_utils.status_utils.queue_status import QueueStatus
from bot.helper.ext_utils.task_manager import is_queued, limit_checker, stop_duplicate_check


class MegaAppListener(MegaListener):
    _NO_EVENT_ON = (MegaRequest.TYPE_LOGIN, MegaRequest.TYPE_FETCH_NODES)
    NO_ERROR = "no error"

    def __init__(self, continue_event: Event, listener):
        self.continue_event = continue_event
        self.node = None
        self.public_node = None
        self.listener = listener
        self.is_cancelled = False
        self.is_quota_error = False
        self.is_stalled = False
        self.error = None
        self.__bytes_transferred = 0
        self.__speed = 0
        self.__name = ''
        # Generation counter: incremented on each proxy-rotation retry so that
        # callbacks belonging to a stale/cancelled transfer are silently dropped.
        self._dl_gen = 0
        # One-shot flag: ensures onDownloadComplete is called at most once per
        # download attempt.  The MEGA SDK can fire onTransferFinish twice for
        # the same transfer (e.g. file-level and folder-level completions), so
        # without this guard a second callback would re-enter onDownloadComplete
        # after the task has already been cleaned up, causing a KeyError on
        # download_dict[uid].  Reset to False on each proxy-rotation retry.
        self._download_done = False
        # Guard flag set while api.startDownload is running.  Stale
        # onRequestFinish callbacks from a previous proxy session's requests
        # can fire during this window and prematurely unblock executor.do()
        # (setting continue_event + mega_listener.error) before any transfer
        # bytes arrive, causing a silent bad-state exit.  While this flag is
        # True we drop request-level callbacks so the download lifecycle is
        # driven solely by transfer callbacks and the stall watchdog.
        self._in_download_phase = False
        super().__init__()

    @property
    def speed(self):
        return self.__speed

    @property
    def downloaded_bytes(self):
        return self.__bytes_transferred

    def onRequestFinish(self, api, request, error):
        if str(error).lower() != "no error":
            # If a download is in progress, this is most likely a stale request
            # callback from the previous proxy session's cleanup (e.g. a
            # getPublicNode or login request that completed after we already
            # rotated to a new proxy and called api.startDownload).  Letting it
            # through would overwrite mega_listener.error and set continue_event,
            # prematurely unblocking executor.do(api.startDownload) with a bad
            # state and causing the "Task was destroyed but it is pending!" warning.
            if self._in_download_phase:
                LOGGER.warning(
                    f"Ignoring stale request error during download phase: {error}"
                )
                return
            # When is_cancelled is True the stall watchdog (or a transfer error)
            # has already decided to abort this session.  The MEGA SDK then cancels
            # all pending in-flight requests (login, getPublicNode, fetchNodes,
            # etc.) and fires an onRequestFinish callback for each one – typically
            # with a "Not found" error – as part of its internal cleanup.  These
            # are pure noise and must not be logged as errors or re-set
            # continue_event (which would interfere with the logout handshake that
            # follows in the proxy-rotation path).
            if self.is_cancelled:
                return
            self.error = error.copy()
            LOGGER.error(f'Mega onRequestFinishError: {self.error}')
            self.continue_event.set()
            return
        request_type = request.getType()
        if request_type == MegaRequest.TYPE_LOGIN:
            api.fetchNodes()
        elif request_type == MegaRequest.TYPE_GET_PUBLIC_NODE:
            self.public_node = request.getPublicMegaNode()
            self.__name = self.public_node.getName()
        elif request_type == MegaRequest.TYPE_FETCH_NODES:
            LOGGER.info("Fetching Root Node.")
            self.node = api.getRootNode()
            self.__name = self.node.getName()
            LOGGER.info(f"Node Name: {self.node.getName()}")
        if request_type not in self._NO_EVENT_ON or self.node and "cloud drive" not in self.__name.lower():
            self.continue_event.set()

    def onRequestTemporaryError(self, api, request, error: MegaError):
        # Temporary error; MEGA SDK retries the request internally.
        # onRequestFinish (above) will be called with the final outcome – do NOT
        # cancel the download or set the continue_event here.
        if self.is_cancelled:
            return
        LOGGER.warning(f'Mega Request error in {error}')

    def onTransferUpdate(self, api: MegaApi, transfer: MegaTransfer):
        if self.is_cancelled:
            api.cancelTransfer(transfer, None)
            self.continue_event.set()
            return
        self.__speed = transfer.getSpeed()
        self.__bytes_transferred = transfer.getTransferredBytes()

    def onTransferFinish(self, api: MegaApi, transfer: MegaTransfer, error):
        # Snapshot the generation counter at callback-entry time.  The asyncio
        # event loop can increment _dl_gen (proxy rotation) between here and the
        # conditional check below; comparing the snapshot against the live value
        # lets us detect and discard stale callbacks from superseded transfers.
        gen = self._dl_gen
        try:
            if self.is_cancelled:
                self.continue_event.set()
            elif (
                not self._download_done
                and gen == self._dl_gen
                and transfer.isFinished()
                and (transfer.isFolderTransfer() or transfer.getFileName() == self.__name)
            ):
                # Set the flag before calling onDownloadComplete so that any
                # duplicate onTransferFinish callback (MEGA SDK can fire it
                # twice for the same transfer) is silently ignored.
                self._download_done = True
                try:
                    async_to_sync(self.listener.onDownloadComplete)
                except Exception as e:
                    LOGGER.error(f"onDownloadComplete raised: {e}")
                finally:
                    # Always unblock the executor so executor.do() doesn't hang
                    # forever when onDownloadComplete raises an exception.
                    self.continue_event.set()
        except Exception as e:
            LOGGER.error(e)
            self.continue_event.set()

    def onTransferTemporaryError(self, api, transfer, error):
        # Snapshot generation at entry so a concurrent _dl_gen increment (proxy
        # rotation) is detectable; see onTransferFinish for the same pattern.
        gen = self._dl_gen
        filen = transfer.getFileName()
        state = transfer.getState()
        errStr = error.toString()
        if state in [1, 4]:
            # Sometimes MEGA (offical client) can't stream a node either and raises a temp failed error.
            # Don't break the transfer queue if transfer's in queued (1) or retrying (4) state [causes seg fault]
            return
        if self.is_cancelled:
            # Already handled; suppress duplicate error logs for the same transfer failure.
            return
        if gen != self._dl_gen:
            # Stale callback from a superseded transfer; drop it.
            return

        LOGGER.error(
            f'Mega download error in file {transfer} {filen}: {error}')
        self.error = errStr
        self.is_cancelled = True
        if 'quota' in errStr.lower():
            self.is_quota_error = True
            self.continue_event.set()
        else:
            async_to_sync(self.listener.onDownloadError,
                          f"TransferTempError: {errStr} ({filen})")
            self.continue_event.set()

    async def cancel_download(self):
        self.is_cancelled = True
        await self.listener.onDownloadError("Download Canceled by user")


class AsyncExecutor:

    def __init__(self):
        self.continue_event = Event()

    async def do(self, function, args):
        self.continue_event.clear()
        await sync_to_async(function, *args)
        await self.continue_event.wait()


# Stall detection: rotate proxy when download makes no progress for this long.
_STALL_TIMEOUT = 60        # seconds of zero progress before treating as a stall
_STALL_CHECK   = 10        # polling interval in seconds
# Slow-speed detection: MEGA throttles connections (especially without a proxy)
# to very low speeds.  The transfer makes tiny progress each interval so the
# zero-progress check never fires.  Detect this separately.
_SLOW_SPEED_THRESHOLD = 10 * 1024   # bytes/s – below this is "throttled"
_SLOW_SPEED_TIMEOUT   = 5 * 60      # seconds (5 min) of sustained low speed before stalling


async def _stall_watchdog(mega_listener, api, timeout=_STALL_TIMEOUT, interval=_STALL_CHECK):
    """Detect mid-transfer stalls and trigger proxy rotation / error reporting.

    Two conditions are caught:
    1. Zero-progress stall – the TCP connection is open but no bytes arrive
       (proxy bandwidth cap).  Triggers after `timeout` seconds.
    2. Sustained low-speed – MEGA throttles the connection (common when no
       proxy is configured) so bytes trickle in below `_SLOW_SPEED_THRESHOLD`
       B/s.  The zero-progress check would never fire because bytes do change;
       this guard triggers after `_SLOW_SPEED_TIMEOUT` seconds.
    """
    last_bytes = None
    stall_elapsed = 0
    slow_elapsed = 0
    while not mega_listener.is_cancelled:
        await sleep(interval)
        if mega_listener.is_cancelled:
            break
        current_bytes = mega_listener.downloaded_bytes
        if last_bytes is None:
            # First observation – just record the baseline.
            last_bytes = current_bytes
            continue
        delta = current_bytes - last_bytes
        if delta == 0:
            # Absolutely no progress: use the fast (zero-progress) timeout.
            stall_elapsed += interval
            slow_elapsed = 0
            if stall_elapsed >= timeout:
                LOGGER.warning(
                    f"MEGA download stalled for {stall_elapsed}s "
                    f"(zero progress – proxy bandwidth limit?), triggering stall handler"
                )
                mega_listener.is_stalled = True
                mega_listener.is_quota_error = True
                mega_listener.is_cancelled = True
                mega_listener.continue_event.set()
                break
        else:
            effective_speed = delta / interval  # bytes/s over this interval
            last_bytes = current_bytes
            stall_elapsed = 0
            if effective_speed < _SLOW_SPEED_THRESHOLD:
                # Some progress, but extremely slow (MEGA throttling).
                slow_elapsed += interval
                if slow_elapsed >= _SLOW_SPEED_TIMEOUT:
                    LOGGER.warning(
                        f"MEGA download throttled below {_SLOW_SPEED_THRESHOLD // 1024} KB/s "
                        f"for {slow_elapsed}s (MEGA IP throttling?), triggering stall handler"
                    )
                    mega_listener.is_stalled = True
                    mega_listener.is_quota_error = True
                    mega_listener.is_cancelled = True
                    mega_listener.continue_event.set()
                    break
            else:
                slow_elapsed = 0


def _apply_mega_proxy(api, mega_proxy_url):
    """Configure proxy settings on a MegaApi instance.

    Uses MegaProxy SDK bindings when available; falls back to the
    http_proxy / https_proxy environment variables otherwise (libcurl
    honours these at runtime).  Returns True if any proxy was applied.
    """
    if not mega_proxy_url:
        return False
    if _MEGA_PROXY_AVAILABLE:
        try:
            proxy = MegaProxy()
            if hasattr(proxy, 'setType') and hasattr(MegaProxy, 'PROXY_CUSTOM'):
                proxy.setType(MegaProxy.PROXY_CUSTOM)
            if hasattr(proxy, 'setURL'):
                proxy.setURL(mega_proxy_url)
                api.setProxySettings(proxy)
                return True
            # setURL not available in this SDK build; fall through to env vars.
        except Exception as e:
            LOGGER.warning(
                f"MegaProxy SDK error ({e}), falling back to environment variables for {mega_proxy_url}"
            )
    from os import environ as _env
    _env['http_proxy'] = mega_proxy_url
    _env['https_proxy'] = mega_proxy_url
    _env['HTTP_PROXY'] = mega_proxy_url
    _env['HTTPS_PROXY'] = mega_proxy_url
    return True


async def add_mega_download(mega_link, path, listener, name):
    MEGA_EMAIL = config_dict['MEGA_EMAIL']
    MEGA_PASSWORD = config_dict['MEGA_PASSWORD']

    # Read proxy list from mega_proxy.txt (one proxy per line); a snapshot is
    # taken here so that file reloads during the download don't cause issues.
    proxy_list = list(mega_proxy_list)
    tried_proxies: set = set()
    current_proxy = random_choice(proxy_list) if proxy_list else ''

    executor = AsyncExecutor()
    api = MegaApi(None, None, None, 'KPSML-X')
    folder_api = None

    try:
        # --- Login / fetch-nodes phase with per-proxy retry ---
        node = None
        while True:
            if current_proxy and _apply_mega_proxy(api, current_proxy):
                LOGGER.info(f"MEGA proxy mode enabled: {current_proxy}")

            mega_listener = MegaAppListener(executor.continue_event, listener)
            api.addListener(mega_listener)

            if MEGA_EMAIL and MEGA_PASSWORD:
                await executor.do(api.login, (MEGA_EMAIL, MEGA_PASSWORD))

            if get_mega_link_type(mega_link) == "file":
                await executor.do(api.getPublicNode, (mega_link,))
                node = mega_listener.public_node
            else:
                folder_api = MegaApi(None, None, None, 'KPSML-X')
                if current_proxy:
                    _apply_mega_proxy(folder_api, current_proxy)
                folder_api.addListener(mega_listener)
                await executor.do(folder_api.loginToFolder, (mega_link,))
                # Guard against authorizeNode(None) when login failed.
                if mega_listener.error is None and mega_listener.node is not None:
                    node = await sync_to_async(folder_api.authorizeNode, mega_listener.node)
                else:
                    node = None

            if mega_listener.error is not None:
                # Detect permanent errors that no proxy can fix (e.g. the link
                # has been deleted or is invalid).  Retrying across all proxies
                # would only flood the log with identical failures.
                error_str = str(mega_listener.error).lower()
                if 'not found' in error_str or 'not accessible' in error_str:
                    LOGGER.error(
                        f"Mega login/fetch failed with a permanent error ({mega_listener.error}); "
                        f"not retrying with other proxies."
                    )
                    try:
                        await sendMessage(listener.message,
                                          f"❌ Mega link error: {mega_listener.error}. "
                                          f"The file/folder may have been deleted or the link is invalid.")
                    except Exception:
                        pass
                    await executor.do(api.logout, ())
                    if folder_api is not None:
                        await executor.do(folder_api.logout, ())
                    return

                # Login/fetch failed – try the next proxy if one is available.
                if current_proxy:
                    tried_proxies.add(current_proxy)
                remaining = [p for p in proxy_list if p not in tried_proxies]
                if remaining:
                    current_proxy = random_choice(remaining)
                    LOGGER.warning(
                        f"Mega login failed ({mega_listener.error}), "
                        f"rotating to next proxy: {current_proxy}"
                    )
                    # Clean up the failed session before retrying.
                    await executor.do(api.logout, ())
                    api.removeListener(mega_listener)
                    if folder_api is not None:
                        await executor.do(folder_api.logout, ())
                        folder_api.removeListener(mega_listener)
                        folder_api = None
                    # Fresh executor / API object for the next attempt.
                    executor = AsyncExecutor()
                    api = MegaApi(None, None, None, 'KPSML-X')
                    continue

                # All proxies exhausted – report the error and bail out.
                await sendMessage(listener.message, str(mega_listener.error))
                await executor.do(api.logout, ())
                if folder_api is not None:
                    await executor.do(folder_api.logout, ())
                return

            break  # Login / fetch succeeded

        # Guard against a None node when the MEGA SDK reports no error but the
        # link is expired, deleted or otherwise unreachable.
        if node is None:
            await sendMessage(listener.message, "❌ Mega link is invalid or the file/folder no longer exists.")
            await executor.do(api.logout, ())
            if folder_api is not None:
                await executor.do(folder_api.logout, ())
            return

        name = name or node.getName()
        msg, button = await stop_duplicate_check(name, listener)
        if msg:
            await sendMessage(listener.message, msg, button)
            await executor.do(api.logout, ())
            if folder_api is not None:
                await executor.do(folder_api.logout, ())
            return

        gid = token_hex(5)
        size = api.getSize(node)
        if limit_exceeded := await limit_checker(size, listener, isMega=True):
            await sendMessage(listener.message, limit_exceeded)
            await executor.do(api.logout, ())
            if folder_api is not None:
                await executor.do(folder_api.logout, ())
            return
        added_to_queue, event = await is_queued(listener.uid)
        if added_to_queue:
            LOGGER.info(f"Added to Queue/Download: {name}")
            async with download_dict_lock:
                download_dict[listener.uid] = QueueStatus(
                    name, size, gid, listener, 'Dl')
            await listener.onDownloadStart()
            await sendStatusMessage(listener.message)
            await event.wait()
            async with download_dict_lock:
                if listener.uid not in download_dict:
                    await executor.do(api.logout, ())
                    if folder_api is not None:
                        await executor.do(folder_api.logout, ())
                    return
            from_queue = True
            LOGGER.info(f'Start Queued Download from Mega: {name}')
        else:
            from_queue = False

        async with download_dict_lock:
            download_dict[listener.uid] = MegaDownloadStatus(name, size, gid, mega_listener, listener.message, listener.upload_details)
        async with queue_dict_lock:
            non_queued_dl.add(listener.uid)

        if from_queue:
            LOGGER.info(f'Start Queued Download from Mega: {name}')
        else:
            await listener.onDownloadStart()
            await sendStatusMessage(listener.message)
            LOGGER.info(f"Download from Mega: {name}")

        await makedirs(path, exist_ok=True)

        while True:
            # Safety check: abort if the task was externally removed (e.g. user cancel).
            async with download_dict_lock:
                if listener.uid not in download_dict:
                    await executor.do(api.logout, ())
                    if folder_api is not None:
                        await executor.do(folder_api.logout, ())
                    return

            # Reset listener state for this download attempt.
            mega_listener.is_cancelled = False
            mega_listener.is_quota_error = False
            mega_listener.is_stalled = False
            mega_listener.error = None
            mega_listener._download_done = False
            mega_listener._in_download_phase = False

            # Run the stall watchdog concurrently with the download so that a
            # proxy bandwidth exhaustion (which stalls silently) is detected and
            # handled via the same proxy-rotation path as quota errors.
            watchdog = create_task(_stall_watchdog(mega_listener, api))
            try:
                mega_listener._in_download_phase = True
                await executor.do(api.startDownload, (node, path, name, None, False, None))
            finally:
                mega_listener._in_download_phase = False
                watchdog.cancel()
                try:
                    await watchdog
                except CancelledError:
                    pass

            # Safety net: if a request-level error arrived while we were waiting
            # for startDownload (and wasn't suppressed by _in_download_phase –
            # which guards the common stale-callback case), the download never
            # actually started.  Report it so the user gets a message instead of
            # a silent bad-state exit that leaves the download in download_dict.
            if mega_listener.error is not None and not mega_listener.is_quota_error and not mega_listener.is_cancelled:
                LOGGER.error(
                    f"Unexpected request error during MEGA download phase: {mega_listener.error}"
                )
                await listener.onDownloadError(
                    f"Mega download error: {mega_listener.error}"
                )
                await executor.do(api.logout, ())
                if folder_api is not None:
                    await executor.do(folder_api.logout, ())
                return

            if mega_listener.is_quota_error:
                if current_proxy:
                    tried_proxies.add(current_proxy)
                remaining = [p for p in proxy_list if p not in tried_proxies]
                if remaining:
                    current_proxy = random_choice(remaining)
                    reason = "stalled (proxy bandwidth limit?)" if mega_listener.is_stalled else "quota exceeded"
                    LOGGER.warning(
                        f"MEGA transfer {reason}, rotating to new proxy: {current_proxy}"
                    )
                    # Simply changing the proxy on a live session is not enough:
                    # the MEGA SDK keeps using the old (stalled/cancelled) TCP
                    # connection until it reconnects, so startDownload silently
                    # does nothing and the stall watchdog immediately fires again.
                    # We must do a full session teardown and re-login on each
                    # proxy rotation to guarantee a clean connection.
                    try:
                        await executor.do(api.logout, ())
                    except Exception:
                        pass
                    api.removeListener(mega_listener)
                    if folder_api is not None:
                        try:
                            await executor.do(folder_api.logout, ())
                        except Exception:
                            pass
                        folder_api.removeListener(mega_listener)
                        folder_api = None

                    executor = AsyncExecutor()
                    api = MegaApi(None, None, None, 'KPSML-X')
                    _apply_mega_proxy(api, current_proxy)
                    mega_listener = MegaAppListener(executor.continue_event, listener)
                    api.addListener(mega_listener)

                    if MEGA_EMAIL and MEGA_PASSWORD:
                        await executor.do(api.login, (MEGA_EMAIL, MEGA_PASSWORD))

                    if mega_listener.error is None:
                        if get_mega_link_type(mega_link) == "file":
                            await executor.do(api.getPublicNode, (mega_link,))
                            node = mega_listener.public_node
                        else:
                            folder_api = MegaApi(None, None, None, 'KPSML-X')
                            _apply_mega_proxy(folder_api, current_proxy)
                            folder_api.addListener(mega_listener)
                            await executor.do(folder_api.loginToFolder, (mega_link,))
                            if mega_listener.error is None and mega_listener.node is not None:
                                node = await sync_to_async(folder_api.authorizeNode, mega_listener.node)
                            else:
                                node = None

                    if mega_listener.error is not None or node is None:
                        LOGGER.error(
                            f"Failed to re-establish MEGA session after proxy rotation "
                            f"(proxy={current_proxy}): {mega_listener.error}"
                        )
                        # Mark the listener cancelled so any delayed SDK callbacks
                        # (login/fetchNodes completions, etc.) are silently dropped
                        # instead of creating orphaned asyncio Tasks.
                        mega_listener.is_cancelled = True
                        # Clean up the new session before reporting the error.
                        # Skipping this leaves a live MEGA SDK session with an
                        # active listener; its delayed callbacks call async_to_sync
                        # which creates asyncio Tasks that nobody holds a reference
                        # to, producing "Task was destroyed but it is pending!".
                        try:
                            await executor.do(api.logout, ())
                        except Exception:
                            pass
                        if folder_api is not None:
                            try:
                                await executor.do(folder_api.logout, ())
                            except Exception:
                                pass
                            folder_api = None
                        await listener.onDownloadError(
                            "Mega download failed: could not re-establish session after proxy rotation"
                        )
                        return

                    # Re-extract size from the new node/session (same file, but
                    # keeps the status object consistent with the active API).
                    size = api.getSize(node)

                    # Update the status object so speed / progress stats stay live.
                    async with download_dict_lock:
                        if listener.uid in download_dict:
                            download_dict[listener.uid] = MegaDownloadStatus(
                                name, size, gid, mega_listener,
                                listener.message, listener.upload_details
                            )
                    continue
                if not proxy_list:
                    if mega_listener.is_stalled:
                        LOGGER.error(
                            "MEGA download throttled/stalled with no proxy configured. "
                            "Add proxies to mega_proxy.txt to avoid MEGA IP throttling."
                        )
                        await listener.onDownloadError(
                            "Mega download failed: MEGA is throttling this IP. "
                            "Add proxies to mega_proxy.txt to use a proxy."
                        )
                    else:
                        LOGGER.error("MEGA quota exceeded with no proxy configured")
                        await listener.onDownloadError(
                            "Mega download failed: Over quota. "
                            "Add proxies to mega_proxy.txt to use a proxy."
                        )
                else:
                    LOGGER.error("Quota exceeded / stalled on all available proxies")
                    await listener.onDownloadError("Mega download failed: Over quota or stalled on all proxies")
                await executor.do(api.logout, ())
                if folder_api is not None:
                    await executor.do(folder_api.logout, ())
                return

            break

        await executor.do(api.logout, ())
        if folder_api is not None:
            await executor.do(folder_api.logout, ())

    except Exception as e:
        LOGGER.error(f"Unhandled exception in add_mega_download: {e}", exc_info=True)
        # Best-effort cleanup so MEGA SDK background threads don't linger.
        try:
            await executor.do(api.logout, ())
        except Exception:
            pass
        if folder_api is not None:
            try:
                await executor.do(folder_api.logout, ())
            except Exception:
                pass
        await listener.onDownloadError(f"Mega download error: {e}")
