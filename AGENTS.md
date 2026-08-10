# Repository Guidelines

## Project Structure & Module Organization

`main.py` initializes aiogram, the database, and polling. Telegram code lives in `bot/`; keep handlers, filters, middleware, and keyboards in their matching packages. SQLAlchemy setup and models belong in `database/`, while music-provider integration belongs in `service/`. Translation catalogs are under `locales/<language>/LC_MESSAGES/`. Put tests in `tests/`, mirroring source packages where practical. Docker configuration is at the root and in `dev/`; CI workflows live in `.github/workflows/`.

## Build, Test, and Development Commands

The project requires Python 3.12 and uses `uv` with the committed `uv.lock`.

- `uv sync` — create/update `.venv` and install runtime and development dependencies.
- `uv run poe run` — start locally after exporting `.env` values and starting PostgreSQL.
- `docker compose up -d --build` — build and run the bot, PostgreSQL, and Adminer stack.
- `uv run poe lang-compile` — compile translation catalogs after editing `.po` files.
- `uv run ruff format --check . && uv run poe lint && uv run poe type-check && uv run poe tests` — reproduce CI quality gates without modifying files.
- `uv run poe format` — format the repository in place.

## Coding Style & Naming Conventions

Use four-space indentation, a 79-character line limit, and type annotations for public functions and model attributes. Ruff enforces all lint rule families except copyright notices; Pyright runs in basic mode. Use `snake_case` for modules/functions/variables, `PascalCase` for classes, and `UPPER_SNAKE_CASE` for constants. Keep handlers small and asynchronous; use loggers instead of `print`.

## Testing Guidelines

Write Pytest tests as `tests/test_<module>.py` with functions named `test_<behavior>`. Prefer isolated unit tests and mock Telegram, network, and database boundaries. No coverage threshold is configured, but new behavior and bug fixes should include focused regression tests. Run `uv run poe tests` before submitting.

## Commit & Pull Request Guidelines

History uses Conventional Commit-style subjects such as `feat: ...` and `refactor: ...`; use an imperative summary and focused commits. Pull requests should explain user-visible changes, note configuration or translation updates, link issues, and include screenshots for message-flow changes. Ensure all quality gates pass before review.

## Security & Configuration

Copy `.env.example` to `.env`; never commit bot tokens, database credentials, or generated secrets. Keep environment-specific values out of source and review dependency or Docker image updates carefully.
