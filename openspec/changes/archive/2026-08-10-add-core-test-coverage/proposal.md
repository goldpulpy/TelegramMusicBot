## Why

The bot's core search, download, persistence, and Telegram-routing behavior is
currently unprotected by maintained automated tests, so regressions can reach
users despite the existing test command and CI gate. A focused unit-test suite
will make the most failure-prone behavior fast and deterministic to verify.

## What Changes

- Add reusable pytest fixtures and async test support for isolated tests of
  Telegram, HTTP, and database boundaries.
- Cover music-provider query construction, HTML parsing, download limits,
  lifecycle behavior, and translated service failures without live network
  access.
- Cover generic CRUD transaction behavior and track-history conversion without
  requiring a running PostgreSQL instance.
- Cover authentication, locale, subscription, language, and private-chat
  decisions with mocked aiogram collaborators.
- Cover track keyboard pagination and the main search, page-navigation, and
  track-delivery handler paths, including invalid input and recoverable errors.
- Keep the default test run hermetic: no Telegram API, music-provider, or
  PostgreSQL access, and no dependency on developer secrets.

## Capabilities

### New Capabilities

- `core-test-suite`: Defines deterministic automated coverage for the bot's
  important service, persistence, middleware/filter, keyboard, and handler
  behavior.

### Modified Capabilities

None.

## Impact

- Adds and organizes test modules under `tests/` to mirror the source packages.
- May add pytest async/mocking development dependencies and shared test
  configuration in `pyproject.toml` and `uv.lock`.
- Exercises `service/`, `database/crud.py`, `bot/utils.py`, selected
  middleware/filters/keyboards, and the core search/download handlers without
  changing their externally visible behavior.
- The existing `uv run poe tests` command and CI test gate will run the expanded
  suite.
