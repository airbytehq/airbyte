# Airmeet Source

This is the repository for the Airmeet source connector, written in Python.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.com/integrations/sources/airmeet).

## Local development

### Prerequisites
- Python ~=3.11
- Poetry

### Installing the connector
From this connector directory, run:
```bash
poetry install
```

### Running the connector
```bash
poetry run source-airmeet spec
poetry run source-airmeet check --config secrets/config.json
poetry run source-airmeet discover --config secrets/config.json
poetry run source-airmeet read --config secrets/config.json --catalog configured_catalog.json
```

### Testing
```bash
poetry run pytest tests/
```