# Testing Connectors

Multiple tests suites compose the Airbyte connector testing pyramid

## Common to all connectors

- [Connectors QA checks](https://docs.airbyte.com/contributing-to-airbyte/resources/qa-checks)
- [Connector Acceptance tests](https://docs.airbyte.com/connector-development/testing-connectors/connector-acceptance-tests-reference/)

## Connector specific tests

### 🐍 Python connectors

We use `pytest` to run unit and integration tests:

```bash
# From connector directory
poetry run pytest
```

### ☕ Java connectors

We run Java connector tests with gradle.

```bash
# Unit tests
./gradlew :airbyte-integrations:connectors:source-postgres:test
# Integration tests
./gradlew :airbyte-integrations:connectors:source-postgres:integrationTestJava
```

Please note that according to the test implementation you might have to provide connector configurations as a `config.json` file in a `.secrets` folder in the connector code directory.

## 🤖 CI

If you want to run the global test suite, exactly like what is run in CI, you should install [`airbyte-ci` CLI](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md) and use the following command:

```bash
airbyte-ci connectors --name=<connector_name> test
```

This will run all the tests for the connector, including the QA checks and the Connector Acceptance tests.
Connector Acceptance tests require connector configuration to be provided as a `config.json` file in a `.secrets` folder in the connector code directory.

Our CI infrastructure runs the connector tests with [`airbyte-ci` CLI](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md). Connectors tests are automatically and remotely triggered on your branch according to the changes made in your branch.
**Passing tests are required to merge a connector pull request.**
