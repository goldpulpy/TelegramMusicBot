<div align="center">
  <h1>🎵 Музыкальный телеграм бот</h1>
  <p>Поиск и прослушивание музыки в Telegram</p>

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-compose-blue?logo=docker)
![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)
![Telegram](https://img.shields.io/badge/Telegram-bot-blue?logo=telegram)
![Adminer](https://img.shields.io/badge/Adminer-blue?logo=adminer)

</div>

## ✨ Возможности (Features)

- 🎵 Поиск и прослушивание музыки
- 🎧 Высокое качество звука
- 🌅 Аудио с обложкой
- 📱 Интуитивный интерфейс
- 🌍 Поддержка нескольких языков (английский, русский)
- 🌍 Автоопределение языка пользователя
- 🐳 Легкое развертывание через Docker
- 🛡️ Безопасное хранение данных в PostgreSQL
- 📊 Управление базой данных (Adminer)
- 📝 Лицензия: Apache License 2.0

## 🎥 Демо (Demo)

Демо бота можно посмотреть [здесь](https://t.me/mygoldmusicbot)

## 🚀 Быстрый старт (Quickstart)

### Предварительные условия (Requirements)

- Docker и Docker Compose должны быть установлены
- Токен бота ([BotFather](https://t.me/botfather))

### Установка (Installation)

1. Клонируйте репозиторий

   ```bash
   git clone https://github.com/goldpulpy/TelegramMusicBot.git
   cd TelegramMusicBot
   ```

2. Скопируйте `.env.example` в `.env`:
   ```bash
   cp .env.example .env
   ```
3. Настройте переменные окружения:

   ```env
   # Bot Configuration
   BOT_TOKEN=your_bot_token # Токен бота
   TIMEZONE=UTC # Пример: Europe/Moscow

   # Database Configuration
   POSTGRES_USER=your_username # Пример: root
   POSTGRES_PASSWORD=your_password # Пример: root
   POSTGRES_DB=your_database_name # Пример: music_bot
   ```

### 🎮 Использование (Usage)

**Запустите бот:**

```bash
docker compose up -d
```

**Остановите бот:**

```bash
docker compose down
```

## 📊 Управление базой данных (Database management)

Доступ к Adminer по адресу `http://your_server_ip:8080`

| Setting  | Value         |
| -------- | ------------- |
| Engine   | PostgreSQL    |
| Host     | db (default)  |
| Username | your_user     |
| Password | your_password |
| Database | your_db_name  |

## 📝 Лицензия (License)

Этот проект лицензирован под Apache License 2.0 - см. [LICENSE](LICENSE) для деталей.

<div align="center">
  <p>Created with ❤️ by <a href="https://github.com/goldpulpy">goldpulpy</a></p>
</div>
