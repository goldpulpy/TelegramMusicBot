## Purpose

Define the provider-independent contract for music discovery and retrieval so
the bot can search a remote provider, present ordered track results, and stream
the selected audio to users.

## ADDED Requirements

### Requirement: Keyword search returns ordered tracks

The music service SHALL expose a keyword search operation that accepts a
non-empty query, performs a provider lookup, and returns an ordered list of
tracks whose order matches the provider's result order.

#### Scenario: Provider returns matching tracks

- **WHEN** a keyword query is submitted and the provider responds with a
  results page containing one or more entries
- **THEN** the service returns tracks ordered as displayed, each carrying a
  performer, a title, and an absolute audio URL

#### Scenario: Provider reports no matches

- **WHEN** the results page is reachable but contains no track entries
- **THEN** the service returns an empty list

#### Scenario: Provider cannot be reached

- **WHEN** no HTTP session is available or the request fails with a network
  error or timeout
- **THEN** the service raises `MusicServiceError` without returning partial
  results

### Requirement: Provider lookup follows the search redirect

The music service SHALL resolve the provider's redirect from its search
endpoint to the canonical results page before parsing tracks.

#### Scenario: Search endpoint redirects

- **WHEN** the search endpoint responds with a redirect that points to the
  results page
- **THEN** the service requests the redirect target and parses tracks from that
  page

### Requirement: Track metadata is extracted from provider markup

The music service SHALL extract each track's performer, title, and absolute
audio URL from the provider's results container.

#### Scenario: Entry exposes complete metadata

- **WHEN** a results entry provides performer, title, and audio URL values
- **THEN** the resulting track contains those exact values and its zero-based
  position in the result list

#### Scenario: Entry omits performer or title

- **WHEN** a results entry lacks performer or title data
- **THEN** the service raises an error rather than emitting a partial track

#### Scenario: Entry omits the audio URL

- **WHEN** a results entry lacks an audio URL
- **THEN** the service raises an error rather than emitting a track without
  downloadable audio

### Requirement: Top-hits listing

The music service SHALL expose a top-hits operation that returns the provider's
default catalog list using the same parsing rules as keyword search.

#### Scenario: Default catalog is retrieved

- **WHEN** the top-hits operation runs against the provider's landing page
- **THEN** the service returns ordered tracks parsed from the page's results
  container

### Requirement: Search text is safely encoded

The music service SHALL encode user-supplied search text into the provider
search request so that whitespace, punctuation, case differences, and
international characters cannot alter the request structure, and it SHALL NOT
derive a network host name from user input.

#### Scenario: Search text contains special characters

- **WHEN** a keyword contains whitespace, punctuation, case differences, or
  international characters
- **THEN** the generated provider request carries the text as an encoded query
  value and remains a valid request to the provider's fixed host

### Requirement: Audio is downloaded with a size guard

The music service SHALL download a track's audio bytes from its absolute audio
URL, reuse the configured HTTP session and timeout, reject downloads whose
declared size exceeds the configured maximum, and translate network failures
into `MusicServiceError`.

#### Scenario: Download succeeds

- **WHEN** a track with a valid audio URL is downloaded
- **THEN** the service returns the full audio payload

#### Scenario: Declared size exceeds the limit

- **WHEN** the provider declares a content length above the configured maximum
  download size
- **THEN** the service raises `MusicServiceError` before reading the payload

#### Scenario: Download fails

- **WHEN** the audio request fails with a network error or timeout
- **THEN** the service raises `MusicServiceError`
