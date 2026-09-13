## 1. Provider request construction

- [x] 1.1 In `service/core.py`, change `BASE_URL` to `dydki.net` and add a
      search-endpoint constant for `https://dydki.net/`; verify with a focused test
      asserting the resolved search and top-hits URLs.
- [x] 1.2 Rewrite `build_search_query` to return
      `https://dydki.net/?mp3=<urllib.parse.quote(keyword)>` and remove the IDNA
      subdomain logic; verify `tests/test_service.py::test_build_search_query`
      passes with whitespace, punctuation, case, and Cyrillic inputs.

## 2. Results parsing

- [x] 2.1 Update `_parse_tracks` in `service/core.py` to locate `div.results`
      and iterate `div.chkd` entries, relying on default redirect following; verify
      the updated parse tests return ordered tracks.
- [x] 2.2 Update `Track.from_element` in `service/data.py` to read
      `.track__artist`, `.track__title`, and the entry's own `data-mp3` attribute;
      verify valid, missing-name, and missing-audio tests.
- [x] 2.3 Confirm `get_top_hits()` fetches the `dydki.net` homepage and parses
      the same `div.results` container; verify via
      `tests/test_service.py::test_search_and_top_hits_use_expected_urls`.

## 3. Tests and configuration

- [x] 3.1 Update `tests/test_service.py` fixtures and expectations for the new
      URLs, redirect-to-results flow, and `div.results`/`div.chkd` markup, then run
      `uv run poe tests` and confirm the suite passes hermetically.
- [x] 3.2 Review `service/headers.json` and either keep it or adjust it for the
      `dydki.net`/`mp3vk.sunproxy.net` hosts; verify with a manual
      `curl`-based audio download smoke check that the headers still return
      `audio/mpeg`.
- [x] 3.3 Add a regression test proving a zero-result results container yields
      an empty list and a missing results container raises the documented error;
      verify the new test fails against the old selectors and passes after the
      change.

## 4. Quality gates

- [x] 4.1 Run `uv run ruff format --check . && uv run poe lint && uv run poe
type-check && uv run poe tests` and confirm all gates pass.
