

#Installing Requirements

Clone this repository:

 Build and Run the Docker Image

*Make sure you mount the app folder and install Docker following the official documentation.*

There are two methods to build and run the Docker image:

### 3.1 Using Official Docker Commands

- **Start Docker daemon** (skip if already running):

  ```bash
  sudo dockerd
  ```

- **Build the Docker image:**

  ```bash
  sudo docker build . -t kpsmlx
  ```

- **Run the image:**

  ```bash
  sudo docker run -p 80:80 -p 8080:8080 kpsmlx
  ```

- **To stop the running image:**

  First, list running containers:

  ```bash
  sudo docker ps
  ```

  Then, stop the container using its ID:

  ```bash
  sudo docker stop <container_id>
  ```

---

### 3.2 Using docker compose (Recommended)


- **Install Docker Compose (v2):**
  ```bash
  sudo apt install docker-compose-plugin

- **Build and run the Docker image in the background:**

  ```bash
  sudo docker compose up --build -d
  ```
  Note: The -d flag runs the bot in detached mode, meaning it will stay online even if you close your SSH terminal.

- **To view the real-time logs:**

  ```bash
  sudo docker compose logs -f
  ```

- **To stop the running bot:**

  ```bash
  sudo docker compose stop
  ```

- **To start the bot again (without rebuilding):**

  ```bash
  sudo docker compose start
  ```

- **To completely remove the container and clear the network:**

  ```bash
  sudo docker compose down
  ```



------

#### Docker Notes

**IMPORTANT NOTES**:

1. Set `BASE_URL_PORT` and `RCLONE_SERVE_PORT` variables to any port you want to use. Default is `80` and `8080` respectively.
2. You should stop the running image before deleting the container and you should delete the container before the image.
3. To delete the container (this will not affect on the image):

```
sudo docker container prune
```

4. To delete te images:

```
sudo docker image prune -a
```

5. Check the number of processing units of your machine with `nproc` cmd and times it by 4, then edit `AsyncIOThreadsCount` in qBittorrent.conf.
    
  </li></ol>
</details>

---


## 🛠️ Variables Descriptions

<details>
  <summary><b>View All Variables  <kbd>Click Here</kbd></b></summary>

- `BOT_TOKEN`: Telegram Bot Token that you got from [BotFather](https://t.me/BotFather). `Str`

- `OWNER_ID`: Telegram User ID (not username) of the Owner of the bot. `Int`

- `TELEGRAM_API`: This is to authenticate your Telegram account for downloading Telegram files. You can get this from <https://my.telegram.org>. `Int`

- `TELEGRAM_HASH`: This is to authenticate your Telegram account for downloading Telegram files. You can get this from <https://my.telegram.org>. `Str`

- `BASE_URL`: Valid BASE URL where the bot is deployed to use torrent web files selection.
  - ***Heroku Deployment***: Format of URL should be `https://app-name-random_code.herokuapp.com/`, where `app-name` is the name of your heroku app Paste the URL got when the App was Made. `Str`

  - ***VPS Deployment***: Format of URL should be `http://myip`, where `myip` is the IP/Domain(public) of your bot or if you have chosen port other than `80` so write it in this format `http://myip:port` (`http` and not `https`). `Str`

- `DATABASE_URL`: Database URL of MongoDb to store all your files and Vars. Adding this will be Helpful. `Str`

- `UPSTREAM_REPO`: GitLab repository URL, if your repo is private add `https://username:{githubtoken}@github.com/{username}/{reponame}` format. `Str`.
    - **NOTE**:
        - Any change in docker you need to deploy/build again with updated repo to take effect. 
        - **No Need to delete .gitignore file or any File**

- `UPSTREAM_BRANCH`: Upstream branch for update. Default is `kpsmlx`. `Str`

</details>

