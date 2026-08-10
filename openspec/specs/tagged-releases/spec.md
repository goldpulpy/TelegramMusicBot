# Tagged Releases Specification

## Purpose

Publish traceable GitHub Releases only from version tags whose source and
declared project version have passed the repository's complete quality gate.

## Requirements

### Requirement: Trigger releases from version tags

The release system SHALL start a release run when a tag whose name begins with
`v` is pushed to the repository and SHALL associate any resulting GitHub
Release with that exact tag and commit.

#### Scenario: Version tag is pushed

- **WHEN** a `v*` tag is pushed to the repository
- **THEN** a release run starts for the tagged commit

#### Scenario: Non-version ref is pushed

- **WHEN** a branch or a tag not beginning with `v` is pushed
- **THEN** the release workflow does not start for that ref

### Requirement: Match the tag to the project version

The release system MUST require the tag name to equal `v` followed by the
`project.version` value declared in `pyproject.toml`.

#### Scenario: Tag and project version match

- **WHEN** tag `v1.2.0` points to source declaring project version `1.2.0`
- **THEN** version validation succeeds

#### Scenario: Tag and project version differ

- **WHEN** a pushed version tag does not exactly match the tagged source's
  declared project version
- **THEN** the release run fails before creating a GitHub Release

### Requirement: Gate release publication on repository checks

The release system SHALL execute the same pip-installed, directly invoked
Ruff, Pyright, and pytest gates required by continuous integration and MUST NOT
publish a GitHub Release unless every gate succeeds.

#### Scenario: Tagged source passes validation

- **WHEN** the tag version matches and every quality gate succeeds
- **THEN** the tagged source becomes eligible for release publication

#### Scenario: Tagged source fails validation

- **WHEN** any required quality gate fails for the tagged source
- **THEN** no GitHub Release is created by that run

### Requirement: Publish a GitHub Release

The release system SHALL create a non-draft GitHub Release for the validated
tag with automatically generated release notes. The release SHALL expose the
standard source archives that GitHub generates for the tag.

#### Scenario: Eligible tag is released

- **WHEN** a tagged commit satisfies version validation and all quality gates
- **THEN** a non-draft GitHub Release is published for the exact tag with
  generated release notes and source archives

### Requirement: Limit publication permissions

The release workflow MUST use only repository content read access during
validation and SHALL grant content write access only to the publication job.
It MUST NOT require production deployment secrets.

#### Scenario: Validation runs before publication

- **WHEN** the release workflow is validating tagged source
- **THEN** no content write permission or production deployment secret is
  available to the validation job
