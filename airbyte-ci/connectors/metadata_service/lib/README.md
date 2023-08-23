# Connector Metadata Service Library

This submodule is responsible for managing all the logic related to validating, uploading, and managing connector metadata.

## Installation

To use this submodule, it is recommended that you use Poetry to manage dependencies.

```
poetry install
```


## Generating Models

This submodule includes a tool for generating Python models from JSON Schema specifications. To generate the models, we use the library [datamodel-code-generator](https://github.com/koxudaxi/datamodel-code-generator). The generated models are stored in `models/generated`.

To generate the models, run the following command:

```bash
poetry run poe generate-models

```

This will read the JSON Schema specifications in `models/src` and generate Python models in `models/generated`.


## Running Tests
```bash
poetry run pytest
```

## Validating Metadata Files
```bash
poetry run metadata_service validate tests/fixtures/valid/metadata_registry_override.yaml
```

## Useful Commands

### Replicate Production Data in your Development Bucket
This will replicate all the production data to your development bucket. This is useful for testing the metadata service with real up to date data.
```bash
TARGET_BUCKET=<YOUR-DEV_BUCKET> poetry poe replicate-prod
```

### Promote Connector Version to Latest
This will promote the specified connector version to the latest version in the registry. This is useful for testing a connector prerelease version in your development bucket before promoting it to the latest version in the registry.
```bash
TARGET_BUCKET=<YOUR-DEV_BUCKET> CONNECTOR="airbyte/source-stripe" VERSION="3.17.0-dev.ea013c8741" poetry poe promote-connector-to-latest
```
