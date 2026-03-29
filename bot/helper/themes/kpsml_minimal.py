#!/usr/bin/env python3
class KPSMLStyle:
    # ─── START ───────────────────────────────────────────────────────────────
    # async def start(client, message) ---> __main__.py
    ST_BN1_NAME = '⚙️ Source'
    ST_BN1_URL = 'https://github.com/Tamilupdates/KPSML-X'
    ST_BN2_NAME = '📡 Updates'
    ST_BN2_URL = 'https://telegram.me/KPSBots'
    ST_MSG = '''<b>◆ KPSML·X</b>
<i>Mirror · Leech · Clone — Premium Transfer Engine</i>

<blockquote>Run {help_command} to access all commands.</blockquote>'''
    ST_BOTPM = '<i>▸ Bot PM active — files delivered here.</i>'
    ST_UNAUTH = '<b>◆ ACCESS DENIED</b>\n\n<i>Unauthorized. Deploy your own instance of KPSML-X.</i>'
    OWN_TOKEN_GENERATE = '<b>⚠ Token Mismatch</b>\n\n<i>This token does not belong to you. Generate your own.</i>'
    USED_TOKEN = '<b>⚠ Token Consumed</b>\n\n<i>This token has already been used. Generate a new one.</i>'
    LOGGED_PASSWORD = '<b>▸ Session Active</b>\n\n<i>Already authenticated via password — token not required.</i>'
    ACTIVATE_BUTTON = '▸ Activate Token'
    TOKEN_MSG = '''◆ <b>LOGIN TOKEN</b>
├ <b>Token</b>   ·  <code>{token}</code>
╰ <b>Expiry</b>  ·  <i>{validity}</i>'''
    # ─────────────────────────────────────────────────────────────────────────
    # async def token_callback(_, query): ---> __main__.py
    ACTIVATED = '▸ Token Activated'
    # ─────────────────────────────────────────────────────────────────────────
    # async def login(_, message): --> __main__.py
    LOGGED_IN = '<b>▸ Already Authenticated</b>'
    INVALID_PASS = '<b>⚠ Invalid Password</b>\n\n<i>Authentication failed. Try again.</i>'
    PASS_LOGGED = '<b>▸ Authenticated</b>'
    LOGIN_USED = '<b>ℹ Usage</b>\n\n<code>/cmd [password]</code>'
    # ─────────────────────────────────────────────────────────────────────────
    # async def log(_, message): ---> __main__.py
    LOG_DISPLAY_BT = '📋 Log'
    WEB_PASTE_BT = '🌐 Paste'
    # ─────────────────────────────────────────────────────────────────────────
    # async def bot_help(client, message): ---> __main__.py
    BASIC_BT = '📌 Basic'
    USER_BT = '👤 Users'
    MICS_BT = '🔧 Misc'
    O_S_BT = '🛡 Owner'
    CLOSE_BT = '✖ Close'
    HELP_HEADER = '''◆ <b>HELP CENTRE</b>

<i>Tap any command to view usage and available flags.</i>'''

    # async def stats(client, message):
    BOT_STATS = '''◆ <b>RUNTIME</b>
<blockquote>▸ Uptime  ·  {bot_uptime}</blockquote>
◆ <b>MEMORY</b>
<blockquote expandable>  {ram_bar}  <code>{ram}%</code>
├ Used   ·  {ram_u}
├ Free   ·  {ram_f}
╰ Total  ·  {ram_t}

<b>Swap</b>
  {swap_bar}  <code>{swap}%</code>
├ Used   ·  {swap_u}
├ Free   ·  {swap_f}
╰ Total  ·  {swap_t}</blockquote>
◆ <b>DISK</b>
<blockquote>  {disk_bar}  <code>{disk}%</code>
├ Read   ·  {disk_read}
├ Write  ·  {disk_write}
├ Used   ·  {disk_u}
├ Free   ·  {disk_f}
╰ Total  ·  {disk_t}</blockquote>
'''
    SYS_STATS = '''◆ <b>SYSTEM</b>
<blockquote>├ OS Uptime  ·  {os_uptime}
├ Version    ·  {os_version}
╰ Arch       ·  {os_arch}</blockquote>
◆ <b>NETWORK</b>
<blockquote>├ Upload     ·  {up_data}
├ Download   ·  {dl_data}
├ Pkts Sent  ·  {pkt_sent}k
├ Pkts Recv  ·  {pkt_recv}k
╰ Total I/O  ·  {tl_data}</blockquote>
◆ <b>CPU</b>
<blockquote>  {cpu_bar}  <code>{cpu}%</code>
├ Freq       ·  {cpu_freq}
├ Avg Load   ·  {sys_load}
├ P-Cores    ·  {p_core}   ·  V-Cores  ·  {v_core}
├ Total      ·  {total_core}
╰ Usable     ·  {cpu_use}</blockquote>
'''
    REPO_STATS = '''◆ <b>REPOSITORY</b>
<blockquote>├ Updated    ·  {last_commit}
├ Current    ·  <code>{bot_version}</code>
├ Latest     ·  <code>{lat_version}</code>
╰ Changelog  ·  <i>{commit_details}</i></blockquote>
▸ <b>Remarks</b>  ·  <code>{remarks}</code>
'''
    BOT_LIMITS = '''◆ <b>TRANSFER LIMITS</b>
<blockquote>├ Direct    ·  {DL} GB
├ Torrent   ·  {TL} GB
├ GDrive    ·  {GL} GB
├ YT-DLP    ·  {YL} GB
├ Playlist  ·  {PL}
├ Mega      ·  {ML} GB
├ Clone     ·  {CL} GB
╰ Leech     ·  {LL} GB</blockquote>
◆ <b>RATE LIMITS</b>
<blockquote>├ Token TTL      ·  {TV}
├ User Time      ·  {UTI} / task
├ User Parallel  ·  {UT}
╰ Bot Parallel   ·  {BT}</blockquote>
'''
    # ─────────────────────────────────────────────────────────────────────────

    # async def restart(client, message): ---> __main__.py
    RESTARTING = '▸ <i>Restarting…</i>'
    # ─────────────────────────────────────────────────────────────────────────

    # async def restart_notification(): ---> __main__.py
    RESTART_SUCCESS = '''▸ <b>Restart Complete</b>
<blockquote>├ Date      ·  {date}
├ Time      ·  {time}
├ Timezone  ·  {timz}
╰ Version   ·  <code>{version}</code></blockquote>'''
    RESTARTED = '▸ <b>Bot Restarted</b>'
    # ─────────────────────────────────────────────────────────────────────────

    # async def ping(client, message): ---> __main__.py
    PING = '<i>▸ Pinging…</i>'
    PING_VALUE = '▸ <b>Pong</b>  ·  <code>{value} ms</code>'
    # ─────────────────────────────────────────────────────────────────────────

    # async def onDownloadStart(self): --> tasks_listener.py
    LINKS_START = """◆ <b>TASK QUEUED</b>
├ <b>Mode</b>  ·  {Mode}
╰ <b>By</b>    ·  {Tag}\n\n"""
    LINKS_SOURCE = """◆ <b>SOURCE</b>
╰ <b>Added</b>  ·  {On}
━━━━━━━━━━━━━━━━━━━━━
{Source}
━━━━━━━━━━━━━━━━━━━━━\n\n"""

    # async def __msg_to_reply(self): ---> pyrogramEngine.py
    PM_START =      "◆ <b>TASK STARTED</b>\n╰ <b>Track</b>  ·  <a href='{msg_link}'>Open in Chat</a>"
    L_LOG_START =   "◆ <b>LEECH STARTED</b>\n├ <b>User</b>    ·  {mention}  (<code>#{uid}</code>)\n╰ <b>Source</b>  ·  <a href='{msg_link}'>Open in Chat</a>"

    # async def onUploadComplete(): ---> tasks_listener.py
    NAME =                '<b>◆ {Name}</b>\n│\n'
    SIZE =                '├ <b>Size</b>     ·  {Size}\n'
    ELAPSE =              '├ <b>Elapsed</b>  ·  {Time}\n'
    MODE =                '├ <b>Mode</b>     ·  {Mode}\n'

    # ─── LEECH ───────────────────────────────────────────────────────────────
    L_TOTAL_FILES =       '├ <b>Files</b>    ·  {Files}\n'
    L_CORRUPTED_FILES =   '├ <b>Corrupt</b>  ·  {Corrupt}\n'
    L_CC =                '╰ <b>By</b>       ·  {Tag}\n\n'
    PM_BOT_MSG =          '▸ <i>Files sent above.</i>'
    L_BOT_MSG =           '▸ <i>Files delivered to your Bot PM.</i>'
    L_LL_MSG =            '▸ <i>Files sent — access via links below.</i>\n'

    # ─── MIRROR ──────────────────────────────────────────────────────────────
    M_TYPE =              '├ <b>Type</b>     ·  {Mimetype}\n'
    M_SUBFOLD =           '├ <b>Folders</b>  ·  {Folder}\n'
    TOTAL_FILES =         '├ <b>Files</b>    ·  {Files}\n'
    RCPATH =              '├ <b>Path</b>     ·  <code>{RCpath}</code>\n'
    M_CC =                '╰ <b>By</b>       ·  {Tag}\n\n'
    M_BOT_MSG =           '▸ <i>Links delivered to your Bot PM.</i>'

    # ─── BUTTONS ─────────────────────────────────────────────────────────────
    CLOUD_LINK =      '☁️ Drive'
    SAVE_MSG =        '💾 Save'
    RCLONE_LINK =     '🔄 RClone'
    DDL_LINK =        '🔗 {Serv}'
    SOURCE_URL =      '🔐 Source'
    INDEX_LINK_F =    '📁 Index'
    INDEX_LINK_D =    '⚡ Index'
    VIEW_LINK =       '🌐 View'
    CHECK_PM =        '📥 Bot PM'
    CHECK_LL =        '🔗 Links Log'
    MEDIAINFO_LINK =  '📊 MediaInfo'
    SCREENSHOTS =     '🖼 Preview'
    # ─────────────────────────────────────────────────────────────────────────

    # def get_readable_message(): ---> bot_utilis.py
    ####──── OVERALL MSG HEADER ────────────────────────────────────────────────
    STATUS_NAME =       '<b>◆ {Name}</b>'

    #####──── PROGRESSIVE STATUS ──────────────────────────────────────────────
    BAR =               '\n  {Bar}'
    PROCESSED =         '\n├ <b>Done</b>    ·  {Processed}'
    STATUS =            '\n├ <b>Status</b>  ·  <a href="{Url}">{Status}</a>'
    ETA =                                                  '  ·  <b>ETA</b>  ·  {Eta}'
    SPEED =             '\n├ <b>Speed</b>   ·  {Speed}'
    ELAPSED =                                     '  ·  <b>Time</b>  ·  {Elapsed}'
    ENGINE =            '\n├ <b>Engine</b>  ·  {Engine}'
    STA_MODE =          '\n├ <b>Mode</b>    ·  {Mode}'
    SEEDERS =           '\n├ <b>Seeds</b>   ·  {Seeders}  ·  '
    LEECHERS =                                               '<b>Peers</b>  ·  {Leechers}'

    ####──── SEEDING ──────────────────────────────────────────────────────────
    SEED_SIZE =      '\n├ <b>Size</b>     ·  {Size}'
    SEED_SPEED =     '\n├ <b>Speed</b>    ·  {Speed}  ·  '
    UPLOADED =                                         '<b>Uploaded</b>  ·  {Upload}'
    RATIO =          '\n├ <b>Ratio</b>    ·  {Ratio}  ·  '
    TIME =                                             '<b>Time</b>  ·  {Time}'
    SEED_ENGINE =    '\n├ <b>Engine</b>   ·  {Engine}'

    ####──── NON-PROGRESSIVE + NON SEEDING ────────────────────────────────────
    STATUS_SIZE =    '\n├ <b>Size</b>     ·  {Size}'
    NON_ENGINE =     '\n├ <b>Engine</b>   ·  {Engine}'

    ####──── OVERALL MSG FOOTER ───────────────────────────────────────────────
    USER =              '\n├ <b>User</b>    ·  <code>{User}</code>  ·  '
    ID =                                                            '<b>ID</b>  ·  <code>{Id}</code>'
    BTSEL =          '\n├ <b>Select</b>  ·  {Btsel}'
    CANCEL =         '\n╰ {Cancel}\n\n'

    ####──── FOOTER ───────────────────────────────────────────────────────────
    FOOTER =    '◆ <b>SYSTEM</b>\n'
    TASKS =     '├ <b>Tasks</b>   ·  {Tasks}\n'
    BOT_TASKS = '├ <b>Tasks</b>   ·  {Tasks}/{Ttask}  ·  <b>Free</b>  ·  {Free}\n'
    Cpu =       '├ <b>CPU</b>     ·  {cpu}%  ·  '
    FREE =                                    '<b>Free</b>  ·  {free} ({free_p}%)'
    Ram =       '\n├ <b>RAM</b>     ·  {ram}%  ·  '
    uptime =                                     '<b>Up</b>  ·  {uptime}'
    DL =        '\n╰ <b>↓</b>  {DL}/s  ·  '
    UL =                                '<b>↑</b>  {UL}/s'

    ###──── NAV BUTTONS ───────────────────────────────────────────────────────
    PREVIOUS = '◀'
    REFRESH = '· {Page} ·'
    NEXT = '▶'
    # ─────────────────────────────────────────────────────────────────────────

    # STOP_DUPLICATE_MSG: ---> clone.py, aria2_listener.py, task_manager.py
    STOP_DUPLICATE = '⚠ <b>Duplicate detected in Drive.</b>\n{content} matching result(s) found:'
    # ─────────────────────────────────────────────────────────────────────────

    # async def countNode(_, message): ----> gd_count.py
    COUNT_MSG =  '▸ <b>Counting</b>  ·  <code>{LINK}</code>'
    COUNT_NAME = '<b>◆ {COUNT_NAME}</b>\n│\n'
    COUNT_SIZE = '├ <b>Size</b>     ·  {COUNT_SIZE}\n'
    COUNT_TYPE = '├ <b>Type</b>     ·  {COUNT_TYPE}\n'
    COUNT_SUB =  '├ <b>Folders</b>  ·  {COUNT_SUB}\n'
    COUNT_FILE = '├ <b>Files</b>    ·  {COUNT_FILE}\n'
    COUNT_CC =   '╰ <b>By</b>       ·  {COUNT_CC}\n'
    # ─────────────────────────────────────────────────────────────────────────

    # LIST ---> gd_list.py
    LIST_SEARCHING = '▸ <b>Searching</b>  ·  <i>{NAME}</i>'
    LIST_FOUND = '▸ <b>{NO} result(s) found for</b> <i>{NAME}</i>'
    LIST_NOT_FOUND = '▸ <b>No results for</b> <i>{NAME}</i>'
    # ─────────────────────────────────────────────────────────────────────────

    # async def mirror_status(_, message): ----> status.py
    NO_ACTIVE_DL = '''<i>▸ No active tasks.</i>

◆ <b>SYSTEM</b>
├ <b>CPU</b>   ·  {cpu}%  ·  <b>Free</b>  ·  {free} ({free_p}%)
╰ <b>RAM</b>   ·  {ram}   ·  <b>Up</b>    ·  {uptime}
'''
    # ─────────────────────────────────────────────────────────────────────────

    # USER Setting --> user_setting.py
    USER_SETTING = '''◆ <b>USER SETTINGS</b>
<blockquote>├ <b>Name</b>      ·  {NAME}  (<code>{ID}</code>)
├ <b>Username</b>  ·  {USERNAME}
├ <b>DC</b>        ·  {DC}
╰ <b>Language</b>  ·  {LANG}</blockquote>
<i>▸ Use <b>-s</b> or <b>-set</b> to configure via argument.</i>'''

    UNIVERSAL = '''◆ <b>UNIVERSAL SETTINGS</b>  ·  {NAME}
<blockquote expandable>├ <b>YT-DLP Options</b>  ·  <code>{YT}</code>
├ <b>Daily Tasks</b>    ·  <code>{DT}</code> / day
├ <b>Last Used</b>      ·  <code>{LAST_USED}</code>
├ <b>User Session</b>   ·  <code>{USESS}</code>
├ <b>MediaInfo</b>      ·  <code>{MEDIAINFO}</code>
├ <b>Save Mode</b>      ·  <code>{SAVE_MODE}</code>
╰ <b>Bot PM</b>         ·  <code>{BOT_PM}</code></blockquote>'''

    MIRROR = '''◆ <b>MIRROR / CLONE</b>  ·  {NAME}
<blockquote expandable>├ <b>RClone Config</b>  ·  <i>{RCLONE}</i>
├ <b>Prefix</b>         ·  <code>{MPREFIX}</code>
├ <b>Suffix</b>         ·  <code>{MSUFFIX}</code>
├ <b>Rename</b>         ·  <code>{MREMNAME}</code>
├ <b>DDL Servers</b>    ·  <i>{DDL_SERVER}</i>
├ <b>TD Mode</b>        ·  <i>{TMODE}</i>
├ <b>User TDs</b>       ·  <i>{USERTD}</i>
╰ <b>Daily Mirror</b>   ·  <code>{DM}</code> / day</blockquote>'''

    LEECH = '''◆ <b>LEECH SETTINGS</b>  ·  {NAME}
<blockquote expandable>├ <b>Daily Leech</b>   ·  <code>{DL}</code> / day
├ <b>Type</b>          ·  <i>{LTYPE}</i>
├ <b>Thumbnail</b>     ·  <i>{THUMB}</i>
├ <b>Split Size</b>    ·  <code>{SPLIT_SIZE}</code>
├ <b>Equal Splits</b>  ·  <i>{EQUAL_SPLIT}</i>
├ <b>Media Group</b>   ·  <i>{MEDIA_GROUP}</i>
├ <b>Caption</b>       ·  <code>{LCAPTION}</code>
├ <b>Prefix</b>        ·  <code>{LPREFIX}</code>
├ <b>Suffix</b>        ·  <code>{LSUFFIX}</code>
├ <b>Rename</b>        ·  <code>{LREMNAME}</code>
├ <b>Dump Chats</b>    ·  <code>{LDUMP}</code>
├ <b>Attachment</b>    ·  <code>{ATTACHMENT}</code>
╰ <b>Metadata</b>      ·  <code>{METADATA}</code></blockquote>'''