# connector_ops

A collection of utilities for working with Airbyte connectors.

# Setup

## Installation

`connector_ops` tools use [Poetry](https://github.com/python-poetry/poetry) to manage dependencies,
and targets Python 3.10 and higher.

Assuming you're in Airbyte repo root:

```bash
cd airbyte-ci/connectors/connector_ops
poetry install
```

## Usage

`connector_ops` provides a set of tools that verify connector characteristics. They're intended to
be used in CI. They will detect the list of connectors that are modified compared to `master` branch
of the repository, and only run checks on them. You can run them locally, too, with
`poetry run TOOL_NAME`.

- `write-review-requirements-file` writes required reviewers github action file.
- `print-mandatory-reviewers` prints out the GitHub comment with required reviewers.

## Contributing to `connector_ops`

### Running tests

To run tests locally:

```bash
poetry run pytest
```

## Changelog

- 0.4.0: Removed acceptance test configuration and allowed hosts checks as they're not used.
