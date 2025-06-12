# Connectors QA

This package has two main purposes:

- Running assets and metadata verification checks on connectors.
- Generating the QA checks documentation that are run on connectors.

## Usage

### Install

Connectors QA is an internal Airbyte package that is not published to PyPI. To install it, run the
following command from this directory:

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
poetry install --with dev
```

### Dependencies

This package uses two local dependencies:

- [`connector_ops`](../connector_ops): To interact with the `Connector` object.
- [`metadata_service/lib`](../metadata_service/lib): To validate the metadata of the connectors.

### Adding a new QA check

To add a new QA check, you have to create add new class in one of the `checks` module. This class
must inherit from `models.Check` and implement the `_run` method. Then, you need to add an instance
of this class to the `ENABLED_CHECKS` list of the module.

**Please run the `generate-documentation` command to update the documentation with the new check and
commit it in your PR.**:

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

### 1.10.2
Update Python version requirement from 3.10 to 3.11.

### 1.10.0
Do not enforce that PyPi publication is enabled for Python connectors.
Enforce that it's declared in the metadata file.
It can be set to true or false. 

### 1.9.1

Fail assets icon check if the icon is the default Airbyte icon.

### 1.8.0

Added minimum sl threshold value to documentation checks to skip them for connectors for which sl is 0.

### 1.7.0

Added  `CheckDocumentationLinks`, `CheckDocumentationHeadersOrder`, `CheckPrerequisitesSectionDescribesRequiredFieldsFromSpec`,
`CheckSourceSectionContent`, `CheckForAirbyteCloudSectionContent`, `CheckForAirbyteOpenSectionContent`, `CheckSupportedSyncModesSectionContent`,
`CheckTutorialsSectionContent`, `CheckChangelogSectionContent` checks that verifies that documentation file follow standard template.

### 1.6.0

Added `manifest-only` connectors support — they will run basic assets and metadata checks.

### 1.5.1

Bumped dependencies.

### 1.5.0

Added `AIRBYTE ENTERPRISE` to the list of allowed licenses, for use by Airbyte Enterprise connectors.

### 1.4.0

Added the `IntegrationTestsEnabledCheck` check that verifies if the integration tests are enabled for connectors with higher cloud usage.

### 1.3.2

Removed documentation checks in `MedatadaCheck` since it's already verified in `DocumentationCheck`.

### 1.3.1

Remove requirements on DockerHub credentials to run metadata validation.

### 1.3.0

Added `CheckConnectorMaxSecondsBetweenMessagesValue` check that verifies presence of
`maxSecondsBetweenMessages` value in `metadata.yaml` file for all source certified connectors.

### 1.2.0

Added `ValidateBreakingChangesDeadlines` check that verifies the minimal compliance of breaking
change rollout deadline.

### 1.1.0

Introduced the `Check.run_on_released_connectors` flag.

### 1.0.4

Adds `htmlcov` to list of ignored directories for `CheckConnectorUsesHTTPSOnly` check.

### 1.0.3

Disable `CheckDocumentationStructure` for now.

### 1.0.2

Fix access to connector types: it should be accessed from the `Connector.connector_type` attribute.

### 1.0.1

- Add `applies_to_connector_types` attribute to `Check` class to specify the connector types that
  the check applies to.
- Make `CheckPublishToPyPiIsDeclared` run on source connectors only.

### 1.0.0

Initial release of `connectors-qa` package.
