## Why

The bot's music search and download currently depend on the `vuxo7.com`
provider, whose hostname-per-query search no longer works reliably. Moving the
provider integration to `dydki.net` restores working keyword search and track
downloads behind the existing `Music`/`Track` interface.

## What Changes

- Replace the `vuxo7.com` provider with `dydki.net` in the music service.
- Search now issues `GET https://dydki.net/?mp3=<urlencoded-query>` and follows
  the server redirect (`301` with `location: /artist/<id>-<slug>/`) to the
  results page.
- Parse track results from the results container (`div.results`) instead of the
  old `ul.playlist` list: each entry exposes performer (`.track__artist`),
  title (`.track__title`), and an absolute audio URL (`data-mp3`).
- Top-hits listing parses the same results container on the `dydki.net`
  homepage.
- Search-query normalization changes from IDNA subdomain construction to query
  parameter encoding; no hostname is derived from user input.
- Track downloads use the absolute `mp3vk.sunproxy.net` URLs from `data-mp3`;
  the 50 MB guard, retries, and `MusicServiceError` translation are unchanged.
- Update provider-specific tests to match the new provider and remove the
  now-unused provider-specific request headers.

## Capabilities

### New Capabilities

- `music-service`: Provider integration contract for keyword search, top-hits
  retrieval, track metadata extraction, and audio download, independent of the
  concrete provider markup.

### Modified Capabilities

- `core-test-suite`: The music-service contract coverage requirement and its
  search-normalization scenario change because the provider URL is now a query
  string rather than an IDNA host name, and markup fixtures change from
  `ul.playlist`/`playlist-*` classes to `div.results`/`div.chkd`.

## Impact

- `service/core.py`: provider base URL, search URL construction, redirect
  handling, and results parsing selector.
- `service/data.py`: `Track.from_element` selectors for the new markup and
  removal of the provider-specific `headers` configuration.
- `service/headers.json`: removed; the provider works with default request
  headers.
- `tests/test_service.py`: updated URL, redirect, and markup fixtures.
- No changes to `Track` field shape, bot handlers, database models, or
  translations; callers continue to use `Music().search()`,
  `get_top_hits()`, and `get_audio_bytes()`.
