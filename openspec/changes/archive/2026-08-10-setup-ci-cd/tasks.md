## 1. Preserve Project Quality Commands

- [x] 1.1 Confirm the existing local Poe tasks and development dependencies
      remain unchanged.

## 2. Implement Reusable Continuous Integration

- [x] 2.1 Create `.github/workflows/ci.yml` with read-only permissions and
      triggers for pull requests to `main`, pushes to `main`, and reusable
      `workflow_call` invocation.
- [x] 2.2 Configure the CI quality job to use Python 3.12, install the existing
      hashed `requirements.txt` with pip, and install Ruff, Pyright, and pytest
      directly with pip.
- [x] 2.3 Add named steps that directly run `ruff format --check .`,
      `ruff check .`, `pyright .`, and `pytest tests`, with no Poe or runtime
      secrets in the workflow.
- [x] 2.4 Add standard-library pytest regression tests for CI triggers,
      installation, direct commands, reusable invocation, and permissions,
      without PyYAML.

## 3. Implement Tagged GitHub Releases

- [x] 3.1 Replace `.github/workflows/release.yml` with a Python-oriented workflow
      triggered only by pushed `v*` tags, with per-tag concurrency and read-only
      default permissions.
- [x] 3.2 Add a version-validation job that reads `project.version` from the
      tagged `pyproject.toml` and fails unless the ref name is exactly
      `v{project.version}`.
- [x] 3.3 Invoke the reusable CI workflow after version validation, then add a
      dependent publication job with job-scoped `contents: write` permission that
      idempotently creates the non-draft GitHub Release with generated notes.
- [x] 3.4 Add standard-library pytest regression tests for tag validation, job
      ordering, release publication, idempotency, and least privilege, without
      PyYAML.

## 4. Verify the Automation

- [x] 4.1 In the pip-installed development environment, run
      `ruff format --check .`, `ruff check .`, `pyright .`, and `pytest tests`;
      address workflow-related failures without disabling gates or expanding
      into unrelated application fixes.
- [x] 4.2 Review the final workflow YAML and repository diff, and confirm
      Actions reference neither Poe nor bot, database, registry, or deployment
      secrets.
- [x] 4.3 Document the first-release operation in the handoff: update
      `project.version`, merge the passing commit, and push the exact matching
      `v{version}` tag.
