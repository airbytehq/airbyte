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

## Changelog

### 0.24.1
Update Python version requirement from 3.10 to 3.11.

## Validating Metadata Files

To be considered valid, a connector must have a metadata.yaml file which must conform to the [ConnectorMetadataDefinitionV0](./metadata_service/models/src/ConnectorMetadataDefinitionV0.yaml) schema, and a documentation file.

The paths to both files must be passed to the validate command.

```bash
poetry run metadata_service validate tests/fixtures/metadata_validate/valid/metadata_simple.yaml tests/fixtures/doc.md
```

## Useful Commands

### Replicate Production Data in your Development Bucket

This will replicate all the production data to your development bucket. This is useful for testing the metadata service with real up to date data.

_💡 Note: A prerequisite is you have [gsutil](https://cloud.google.com/storage/docs/gsutil) installed and have run `gsutil auth login`_

_⚠️ Warning: Its important to know that this will remove ANY files you have in your destination buckets as it calls `gsutil rsync` with `-d` enabled._

```bash
TARGET_BUCKET=<YOUR-DEV_BUCKET> poetry run poe replicate-prod
```

### Copy specific connector version to your Development Bucket

This will copy the specified connector version to your development bucket. This is useful for testing the metadata service with a specific version of a connector.

_💡 Note: A prerequisite is you have [gsutil](https://cloud.google.com/storage/docs/gsutil) installed and have run `gsutil auth login`_

```bash
TARGET_BUCKET=<YOUR-DEV_BUCKET> CONNECTOR="airbyte/source-stripe" VERSION="3.17.0-dev.ea013c8741" poetry run poe copy-connector-from-prod
```

### Promote Connector Version to Latest

This will promote the specified connector version to the latest version in the registry. This is useful for creating a mocked registry in which a prerelease connector is treated as if it was already published.

_💡 Note: A prerequisite is you have [gsutil](https://cloud.google.com/storage/docs/gsutil) installed and have run `gsutil auth login`_

_⚠️ Warning: Its important to know that this will remove ANY existing files in the latest folder that are not in the versioned folder as it calls `gsutil rsync` with `-d` enabled._

```bash
TARGET_BUCKET=<YOUR-DEV_BUCKET> CONNECTOR="airbyte/source-stripe" VERSION="3.17.0-dev.ea013c8741" poetry run poe promote-connector-to-latest
```
