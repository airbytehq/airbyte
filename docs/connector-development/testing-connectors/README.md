# Testing Connectors

Multiple tests suites compose the Airbyte connector testing pyramid

## Tests run by our CI pipeline

- [Connector QA Checks](https://docs.airbyte.com/contributing-to-airbyte/resources/qa-checks): Static asset checks that validate that a connector is correctly packaged to be successfully released to production.
- Unit Tests: Connector-specific tests written by the connector developer which don’t require access to the source/destination.
- Integration Tests: Connector-specific tests written by the connector developer which _may_ require access to the source/destination.
- [Connector Acceptance Tests](https://docs.airbyte.com/connector-development/testing-connectors/connector-acceptance-tests-reference/): Connector-agnostic tests that verify that a connector adheres to the [Airbyte protocol](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol). Credentials to a source/destination sandbox account are **required**.
- [Regression Tests](https://github.com/airbytehq/airbyte/tree/master/airbyte-ci/connectors/live-tests): Connector-agnostic tests that verify that the behavior of a connector hasn’t changed unexpectedly between connector versions. A sandbox cloud connection is required. Currently only available for API source connectors.


## 🤖 CI

If you want to run the global test suite, exactly like what is run in CI, you should install [`airbyte-ci` CLI](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md) and use the following command:

```bash
airbyte-ci connectors --name=<connector_name> test
```

CI will run all the tests that are available for a connector. This can include all of the tests listed above, if we have the appropriate credentials. At a minimum, it will include the Connector QA checks and any tests that exist in a connector's `unit_tests` and `integration_tests` directories.
To run Connector Acceptance tests locally, you must provide connector configuration as a `config.json` file in a `.secrets` folder in the connector code directory.
Regression tests may only be run locally with authorization to our cloud resources.

Our CI infrastructure runs the connector tests with [`airbyte-ci` CLI](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md). Connectors tests are automatically and remotely triggered on your branch according to the changes made in your branch.
**Passing tests are required to merge a connector pull request.**

## Connector specific tests

### 🐍 Python connectors

We use `pytest` to run unit and integration tests:

```bash
# From connector directory
poetry run pytest
```

### ☕ Java connectors

:::warning
Airbyte is undergoing a major revamp of the shared core Java destinations codebase, with plans to release a new CDK in 2024.
We are actively working on improving usability, speed (through asynchronous loading), and implementing [Typing and Deduplication](/using-airbyte/core-concepts/typing-deduping) (Destinations V2).
For this reason, Airbyte is not reviewing/accepting new Java connectors for now.
:::

We run Java connector tests with gradle.

```bash
# Unit tests
./gradlew :airbyte-integrations:connectors:source-postgres:test
# Integration tests
./gradlew :airbyte-integrations:connectors:source-postgres:integrationTestJava
```

Please note that according to the test implementation you might have to provide connector configurations as a `config.json` file in a `.secrets` folder in the connector code directory.

