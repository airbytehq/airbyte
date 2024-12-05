# Environment setup

Let's first start by cloning the repository, optionally forking it first

```bash
git clone git@github.com:airbytehq/airbyte.git
cd airbyte
```

Use the Airbyte provided code generator which bootstraps the scaffolding for our connector:

```bash
cd airbyte-integrations/connector-templates/generator
./generate.sh
```

Select Python CDK Source Set name to `survey-monkey-demo`

Next change your working directory to the new connector module. Also change airbyte-cdk version
to the one used for this tutorial in `pyproject.toml`:

```bash
cd ../../connectors/source-survey-monkey-demo
```

Then create an initial python environment and install the dependencies required to run an API Source connector:

```bash
poetry lock
poetry install --with dev
```

Let's verify the unit tests pass

```bash
poetry run pytest unit_tests
```

And the check operation fails as expected

```bash
poetry run source-survey-monkey-demo check --config secrets/config.json
```

It should return a failed connection status

```json
{
  "type": "CONNECTION_STATUS",
  "connectionStatus": {
    "status": "FAILED",
    "message": "Config validation error: 'TODO' is a required property"
  }
}
```

The discover operation should also fail as expected

```bash
poetry run source-survey-monkey-demo discover --config secrets/config.json
```

It should fail because `TODO' is a required property`

The read operation should also fail as expected

```bash
poetry run source-survey-monkey-demo read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

It should fail because `TODO' is a required property`

We're ready to start development. In the [next section](./2-reading-a-page.md), we'll read a page of
records from the surveys endpoint.
