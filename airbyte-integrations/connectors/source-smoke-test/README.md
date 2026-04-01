# Source Smoke Test

Smoke test source for destination regression testing. Generates synthetic data
across predefined scenarios that cover common destination failure patterns:
type variations, null handling, naming edge cases, schema variations, and
batch size variations.

This connector is a thin wrapper around
[PyAirbyte's smoke test source](https://github.com/airbytehq/PyAirbyte).
All business logic lives in the `airbyte.cli.smoke_test_source` module of PyAirbyte.

## Local Development

### Prerequisites

- Python 3.10+
- Poetry

### Install Dependencies

```bash
cd airbyte-integrations/connectors/source-smoke-test
poetry install
```

### Run the Connector

```bash
# Print the spec
poetry run source-smoke-test spec

# Check the connection
poetry run source-smoke-test check --config secrets/config.json

# Discover the catalog
poetry run source-smoke-test discover --config secrets/config.json
```

For general connector development guidance, see the
[Connector Development Guide](https://docs.airbyte.com/connector-development/).
