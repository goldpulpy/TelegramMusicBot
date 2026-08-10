<div align="center">

# 🎵 Telegram Music Bot

<p><b>Поиск, прослушивание и отправка музыки прямо в Telegram</b></p>

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-2CA5E0?logo=telegram&logoColor=white)](https://docs.aiogram.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![CI](https://github.com/goldpulpy/TelegramMusicBot/actions/workflows/ci.yml/badge.svg)](https://github.com/goldpulpy/TelegramMusicBot/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

[🎧 Демо](https://t.me/mygoldmusicbot) · [🚀 Быстрый старт](#-быстрый-старт-в-docker) · [💻 Разработка](#-локальная-разработка) · [📝 OpenSpec](#-openspec) · [📄 Лицензия](#-лицензия)

</div>

## 📖 О проекте

Бот принимает название исполнителя или трека, находит музыку во внешнем
источнике и отправляет выбранную композицию пользователю. Интерфейс построен
на inline-кнопках, поддерживает постраничную навигацию и отправку всех треков
с текущей страницы.

Основные возможности:

- 🔎 Поиск музыки по исполнителю или названию;
- 🎧 Прослушивание и отправка аудиофайлов в Telegram;
- 🔥 Подборка популярных треков;
- 📚 История поисковых запросов в PostgreSQL;
- 🌍 Интерфейс на русском и английском языках;
- 🗣️ Автоматический выбор языка Telegram-пользователя;
- ✅ Проверка обязательной подписки на каналы;
- 🔒 Работа только в личных чатах;
- 🐳 Удобный запуск через Docker Compose;
- 📊 Adminer для просмотра и администрирования базы данных.

---

## 🚀 Быстрый старт в Docker

### 📋 Требования

- 🐳 [Docker](https://docs.docker.com/get-docker/) с Docker Compose;
- 🔑 токен Telegram-бота от [@BotFather](https://t.me/BotFather).

### 1️⃣ Клонируйте репозиторий

```bash
git clone https://github.com/goldpulpy/TelegramMusicBot.git
cd TelegramMusicBot
```

### 2️⃣ Создайте конфигурацию

```bash
cp .env.example .env
```

Откройте `.env` и как минимум замените токен и учётные данные базы:

```dotenv
BOT_TOKEN=1234567890:replace_with_your_bot_token

POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=music_bot
POSTGRES_PASSWORD=replace_with_a_strong_password
POSTGRES_DB=music_bot

ADMINER_PORT=8080
TZ=UTC
```

> [!IMPORTANT]
> Значение `POSTGRES_HOST=postgres` обязательно для запуска приложения внутри
> основного Docker Compose-стека.

### 3️⃣ Соберите и запустите сервисы

```bash
docker compose up -d --build
```

Будут запущены три контейнера:

- 🤖 `bot` - Telegram-бот;
- 🐘 `postgres` - PostgreSQL 17;
- 📊 `adminer` - веб-интерфейс базы данных.

Проверьте состояние и логи:

```bash
docker compose ps
docker compose logs -f bot
```

При первом старте приложение автоматически создаёт необходимые таблицы.
После появления сообщения о запуске polling откройте бота и отправьте
`/start`.

### 🎛️ Управление стеком

```bash
# Остановить контейнеры
docker compose down

# Перезапустить бота
docker compose restart bot

# Пересобрать после изменения кода или зависимостей
docker compose up -d --build bot
```

> [!WARNING]
> Данные PostgreSQL хранятся в именованном Docker volume и сохраняются после
> обычного `docker compose down`. Команда `docker compose down -v` удалит
> volume вместе с данными - используйте её только при необходимости.

---

## 💻 Локальная разработка

Локально удобно запускать только PostgreSQL и Adminer в Docker, а приложение -
из виртуального окружения. Так изменения кода применяются без пересборки
образа.

### 📋 Требования

- 🐍 Python 3.12;
- 📦 [uv](https://docs.astral.sh/uv/);
- 🐳 Docker с Docker Compose;
- 🔑 токен бота.

### 1️⃣ Установите зависимости

```bash
uv sync
```

Команда создаст `.venv` и установит runtime- и dev-зависимости согласно
`pyproject.toml` и `uv.lock`.

### 2️⃣ Подготовьте `.env`

```bash
cp .env.example .env
```

Для локального Python-процесса измените адрес базы на localhost:

```dotenv
BOT_TOKEN=1234567890:replace_with_your_bot_token

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=music_bot
POSTGRES_PASSWORD=replace_with_a_strong_password
POSTGRES_DB=music_bot

ADMINER_PORT=8080
TZ=UTC
```

> [!CAUTION]
> Не добавляйте `.env` и настоящие секреты в Git.

### 3️⃣ Запустите инфраструктуру

```bash
docker compose -f dev/docker-compose.yml --env-file .env up -d
```

Dev-конфигурация публикует PostgreSQL на `localhost:5432` и Adminer на
`http://localhost:8080`, но не запускает контейнер приложения.

### 4️⃣ Запустите бота

```bash
uv run poe run
```

Остановка выполняется через `Ctrl+C`, инфраструктура останавливается командой:

```bash
docker compose -f dev/docker-compose.yml down
```

---

## ⚙️ Переменные окружения

| Переменная          | Обязательна | Значение по умолчанию | Описание                                               |
| ------------------- | :---------: | --------------------- | ------------------------------------------------------ |
| `BOT_TOKEN`         |     да      | -                     | токен от BotFather; минимум 16 символов                |
| `POSTGRES_HOST`     |     нет     | `localhost`           | `postgres` в Docker, `localhost` при локальном запуске |
| `POSTGRES_PORT`     |     нет     | `5432`                | порт PostgreSQL                                        |
| `POSTGRES_USER`     |     да      | -                     | пользователь базы данных                               |
| `POSTGRES_PASSWORD` |     да      | -                     | пароль пользователя базы                               |
| `POSTGRES_DB`       |     да      | -                     | имя базы данных                                        |
| `ADMINER_PORT`      |     нет     | `8080`                | опубликованный порт Adminer; используется Compose      |
| `TZ`                |     нет     | `UTC`                 | часовой пояс контейнера PostgreSQL                     |

Настройки приложения загружаются из окружения и файла `.env`. Неизвестные
переменные игнорируются. Порт должен находиться в диапазоне от 1 до 65535.

---

## 🗄️ Работа с базой данных

Откройте [http://localhost:8080](http://localhost:8080) и используйте:

| Поле Adminer | Docker Compose               | Локальная разработка         |
| ------------ | ---------------------------- | ---------------------------- |
| Система      | PostgreSQL                   | PostgreSQL                   |
| Сервер       | `postgres`                   | `postgres`                   |
| Пользователь | значение `POSTGRES_USER`     | значение `POSTGRES_USER`     |
| Пароль       | значение `POSTGRES_PASSWORD` | значение `POSTGRES_PASSWORD` |
| База данных  | значение `POSTGRES_DB`       | значение `POSTGRES_DB`       |

Adminer работает внутри Docker-сети, поэтому сервер в его форме называется
`postgres` в обоих сценариях.

### 📋 Таблицы приложения

- 👤 `users` - профиль, язык и счётчик запросов пользователя;
- 🔎 `search_history` - запросы и найденные треки в формате JSONB;
- ✅ `required_subscriptions` - каналы, подписка на которые обязательна.

### 🧩 Настроить обязательную подписку

Чтобы включить обязательную подписку, добавьте запись в
`required_subscriptions` через Adminer. Бот должен иметь доступ к указанному
каналу, иначе проверка участника не сможет работать корректно.

### 🧩 Где размещать новый код

- обработчики - в `bot/handlers/`, с регистрацией роутера в
  `bot/handlers/__init__.py`;
- фильтры, middleware и клавиатуры - в соответствующем пакете `bot/`;
- модели и операции с данными - в `database/`;
- интеграцию с музыкальным провайдером - в `service/`;
- переводы - в `locales/<язык>/LC_MESSAGES/messages.po`;
- тесты - в `tests/`, по возможности повторяя структуру исходных пакетов.

Обработчики должны оставаться небольшими и асинхронными. Сетевые запросы и
доступ к базе выносите за их границы, ошибки записывайте через `logging`, а не
через `print`.

---

## 🧰 Команды разработчика

| Команда                   | Назначение                              |
| ------------------------- | --------------------------------------- |
| `uv sync`                 | синхронизировать `.venv` по lock-файлу  |
| `uv run poe run`          | запустить бота локально                 |
| `uv run poe format`       | отформатировать проект Ruff             |
| `uv run poe lint`         | запустить Ruff lint с автоисправлениями |
| `uv run poe type-check`   | проверить типы Pyright                  |
| `uv run poe tests`        | запустить тесты Pytest                  |
| `uv run poe lang-compile` | скомпилировать каталоги переводов       |

Перед коммитом воспроизведите проверки CI:

```bash
uv run ruff format --check .
uv run poe lint
uv run poe type-check
uv run poe tests
```

> [!TIP]
> Для Ruff включены автоисправления, включая unsafe fixes, поэтому после
> `poe lint` всегда просматривайте diff.

---

## 📝 OpenSpec

Проект использует OpenSpec и подход spec-driven development для планирования
изменений до начала реализации. OpenSpec обслуживается AI-агентом через
специализированные skills: разработчику не нужно вручную вести изменения через
OpenSpec CLI или редактировать его служебные файлы.

### 📦 Установка

Для работы skills требуется Node.js 20.19.0 или новее и глобально установленный
OpenSpec CLI:

```bash
node --version
npm install -g @fission-ai/openspec@latest
openspec --version
```

Репозиторий уже инициализирован, поэтому запускать `openspec init` после
клонирования не нужно. Другие варианты установки доступны в
[официальной документации OpenSpec](https://openspec.dev/docs/installation).

### 🔄 Рабочий процесс

1. 💭 Обсудите неясную идею с агентом через `$openspec-explore`.
2. 📝 Попросите подготовить изменение через `$openspec-propose`, описав желаемое
   поведение. Агент создаст proposal, design, delta-спецификации и список задач.
3. 👀 Проверьте и согласуйте получившийся план.
4. 🛠️ Отдельным запросом запустите реализацию через `$openspec-apply-change`.
5. 📦 После завершения и проверки реализации вызовите
   `$openspec-archive-change`. Агент синхронизирует основные спецификации и
   перенесёт завершённое изменение в архив.

Например:

```text
$openspec-propose Добавь пользователю возможность создавать плейлисты
$openspec-apply-change add-playlists
$openspec-archive-change add-playlists
```

При необходимости основные спецификации можно обновить без архивации через
`$openspec-sync-specs`. В Codex skills вызываются с префиксом `$`; в клиентах,
которые используют slash-команды, тот же workflow может быть доступен как
`/openspec-propose`, `/openspec-apply-change` и `/openspec-archive-change`.

Актуальные требования находятся в `openspec/specs/`, активные изменения - в
`openspec/changes/`, а завершённые - в `openspec/changes/archive/`. Эти файлы
нужно коммитить вместе с соответствующими изменениями кода.

---

## 🌍 Локализация

Сейчас поддерживаются `en` и `ru`. Чтобы изменить существующий перевод:

1. Отредактируйте `messages.po` нужного языка.
2. Скомпилируйте каталоги:

   ```bash
   uv run poe lang-compile
   ```

3. Перезапустите приложение и проверьте оба языка.
4. Добавьте изменённые `.po` файлы в коммит. Каталоги `.mo` игнорируются Git
   и создаются локально или при сборке Docker-образа.

Чтобы добавить язык, создайте каталог
`locales/<код>/LC_MESSAGES/messages.po`, добавьте его в список
`support_languages` в `locales/_support_languages.py`, скомпилируйте каталог и
проверьте выбор языка и команды бота.

---

## 🩺 Решение проблем

### 🐘 Приложение не подключается к PostgreSQL

- в полном Docker-стеке используйте `POSTGRES_HOST=postgres`;
- при запуске через `uv run poe run` используйте `POSTGRES_HOST=localhost`;
- проверьте `docker compose ps` и совпадение учётных данных в `.env`;
- для dev-стека убедитесь, что порт `POSTGRES_PORT` свободен.

### 🔑 Бот не запускается из-за токена

Получите новый токен у [@BotFather](https://t.me/BotFather), уберите пробелы и кавычки, затем перезапустите
приложение. Не публикуйте токен в issue, логах или commit history.

### 🌐 Изменения переводов не видны

Выполните `uv run poe lang-compile` и перезапустите приложение. Для Docker также
потребуется пересборка образа, поскольку каталоги компилируются во время build.

### 🧱 Изменения моделей не появились в базе

Автоматическое создание таблиц не обновляет уже существующую схему. Нужна
явная миграция либо пересоздание только локальной тестовой базы, если её данные
не представляют ценности.

---

## 🔐 Безопасность

- не коммитьте `.env`, токены, пароли и сгенерированные секреты;
- используйте отдельные учётные данные и сильные пароли в production;
- не публикуйте PostgreSQL наружу без необходимости;
- внимательно проверяйте обновления зависимостей и Docker-образов;

---

## 📄 Лицензия

Проект распространяется по лицензии [Apache License 2.0](LICENSE).

<div align="center">

Created with ❤️ by [goldpulpy](https://github.com/goldpulpy)

</div>
