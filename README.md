<div align="center">
  <h1>🎵 Telegram Music Bot</h1>
  <p>Powerful bot for searching and listening to music in Telegram</p>

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-compose-blue?logo=docker)
![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)

</div>

## ✨ Features

- 🎵 Instant music search and playback
- 🎧 High sound quality
- 📱 Intuitive interface
- 🌍 Multiple language support
- 🐳 Easy deployment via Docker
- 🛡️ Secure data storage in PostgreSQL
- 📝 License: Apache License 2.0

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Telegram Bot Token ([Get it from BotFather](https://t.me/botfather))

### Installation

1. Clone the repository

   ```bash
   git clone https://github.com/goldpulpy/telegram-music-bot.git
   cd telegram-music-bot
   ```

2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Configure your environment variables:

   ```env
   # Bot Configuration
   BOT_TOKEN=your_bot_token_here

   # Database Configuration
   POSTGRES_USER=your_username
   POSTGRES_PASSWORD=your_password
   POSTGRES_DB=your_database_name
   ```

### 🎮 Usage

**Start the bot:**

```bash
docker compose up -d
```

**Stop the bot:**

```bash
docker compose down
```

## 📊 Database Management

Access Adminer at `http://your_server_ip:8080`

| Setting  | Value         |
| -------- | ------------- |
| Engine   | PostgreSQL    |
| Host     | db (default)  |
| Username | your_user     |
| Password | your_password |
| Database | your_db_name  |

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

<div align="center">
  <p>Created with ❤️ by <a href="https://github.com/goldpulpy">goldpulpy</a></p>
</div>
