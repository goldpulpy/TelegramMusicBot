# Repository Guidelines

## Project Structure & Module Organization

`main.py` wires together aiogram, localization, and database initialization. Telegram-facing code lives in `bot/`: handlers, filters, middleware, and keyboards have dedicated packages. SQLAlchemy setup, CRUD helpers, and models belong in `database/`; music-provider integration is isolated in `service/`. Translation sources are in `locales/<language>/LC_MESSAGES/messages.po`, with language metadata in `locales/_support_languages.py`. Docker definitions are at the root, with database-only services in `dev/`.

## Build, Test, and Development Commands

- `uv sync --dev` creates the Python 3.12 environment from `pyproject.toml` and `uv.lock`.
- `cp .env.example .env` prepares configuration; replace its placeholders before starting.
- `uv run poe run` starts the bot locally with `python main.py`.
- `uv run poe check` formats, lints with Ruff, and runs Pyright.
- `docker compose up -d --build` builds and starts the bot, PostgreSQL, and Adminer; `docker compose down` stops them.
- `docker compose -f dev/docker-compose.yml up -d` starts only the development database services.

## Coding Style & Naming Conventions

Use four-space indentation, type annotations, and short docstrings for public APIs. Ruff enforces a 79-character line length and its configured `ALL` rule set. Use `snake_case` for modules, functions, and variables, `PascalCase` for classes, and uppercase names for constants. Keep async I/O explicit and register handlers through the existing setup pattern.

## Testing Guidelines

Tests are required for new behavior and bug fixes. Place them under `tests/`, mirror the production package structure, and name files `test_<module>.py` and functions `test_<behavior>()`. Mock Telegram API, PostgreSQL, and music-provider calls so tests remain deterministic. The repository does not yet declare a test runner; add one to the development dependency group and expose its command through Poe when introducing the first tests. Run `uv run poe check` before submitting changes.

## Commit & Pull Request Guidelines

History uses Conventional Commit-style subjects such as `feat:`, `refactor:`, and `change:`. Prefer an imperative summary (for example, `fix: handle empty search results`) and focused commits. PRs should explain behavior, configuration or schema effects, and verification; link related issues. Include screenshots for changed messages or keyboards, and update both language catalogs when user-facing text changes.

## Security & Configuration

Never commit `.env`, bot tokens, database passwords, or captured user data. Add new settings to `.env.example` with safe placeholders. Preserve the container's non-root runtime and validate untrusted callback and message input at handler boundaries.
