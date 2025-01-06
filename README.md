<h1 align="center">Telegram Music Bot 🎵</h1>

## Information ℹ️

- Author: `goldpulpy`
- Python version: `3.11`
- Database: `PostgreSQL`
- Pipeline deployment: `Docker Compose`

Bot for searching and listening to music in Telegram 🎶

Language support: 🇬🇧 `English`, 🇷🇺 `Russian`

## Setup application ⚙️

- First you need to create a bot in [BotFather](https://t.me/botfather)
- `.env.example` copy and rename to `.env`
- Fill environment variables

```bash
# Application
BOT_TOKEN=YOUR_BOT_TOKEN # Bot token from BotFather

# Database
POSTGRES_USER=YOUR_USER # Database user (example: root)
POSTGRES_PASSWORD=YOUR_PASSWORD # Database password (example: root)
POSTGRES_DB=YOUR_DB_NAME # Database name (example: db)
```

## Run application ▶️

1. Install `Docker`
2. Run application

```bash
docker compose up -d
```

## Stop application ⏹

```bash
docker compose down
```

## Login to database (Adminer) 🗄

Open in browser `http://your_server_ip:8080`

- Host: `db`
- Database: `YOUR_DB_NAME`
- Username: `POSTGRES_USER`
- Password: `POSTGRES_PASSWORD`

## License 📜

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details

<h6 align="center">Created by goldpulpy with ❤️</h6>
