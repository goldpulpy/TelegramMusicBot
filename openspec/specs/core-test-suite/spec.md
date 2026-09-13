# Core Test Suite Specification

## Purpose

Provide a fast, deterministic safety net for the bot's core music, persistence,
access-control, presentation, and Telegram interaction behavior.

## Requirements

### Requirement: Hermetic default test execution

The automated test suite SHALL run through the repository's standard test
command without contacting Telegram, the music provider, or PostgreSQL and
without requiring application secrets.

#### Scenario: Tests run in an isolated development environment

- **WHEN** a developer runs the standard test command with no external services
  available and no production credentials configured
- **THEN** the core test suite completes using controlled test doubles for all
  network and persistence boundaries

### Requirement: Music service contract coverage

The automated test suite SHALL verify search-query encoding, result-page
redirect resolution, track parsing from the provider's results markup, session
lifecycle, provider-error translation, successful downloads, and the
configured maximum download-size guard.

#### Scenario: Provider markup is valid

- **WHEN** representative results markup contains performer, title, and audio
  URL data
- **THEN** the suite verifies that ordered track records are produced with the
  expected metadata

#### Scenario: Provider access or payload is invalid

- **WHEN** a request fails, the redirect target or required results data is
  absent, or a declared download exceeds the allowed size
- **THEN** the suite verifies the documented service failure or validation
  behavior without making a live request

#### Scenario: Search text requires normalization

- **WHEN** search text contains whitespace, punctuation, case differences, or
  international characters
- **THEN** the suite verifies the provider request carries the text as an
  encoded query value against the provider's fixed host, and that no host name
  is derived from user input

### Requirement: Persistence boundary coverage

The automated test suite SHALL verify create, read, list, update, and delete
operations, including transaction cleanup on success and rollback on failure,
using isolated session doubles.

#### Scenario: Persistence operation succeeds

- **WHEN** a CRUD operation completes successfully
- **THEN** the suite verifies the expected query or mutation, commit, refresh,
  return value, and session close behavior as applicable

#### Scenario: Persistence operation fails

- **WHEN** a database mutation or session-scoped operation raises an error
- **THEN** the suite verifies rollback and session close behavior and preserves
  the original error for the caller

#### Scenario: Search history is loaded

- **WHEN** stored history contains serialized tracks or no matching history
  exists
- **THEN** the suite verifies that typed tracks or an empty list is returned,
  respectively

### Requirement: Access and localization decision coverage

The automated test suite SHALL verify user creation and refresh, locale
selection, required-subscription decisions, supported-language decisions, and
private-chat decisions.

#### Scenario: User update is authenticated

- **WHEN** an incoming Telegram user is new or already stored
- **THEN** the suite verifies that the correct create or update path supplies the
  downstream handler with the persisted user

#### Scenario: Access filters evaluate boundary states

- **WHEN** required channels are absent, membership is allowed or denied,
  Telegram membership lookup fails, or the event is not from a private chat
- **THEN** the suite verifies the corresponding allow-or-block decision

#### Scenario: Locale is selected

- **WHEN** a user has a supported, unsupported, or missing language value
- **THEN** the suite verifies locale fallback and language-selection decisions

### Requirement: Track presentation coverage

The automated test suite SHALL verify track keyboard pagination and callback
payloads at empty, first, middle, final, and out-of-range pages.

#### Scenario: Track results span pages

- **WHEN** a track collection contains more than one page
- **THEN** the suite verifies visible track buttons, page indicators, navigation
  availability, bounded page selection, and the current-page download action

#### Scenario: Track results fit one page

- **WHEN** a track collection is empty or fits on one page
- **THEN** the suite verifies that no unnecessary pagination controls are shown

### Requirement: Core handler-flow coverage

The automated test suite SHALL verify the main search, page navigation, selected
track delivery, and current-page delivery flows at their collaborator
boundaries.

#### Scenario: Search input is accepted

- **WHEN** a user submits a non-empty search term within the supported length
- **THEN** the suite verifies provider search, history persistence, user query
  accounting, and replacement of the progress message with track controls

#### Scenario: Handler input is invalid or unusable

- **WHEN** message text or callback data is missing, malformed, out of range, or
  cannot be attached to an editable or sendable Telegram message
- **THEN** the suite verifies the handler's user-facing fallback and that
  downstream work is not performed where the handler rejects the input

#### Scenario: A track is delivered

- **WHEN** valid stored track data is selected individually or by current page
- **THEN** the suite verifies acknowledgement, bounded selection, download, and
  correctly attributed audio delivery

#### Scenario: Track delivery fails

- **WHEN** track retrieval, download, or Telegram delivery raises an error
- **THEN** the suite verifies the flow follows its recoverable error path without
  leaking the exception to the update-processing loop
