## MODIFIED Requirements

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
