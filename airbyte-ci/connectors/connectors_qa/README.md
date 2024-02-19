# Connectors QA

This package has two main purposes:
* Running QA checks on connectors.
* Generating the QA checks documentation that are run on connectors.



## Usage

### Install

```bash
pipx install .
```

This will make `connectors-qa` available in your `PATH`.


Feel free to run `connectors-qa --help` to see the available commands and options.


### Examples

#### Running QA checks on one or more connectors:

```bash
# This command must run from the root of the Airbyte repo
connectors-qa run --name=source-faker --name=source-google-sheets
```
#### Running QA checks on all connectors:

```bash
# This command must run from the root of the Airbyte repo
connectors-qa run --connector-directory=airbyte-integrations/connectors
```

#### Running QA checks on all connectors and generating a JSON report:

```bash
### Generating documentation for QA checks:
connectors-qa run --connector-directory=airbyte-integrations/connectors --report-path=qa_report.json
```

#### Running only specific QA checks on one or more connectors:

```bash
connectors-qa run --name=source-faker --name=source-google-sheets --check=CheckConnectorIconIsAvailable --check=CheckConnectorUsesPythonBaseImage
```

#### Running only specific QA checks on all connectors:

```bash
connectors-qa run --connector-directory=airbyte-integrations/connectors --check=CheckConnectorIconIsAvailable --check=CheckConnectorUsesPythonBaseImage
```

#### Generating documentation for QA checks:

```bash
connectors-qa generate-documentation qa_checks.md
```

## Development

```bash
poetry install
```

### Dependencies
This package uses two local dependencies:
* [`connector_ops`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/connector_ops): To interact with the `Connector` object.
* [`metadata_service/lib`]((https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/metadata_service/lib)): To validate the metadata of the connectors.

### Adding a new QA check

To add a new QA check, you have to create add new class in one of the `checks` module. This class must inherit from `models.Check` and implement the `_run` method. Then, you need to add an instance of this class to the `ENABLED_CHECKS` list of the module.

**Please run the `generate-documentation` command to update the documentation with the new check and commit it in your PR.**:
```bash
# From airbyte repo root
connectors-qa generate-documentation docs/contributing-to-airbyte/resources/qa-checks.md
```

### Running tests

```bash
poe test
```

### Running type checks

```bash
poe type_check
```

### Running the linter

```bash
poe lint
```

## Changelog

### 1.0.1
* Add `applies_to_connector_types` attribute to `Check` class to specify the connector types that the check applies to.
* Make `CheckPublishToPyPiIsEnabled` run on source connectors only.

### 1.0.0
Initial release of `connectors-qa` package.