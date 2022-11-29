# Step 6: Testing

We should make sure the connector respects the Airbyte specifications before we start using it in production.
This can be done by executing the Source Acceptance Tests (SAT).

These tests will assert the most basic functionalities work as expected and are configured in `acceptance-test-config.yml`.

Before running the tests, we'll create an invalid config to make sure the `check` operation fails if the credentials are wrong, and an abnormal state to verify the connector's behavior when running with an abnormal state.

Update `integration_tests/invalid_config.json` with this content

```json
{
  "access_key": "<invalid_key>",
  "start_date": "2022-07-21",
  "base": "USD"
}
```

and `integration_tests/abnormal_state.json` with

```json
{
  "rates": {
    "date": "2999-12-31"
  }
}
```

You can run the acceptance tests with the following commands:

```bash
docker build . -t airbyte/source-exchange-rates-tutorial:dev
python -m pytest integration_tests -p integration_tests.acceptance
```

## Next steps:

Next, we'll add the connector to the [Airbyte platform](https://docs.airbyte.com/connector-development/tutorials/cdk-tutorial-python-http/use-connector-in-airbyte).

## Read more:

- [Error handling](../understanding-the-yaml-file/error-handling.md)
- [Pagination](../understanding-the-yaml-file/pagination.md)
- [Testing connectors](../../testing-connectors/README.md)
- [Contribution guide](../../../contributing-to-airbyte/README.md)
- [Greenhouse source](https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors/source-greenhouse)
- [Sendgrid source](https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors/source-sendgrid)
- [Sentry source](https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors/source-sentry)