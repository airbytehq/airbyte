# Testing Connectors

## Our testing pyramid
Multiple tests suites compose the Airbyte connector testing pyramid:
Connector specific tests declared in the connector code directory:
* Unit tests
* Integration tests

Tests common to all connectors:
* [QA checks](https://github.com/airbytehq/airbyte/blob/master/tools/ci_connector_ops/ci_connector_ops/qa_checks.py#L1)
* [Connector Acceptance tests](https://docs.airbyte.com/connector-development/testing-connectors/connector-acceptance-tests-reference/)

## Running tests
Unit and integration tests can be run directly from the connector code.

Using `pytest` for Python connectors:
```bash
python -m pytest unit_tests/
python -m pytest integration_tests/
```

Using `gradle` for Java connectors:

```bash
./gradlew :airbyte-integrations:connectors:source-postgres:test
./gradlew :airbyte-integrations:connectors:source-postgres:integrationTestJava
```

Please note that according to the test implementation you might have to provide connector configurations as a `config.json` file in a `.secrets` folder in the connector code directory.


If you want to run the global test suite, exactly like what is run in CI, you should install [`airbyte-ci` CLI](https://github.com/airbytehq/airbyte/blob/master/tools/ci_connector_ops/ci_connector_ops/pipelines/README.md) and use the following command:

```bash
airbyte-ci connectors --name=<connector_name> test
```

This will run all the tests for the connector, including the QA checks and the Connector Acceptance tests.
Connector Acceptance tests require connector configuration to be provided as a `config.json` file in a `.secrets` folder in the connector code directory.


## Tests on pull requests
Our CI infrastructure runs the connector tests with [`airbyte-ci` CLI](https://github.com/airbytehq/airbyte/blob/master/tools/ci_connector_ops/ci_connector_ops/pipelines/README.md). Connectors tests are automatically and remotely triggered on your branch according to the changes made in your branch.
**Passing tests are required to merge a connector pull request.**