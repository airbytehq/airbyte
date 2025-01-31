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

Connector OPS package provides useful `Connector` class and helper methods. It's used in several Airbyte CI packages.

## Contributing to `connector_ops`

### Running tests

To run tests locally:

```bash
poetry run pytest
```

## Changelog
- 0.10.2: Update Python version requirement from 3.10 to 3.11.
- 0.10.1: Update to `ci_credentials` 1.2.0, which drops `common_utils`.
- 0.10.0: Add `documentation_file_name` property to `Connector` class.
- 0.9.0: Add components path attribute for manifest-only connectors.
- 0.8.1: Gradle dependency discovery logic supports the Bulk CDK.
- 0.8.0: Add a `sbom_url` property to `Connector`
- 0.7.0: Added required reviewers for manifest-only connector changes/additions.
- 0.6.1: Simplified gradle dependency discovery logic.
- 0.6.0: Added manifest-only build.
- 0.5.0: Added `cloud_usage` property to `Connector` class.
- 0.4.0: Removed acceptance test configuration and allowed hosts checks as they're not used.
