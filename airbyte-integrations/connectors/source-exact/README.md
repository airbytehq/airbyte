# Exact Source

## Local development

### Prerequisites

**To iterate on this connector, make sure to complete this prerequisites section.**

#### Minimum Python version required `= 3.11.0`

### Locally running the connector

```
poetry run source-exact spec
poetry run source-exact check --config secrets/config.json
poetry run source-exact discover --config secrets/config.json
poetry run source-exact read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

### Optional flags

```
--debug
```