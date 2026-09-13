## Context

See `proposal.md` for motivation. The change is confined to the `service/`
package. The bot calls `Music().search(keyword)`, `Music().get_top_hits()`, and
`Music().get_audio_bytes(track)`; the `Track` dataclass shape and all handler
and database code stay unchanged. The current implementation builds a
per-keyword IDNA host name (`<query>.vuxo7.com`) and parses
`ul.playlist > li` markup.

The replacement provider `dydki.net` was inspected directly:

- `GET https://dydki.net/?mp3=<query>` returns `301` with
  `location: /artist/<id>-<slug>/`.
- The redirect target contains `div.results` with one `div.chkd` per track.
- Each entry has `data-mp3` (absolute `https://mp3vk.sunproxy.net/...` audio
  URL), `.track__artist` (performer), and `.track__title`.
- `https://dydki.net/` (homepage) uses the same `div.results`/`div.chkd`
  structure with ~99 entries, so it can back `get_top_hits()`.
- A sampled `data-mp3` URL downloads with `200` and a valid `content-length`
  using default request headers (no special referer required).

## Goals / Non-Goals

**Goals:**

- Switch the provider to `dydki.net` while preserving the public `Music` and
  `Track` contracts.
- Keep result ordering, performer/title/audio extraction, retry behavior, the
  50 MB size guard, and `MusicServiceError` translation.
- Keep provider-specific selector logic in one place.

**Non-Goals:**

- Changing the `Track` dataclass fields, handler flows, pagination, database
  schema, or translations.
- Migrating or re-resolving audio URLs stored in historical search records.
- Supporting multiple providers or runtime provider selection.

## Decisions

**Search request as an encoded query, not a host name.**
`build_search_query` returns `https://dydki.net/?mp3=<quote(keyword)>` using
`urllib.parse.quote`, matching the site's own `encodeURIComponent` behavior.
This removes IDNA/subdomain logic and the host-name injection surface.
Alternative considered: continue returning a bare value and append the query in
`search()`; a single URL builder keeps normalization testable and centralized.

**Rely on the HTTP client's redirect following.**
`_parse_tracks` issues a GET to the search URL with an explicit
`allow_redirects=True`, so the `301` to `/artist/...` is resolved to the final
results page transparently. The flag is passed explicitly rather than left to
the client default, and a focused test asserts it so a future change to
`allow_redirects=False` cannot silently break live search. Alternative
considered: request with `allow_redirects=False` and re-fetch the `Location`
header manually. The manual path adds a request and handling of relative URLs
for no behavioral gain, since the redirect target is always the results page.

**Parse `div.results` / `div.chkd` in `Track.from_element`.**
`_parse_tracks` locates `div.results` (replacing `ul.playlist`) and iterates
`div.chkd` children (replacing `li`). `Track.from_element` reads
`.track__artist`, `.track__title`, and the entry's own `data-mp3` attribute
(replacing `.playlist-play[data-url]`). Missing performer/title keeps raising
`ValueError`; a missing `data-mp3` keeps raising `TypeError`, preserving the
existing error contract and tests.

**Homepage backs top-hits.**
`get_top_hits()` fetches `https://dydki.net/` and reuses `_parse_tracks`, since
the homepage exposes the same results markup. No separate selector is needed.

**Constants; provider-specific headers removed.**
`BASE_URL` becomes `dydki.net`; a search-endpoint constant is introduced for
the `/?mp3=` path. `service/headers.json` is removed and `ServiceConfig` no
longer carries a `headers` field, because the sampled search, top-hits, and
audio download all succeed with aiohttp's default request headers. This drops
the `json`/`Path` file load from service startup.

## Risks / Trade-offs

- **Provider markup or class names change** → selectors live in
  `Track.from_element` and `_parse_tracks` only; fixtures in
  `tests/test_service.py` document the expected structure so breakage is caught
  by tests.
- **`data-mp3` proxy URLs may expire or require headers later** → download
  failures are already translated to `MusicServiceError` and surfaced to the
  user.
- **Anti-bot or geo/rate limiting** (the server returns an `x-geoip-country`
  header) → retries with exponential backoff are retained; failures stay
  contained by the handler's existing error handling.
- **Historical stored tracks point at the old provider** → explicitly out of
  scope; only new searches receive `dydki.net` URLs.
- **Zero-result queries may land on a page without `div.results`** →
  `_parse_tracks` should treat a missing results container consistently
  (documented failure) while an empty container returns an empty list. This is
  verified by tests rather than assumed.

## Migration Plan

1. Update selectors, constants, and URL building in `service/`.
2. Update `tests/test_service.py` fixtures and expectations, then run the
   quality gates.
3. Deploy the new code; no schema or configuration migration is required.
4. Rollback is reverting the provider constants and parser selectors.
