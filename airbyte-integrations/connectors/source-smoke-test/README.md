# Smoke Test source connector

This is the repository for the Smoke Test source connector, written in Python.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.com/integrations/sources/smoke-test).

## Overview

The Smoke Test source generates synthetic test data across 15 predefined scenarios designed to exercise common destination failure patterns:

- **Type coverage**: basic types, timestamps, large decimals, nested JSON/arrays
- **Null handling**: nullable columns across all types, always-null columns, null-vs-empty-vs-zero
- **Naming edge cases**: reserved SQL words, CamelCase, dots/dashes/spaces in column names, long column names, mixed-case stream names
- **Schema variations**: wide table (50 columns), no-primary-key stream, empty stream, single-record stream
- **Batch sizes**: configurable large batch (default 1000 records)
- **Unicode/special strings**: international characters, escape sequences

The source also supports dynamic scenario injection via the `custom_scenarios` config field.

## Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `all_fast_streams` | boolean | `true` | Include all fast (non-high-volume) predefined streams |
| `all_slow_streams` | boolean | `false` | Include all slow (high-volume) streams such as `large_batch_stream` |
| `scenario_filter` | array of strings | `[]` | Specific scenario names to include (unioned with boolean flags) |
| `large_batch_record_count` | integer | `1000` | Number of records for `large_batch_stream` |
| `custom_scenarios` | array of objects | `[]` | Additional test scenarios to inject at runtime |

## Local development

### Prerequisites

- Python (~=3.10)
- Poetry (~=1.7) - installation instructions [here](https://python-poetry.org/docs/#installation)

### Installing the connector

From this connector directory, run:

```bash
poetry install --with dev
```

### Locally running the connector

```
poetry run source-smoke-test spec
poetry run source-smoke-test check --config secrets/config.json
poetry run source-smoke-test discover --config secrets/config.json
poetry run source-smoke-test read --config secrets/config.json --catalog sample_files/configured_catalog.json
```

### Running unit tests

To run unit tests locally, from the connector directory run:

```
poetry run pytest unit_tests
```

### Building the docker image

1. Install [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md)
2. Run the following command to build the docker image:

```bash
airbyte-ci connectors --name=source-smoke-test build
```

An image will be available on your host with the tag `airbyte/source-smoke-test:dev`.
