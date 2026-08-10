## Context

See `proposal.md` for motivation and
`specs/core-test-suite/spec.md` for the required behavior. The application is
asynchronous and its core flows cross aiogram objects, an aiohttp-based provider,
and SQLAlchemy sessions. The repository already runs pytest from `uv run poe
tests`, but it has no maintained test modules or async pytest configuration.
Imports also construct settings and database objects, so tests must establish
safe configuration before importing affected modules.

## Goals / Non-Goals

**Goals:**

- Keep the default suite fast and deterministic enough for every CI run.
- Test behavior through public or cohesive unit boundaries while replacing only
  Telegram, HTTP, and database edges.
- Use small reusable fixtures/builders so async interaction assertions remain
  readable.
- Organize tests to mirror source packages and make ownership obvious.

**Non-Goals:**

- Live end-to-end tests against Telegram, the external provider, or PostgreSQL.
- A numeric repository-wide coverage threshold in this change.
- Exhaustive tests for static router registration, translations, configuration,
  or trivial model declarations.
- Refactoring production behavior solely to satisfy test implementation.

## Decisions

### Use pytest async support and standard-library mocks

Add `pytest-asyncio` as a development dependency and run async tests in automatic
mode. Use `AsyncMock`, `MagicMock`, and narrow fake async context managers rather
than adding a broad Telegram-specific mocking framework. This keeps dependencies
small while making awaited-call assertions explicit.

Alternative considered: wrap every coroutine with `asyncio.run`. That avoids a
dependency but makes fixtures and failure output more cumbersome across a suite
whose important behavior is predominantly asynchronous.

### Define hermetic import and boundary fixtures centrally

Use `tests/conftest.py` for deterministic test environment values and reusable
builders for tracks, users, callback/message doubles, HTTP responses, and async
sessions. Apply patches at the symbol lookup site and restore them automatically
per test. No fixture may connect to an external system.

Alternative considered: create a disposable PostgreSQL instance. That is useful
for later integration coverage, but it would slow the default suite and make its
success dependent on Docker or local infrastructure.

### Test by risk-focused source area

Mirror the source layout with focused modules for the music service and data,
CRUD and utilities, middleware and filters, inline keyboards, and core handlers.
Prefer state/output assertions for pure behavior and interaction assertions only
at genuine side-effect boundaries.

Alternative considered: one end-to-end mocked update pipeline. Such tests cover
more wiring per case but are harder to diagnose and can pass while individual
branch contracts remain unverified.

### Exercise retry semantics without real delays

Test failures at the music service boundary using controlled responses and
disable or replace retry waiting in tests. Verify the final error contract and,
where valuable, attempt counts without adding wall-clock delay.

Alternative considered: omit retry-decorated failures. That would leave a major
reliability path uncovered; allowing real exponential waits would make the suite
unacceptably slow.

### Treat current behavior as the baseline contract

Tests will encode the behavior defined by the delta spec and current source. If a
test exposes contradictory or unsafe current behavior, implementation should
record it and make the smallest justified production fix rather than weakening a
meaningful assertion. Any externally visible behavior change beyond the spec
requires a separate proposal update.

## Risks / Trade-offs

- [Mock-heavy handler tests can couple to implementation details] → Assert user-
  visible outputs and key boundary calls, and use helper builders to absorb
  aiogram object construction changes.
- [Global settings are instantiated during import] → Establish safe environment
  values before test collection imports application modules; never use real
  credentials.
- [Tenacity wrappers can add seconds to failure tests] → Replace wait behavior or
  invoke controlled retry paths with zero-delay configuration.
- [SQLAlchemy statement assertions can be brittle] → Assert returned values and
  session lifecycle first; inspect query structure only where it is the behavior
  under test.
- [No numeric coverage target permits gradual gaps] → Use the explicit scenario
  inventory as acceptance criteria and leave threshold adoption to a later,
  evidence-based change.

## Migration Plan

1. Add async test configuration and any required development dependency, then
   update the lockfile.
2. Add shared hermetic fixtures before importing application modules in tests.
3. Land tests by source area, keeping `uv run poe tests` green after each group.
4. Run formatting, linting, type checking, and the complete test command.

Rollback consists of reverting the test modules, test-only configuration, and
development dependency changes; no runtime data or schema migration is involved.
