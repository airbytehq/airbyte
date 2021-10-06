# Step 8: Test Connector

## Unit Tests

Add any relevant unit tests to the `unit_tests` directory. Unit tests should **not** depend on any secrets.

You can run the tests using `python -m pytest -s unit_tests`

## Integration Tests

Place any integration tests in the `integration_tests` directory such that they can be [discovered by pytest](https://docs.pytest.org/en/6.2.x/goodpractices.html#conventions-for-python-test-discovery).

## Standard Tests

Standard tests are a fixed set of tests Airbyte provides that every Airbyte source connector must pass. While they're only required if you intend to submit your connector to Airbyte, you might find them helpful in any case. See [Testing your connectors](https://docs.airbyte.io/connector-development/testing-connectors)

If you want to submit this connector to become a default connector within Airbyte, follow steps 8 onwards from the [Python source checklist](https://docs.airbyte.io/connector-development/tutorials/building-a-python-source#step-8-set-up-standard-tests)
