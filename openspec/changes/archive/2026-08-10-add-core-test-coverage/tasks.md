## 1. Test Infrastructure

- [x] 1.1 Add `pytest-asyncio` to the development dependencies, configure async
      test discovery, and update `uv.lock`.
- [x] 1.2 Add `tests/conftest.py` with safe import-time configuration and reusable
      track, Telegram-event, HTTP-response, and async-session fixtures.
- [x] 1.3 Verify an isolated test run starts without a `.env` file, external
      services, network access, or production credentials.

## 2. Music Provider Tests

- [x] 2.1 Add parameterized tests for search-query cleaning, case and whitespace
      normalization, punctuation removal, and international-domain encoding.
- [x] 2.2 Add track-conversion and playlist-parsing tests for valid metadata,
      stable indexes, and missing required markup.
- [x] 2.3 Add session lifecycle and search/top-hits tests that verify the expected
      provider URL and reject use without an initialized session.
- [x] 2.4 Add zero-delay failure tests for HTTP errors, timeouts, malformed
      playlists, successful audio reads, and oversized declared downloads.

## 3. Persistence and Utility Tests

- [x] 3.1 Add CRUD read and list tests using isolated SQLAlchemy session/result
      doubles.
- [x] 3.2 Add CRUD create, update, and delete success tests covering add/delete,
      commit, refresh, returned values, and session closure.
- [x] 3.3 Add CRUD failure tests covering rollback, session closure, and original
      exception propagation from mutation and session-scoped failures.
- [x] 3.4 Add utility tests for reconstructing tracks from search history, missing
      history, profile-photo URL creation, and absent profile photos or file paths.

## 4. Middleware and Filter Tests

- [x] 4.1 Add authentication middleware tests for new-user creation,
      existing-user refresh, data injection, downstream handler invocation, and
      propagated persistence failure.
- [x] 4.2 Add locale and language-filter tests for stored, missing, supported,
      and unsupported language values.
- [x] 4.3 Add required-subscription tests for no configured channels, allowed and
      denied membership statuses, inaccessible chats, and failed member lookup.
- [x] 4.4 Add private-chat filter tests for private and non-private messages,
      callbacks with messages, and callbacks without editable messages.

## 5. Presentation and Handler Tests

- [x] 5.1 Add inline track-keyboard tests for empty and single-page results plus
      first, middle, last, negative, and excessive page requests.
- [x] 5.2 Add search handler tests for missing, blank, oversized, and valid text,
      including progress messaging, provider lookup, history creation, query-count
      update, and result keyboard rendering.
- [x] 5.3 Add track-list and page-navigation tests for valid callbacks, missing or
      malformed data, non-editable messages, and recoverable Telegram edit errors.
- [x] 5.4 Add selected-track and current-page delivery tests for acknowledgement,
      bounded slicing, download, metadata/caption/thumbnail delivery, and missing
      chat or message states.
- [x] 5.5 Add handler failure-path tests that verify user-facing fallbacks where
      defined and prevent exceptions from escaping the update-processing boundary.

## 6. Verification

- [x] 6.1 Run `uv run poe tests` and confirm the suite remains hermetic and avoids
      retry-induced delays.
- [x] 6.2 Run `uv run ruff format --check .`, `uv run poe lint`, and `uv run poe
type-check`, then resolve all test-related failures.
- [x] 6.3 Review the completed suite against every scenario in the
      `core-test-suite` spec and fill any acceptance-criteria gaps.
