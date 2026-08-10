## Why

The project has local quality commands but no repository-native automation to
enforce them on changes or to publish consistent releases. Adding GitHub
Actions will make pull requests and tagged releases reproducible and prevent a
release from being created from code that fails the project's checks.

## What Changes

- Add continuous integration for pull requests and pushes to the default
  branch using Python 3.12 and pip-installed runtime and quality dependencies.
- Invoke Ruff, Pyright, and pytest directly in Actions instead of routing CI
  commands through Poe.
- Validate formatting non-mutatively with `ruff format --check .`.
- Add tag-driven release automation for `v*` tags.
- Require the release tag version to match `project.version` and require all
  quality gates to pass before publishing.
- Create a GitHub Release for the pushed tag with generated release notes and
  the source archives GitHub provides automatically.
- Replace the existing untracked Node/NPM-oriented CD draft with the Python
  release workflow during implementation.

## Capabilities

### New Capabilities

- `continuous-integration`: Automated validation of repository changes using
  the project's Python formatting, linting, type-checking, and test commands.
- `tagged-releases`: Validated creation of GitHub Releases from version tags.

### Modified Capabilities

None.

## Impact

- Adds GitHub Actions workflow configuration under `.github/workflows/`.
- Retains Poe only as an optional local developer interface; Actions install
  and invoke their required tools independently.
- Uses GitHub-hosted runners, the repository-scoped `GITHUB_TOKEN`, Python
  3.12, and pip; no production credentials are required.
- Does not deploy the bot or publish a Python package or container image.
