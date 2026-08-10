## Purpose

Ensure every proposed and integrated repository change is validated against
the project's declared Python quality gates in a clean, reproducible
environment.

## ADDED Requirements

### Requirement: Validate pull requests and default-branch pushes

The continuous integration system SHALL run for every pull request targeting
the default branch and every push to the default branch.

#### Scenario: Pull request targets the default branch

- **WHEN** a pull request is opened or updated against the default branch
- **THEN** the continuous integration workflow runs for the pull request's
  current commit

#### Scenario: Commit reaches the default branch

- **WHEN** a commit is pushed to the default branch
- **THEN** the continuous integration workflow runs for that commit

### Requirement: Install the Python environment with pip

The continuous integration system SHALL use Python 3.12 and pip to install the
project's runtime requirements and the Ruff, Pyright, and pytest dependencies
required by its quality gates.

#### Scenario: CI environment is prepared

- **WHEN** a continuous integration run starts
- **THEN** pip installs the runtime requirements and required quality tools for
  Python 3.12

### Requirement: Enforce every declared quality gate

The continuous integration system SHALL invoke Ruff directly to check
formatting without modifying files and to lint the repository, SHALL invoke
Pyright directly for type checking, and SHALL invoke pytest directly for the
test suite. Actions MUST NOT invoke Poe, and the run MUST fail if any gate
fails.

#### Scenario: All quality gates pass

- **WHEN** formatting, linting, type checking, and tests all complete
  successfully
- **THEN** the continuous integration run succeeds

#### Scenario: A quality gate fails

- **WHEN** any formatting, linting, type-checking, or test command returns a
  failure
- **THEN** the continuous integration run fails and identifies the failing
  gate

#### Scenario: Actions execute quality tools

- **WHEN** a continuous integration quality step runs
- **THEN** it executes Ruff, Pyright, or pytest directly without a Poe command

### Requirement: Avoid runtime secrets

The continuous integration workflow MUST NOT require the production bot token,
database password, or other runtime credentials to execute its quality gates.

#### Scenario: CI runs for an untrusted pull request

- **WHEN** the continuous integration workflow runs without repository
  runtime secrets
- **THEN** all quality gates can still execute deterministically
