## Context

See `proposal.md` for motivation. The repository is hosted on GitHub and uses
Python 3.12, `pyproject.toml`, and an existing hashed production
`requirements.txt`. Poe wraps local quality commands, but GitHub Actions will
install dependencies with pip and invoke each underlying tool directly.
The only existing workflow is an untracked CD draft for Node/NPM and does not
match this project's toolchain. The behavioral contracts are defined in the
`continuous-integration` and `tagged-releases` delta specs.

## Goals / Non-Goals

**Goals:**

- Keep one reusable definition of the Python quality gates for both CI and
  tagged releases.
- Make each failed quality gate clear in the GitHub Actions run.
- Install runtime dependencies and CI quality tools directly with pip.
- Keep release write permission isolated to the final publication job.
- Make repeated or concurrent tag events predictable.

**Non-Goals:**

- Building or publishing a Python distribution or container image.
- Deploying the bot to a host or supplying production credentials.
- Configuring GitHub branch-protection rules, which are repository settings
  outside the versioned workflow files.
- Correcting unrelated application lint, type, or test failures discovered by
  the new gates.

## Decisions

### Use GitHub Actions with a reusable CI workflow

Create `.github/workflows/ci.yml` with `pull_request` and `push` triggers for
the confirmed default branch, `main`, plus `workflow_call`. Its quality job
checks out the source, installs Python 3.12, installs the development
environment with pip, and runs four named direct commands: `ruff format
--check .`, `ruff check .`, `pyright .`, and `pytest tests`. The release
workflow calls this same workflow rather than copying the commands.

This prevents CI and release validation from drifting while keeping failures
visible by step. Separate workflow files with duplicated commands were
considered, but rejected because future quality-command changes could be
applied to only one path. Calling Poe from Actions was rejected because the
workflow can invoke each quality tool directly with clearer, thinner CI
plumbing.

### Install runtime and quality dependencies directly with pip

Actions installs the existing runtime set with `python -m pip install
--require-hashes -r requirements.txt`, then installs Ruff, Pyright, pytest, and
their dependencies directly with pip. `actions/setup-python` may cache pip
downloads using the existing `requirements.txt` as its dependency path.

Installing with `uv` in Actions was rejected in favor of the requested
pip-based setup. Existing Poe tasks remain unchanged for local developers and
are not referenced by workflow files.

### Validate and publish releases in ordered jobs

Replace `.github/workflows/release.yml` with a Python-oriented workflow for pushed
`v*` tags. A read-only job
extracts `project.version` from `pyproject.toml` with Python's `tomllib` and
compares `github.ref_name` to `v{version}`. The reusable quality workflow runs
only after the version check succeeds. A final publication job runs only after
quality succeeds and creates a non-draft GitHub Release for the existing tag
with generated notes.

Using the GitHub CLI available on GitHub-hosted runners is preferred over a
package-registry or deployment action because the required output is a GitHub
Release and its automatic source archives. Publishing to PyPI, NPM, GHCR, or a
server was rejected as outside the requested release model.

### Scope permissions and concurrency explicitly

Workflows default to `contents: read`. Only the publication job receives
`contents: write`, through the repository-provided `GITHUB_TOKEN`. Release
runs use a concurrency group derived from the full tag ref with cancellation
disabled, avoiding two publishers for the same tag while never cancelling an
active publication.

Broad workflow-level write permissions were rejected because validation jobs
do not need them. Production secrets are neither declared nor passed to the
reusable workflow.

### Test workflow contracts without a YAML dependency

Add pytest regression tests that use `pathlib` and string assertions to verify
the workflows' critical triggers, direct quality commands, tag validation,
job ordering, release behavior, and permission boundaries. The tests require
only Python's standard library and pytest; PyYAML is not declared or installed
by Actions.

A YAML parser would enable structural assertions, but was rejected to avoid an
extra direct dependency for a small pair of stable workflow files.

## Risks / Trade-offs

- [The current repository may already fail one or more direct quality gates] →
  Run each tool locally during implementation, fix only workflow/task
  integration issues in this change, and report unrelated application
  failures without weakening or skipping the gate.
- [Directly installed quality tools can change as new releases appear] → Keep
  their minimum supported versions in `pyproject.toml`, review CI failures as
  dependency updates, and pin a tool only if upstream compatibility requires
  it.
- [Setup actions can introduce supply-chain risk] → Use official GitHub
  actions at stable major versions and keep workflow permissions minimal; SHA
  pinning can be added by dependency automation later.
- [A release may already exist for a retried tag] → Make publication detect
  the existing release and succeed without creating a duplicate, while still
  failing for other publication errors.
- [Generated notes depend on GitHub's comparison base selection] → Accept
  GitHub's standard release-note generation for this initial workflow; custom
  changelog policy is outside scope.

## Migration Plan

1. Add the reusable pip-based Python CI workflow with direct quality commands
   and standard-library regression tests.
2. Verify the workflow triggers, commands, and permissions through tests and
   review.
3. Replace the contents of the untracked Node/NPM CD draft with the tag release
   workflow, retaining the `.github/workflows/release.yml` path.
4. Run Ruff, Pyright, and pytest directly, and inspect the workflow YAML.
5. Merge without creating a tag; CI begins running on configured branch and
   pull-request events.
6. For the first release, set `project.version`, merge it, and push the exact
   matching `v{version}` tag.

Rollback is a normal revert of the workflow and test commit. If an incorrect
release was published, delete the GitHub Release while retaining or deleting
the Git tag according to the repository's release policy; no runtime deployment
needs rollback.
