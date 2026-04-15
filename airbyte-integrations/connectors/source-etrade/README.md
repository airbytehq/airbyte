# E*TRADE Source

This is the repository for the E*TRADE source connector, written in Python.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.com/integrations/sources/etrade).

## Local development

### Prerequisites

- Python 3.9+
- Poetry

### Installing dependencies

```bash
poetry install
```

### Running unit tests

```bash
poetry run pytest unit_tests/ -x
```

### Running the connector

```bash
poetry run source-etrade spec
poetry run source-etrade check --config secrets/config.json
poetry run source-etrade discover --config secrets/config.json
poetry run source-etrade read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

## Authentication

This connector uses OAuth 1.0a authentication. You need:

1. **Consumer Key** and **Consumer Secret** from the [E*TRADE Developer Portal](https://developer.etrade.com)
2. **OAuth Token** and **OAuth Token Secret** obtained through the E*TRADE OAuth authorization flow

Note: E*TRADE access tokens expire at midnight US Eastern time daily and must be renewed.
