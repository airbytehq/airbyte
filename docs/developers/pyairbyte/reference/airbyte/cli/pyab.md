---
id: airbyte-cli-pyab
title: "airbyte.cli.pyab Module"
sidebar_label: "airbyte.cli.pyab"
---

# `airbyte.cli.pyab` Module

CLI for PyAirbyte.

The PyAirbyte CLI provides a command-line interface for testing connectors and running benchmarks.

After installing PyAirbyte, the CLI can be invoked with the `pyairbyte` CLI executable, or the
shorter `pyab` alias.

These are equivalent:

```bash
pyairbyte --help
pyab --help
```

You can also use `pipx` or the fast and powerful `uv` tool to run the PyAirbyte CLI
without pre-installing:

```bash
# Install `uv` if you haven't already:
brew install uv

# Run the PyAirbyte CLI using `uvx`:
uvx --from=airbyte pyab --help
```

Example `benchmark` Usage:

```bash
# PyAirbyte System Benchmark (no-op):
pyab benchmark --num-records=2.4e6

# Source Benchmark:
pyab benchmark --source=source-hardcoded-records --config='{count: 400000}'
pyab benchmark --source=source-hardcoded-records --config='{count: 400000}' --streams='*'
pyab benchmark --source=source-hardcoded-records --config='{count: 4000}' --streams=dummy_fields

# Source Benchmark from Docker Image:
pyab benchmark --source=airbyte/source-hardcoded-records:latest --config='{count: 400_000}'
pyab benchmark --source=airbyte/source-hardcoded-records:dev --config='{count: 400_000}'

# Destination Benchmark:
pyab benchmark --destination=destination-dev-null --config=/path/to/config.json

# Benchmark a Local Python Source (source-s3):
pyab benchmark --source=$(poetry run which source-s3) --config=./secrets/config.json
# Equivalent to:
LOCAL_EXECUTABLE=$(poetry run which source-s3)
CONFIG_PATH=$(realpath ./secrets/config.json)
pyab benchmark --source=$LOCAL_EXECUTABLE --config=$CONFIG_PATH
```

Example `validate` Usage:

```bash
pyab validate --connector=source-hardcoded-records
pyab validate --connector=source-hardcoded-records --config='{count: 400_000}'
```

----------------------

PyAirbyte CLI Guidance

Providing connector configuration:

When providing configuration via `--config`, you can providing any of the following:

1. A path to a configuration file, in yaml or json format.

2. An inline yaml string, e.g. `--config='{key: value}'`, --config='\{key: \{nested: value\}\}'.

When providing an inline yaml string, it is recommended to use single quotes to avoid shell
interpolation.

Providing secrets:

You can provide secrets in your configuration file by prefixing the secret value with `SECRET:`.
For example, --config='\{password: "SECRET:my_password"'\} will look for a secret named `my_password`
in the secret store. By default, PyAirbyte will look for secrets in environment variables and
dotenv (.env) files. If a secret is not found, you'll be prompted to provide the secret value
interactively in the terminal.

It is highly recommended to use secrets when using inline yaml strings, in order to avoid
exposing secrets in plain text in the terminal history. Secrets provided interactively will
not be echoed to the terminal.

### `benchmark` {#airbyte.cli.pyab.benchmark}

<ApiMember kind="function">

<ApiSignature>

```python
def benchmark(
    *,
    source: Annotated[str | None, Parameter(help="The source name, with an optional version declaration. If the name contains a colon (\':\'), it will be interpreted as a docker image and tag. ")] = None,
    streams: Annotated[str, Parameter(help="A comma-separated list of stream names to select for reading. If set to \'*\', all streams will be selected. Defaults to \'*\'.")] = '*',
    num_records: "Annotated[str, Parameter(help='The number of records to generate for the benchmark. Ignored if a source is provided. You can specify the number of records to generate using scientific notation. For example, `5e6` will generate 5 million records. By default, 500,000 records will be generated (`5e5` records). If underscores are provided within a numeric string, they will be ignored.')]" = '5e5',
    destination: "Annotated[str | None, Parameter(help='The destination name, with an optional version declaration. If a path is provided, it will be interpreted as a path to the local executable. ')]" = None,
    config: Annotated[str | None, Parameter(help=CONFIG_HELP)] = None,
    use_python: Annotated[str | None, Parameter(help=USE_PYTHON_HELP)] = None,
) -> None
```

</ApiSignature>

CLI command to run a `benchmark` operation.

You can provide either a source or a destination, but not both. If a destination is being
benchmarked, you can use `--num-records` to specify the number of records to generate for the
benchmark.

If a source is being benchmarked, you can provide a configuration file or a job
definition file to run the source job.

</ApiMember>

### `destination_smoke_test` {#airbyte.cli.pyab.destination_smoke_test}

<ApiMember kind="function">

<ApiSignature>

```python
def destination_smoke_test(
    *,
    destination: Annotated[str, Parameter(help="The destination connector to test. Can be a connector name (e.g. \'destination-snowflake\'), a Docker image with tag (e.g. \'airbyte/destination-snowflake:3.14.0\'), or a path to a local executable.")],
    config: "Annotated[str | None, Parameter(help='The destination configuration. ' + CONFIG_HELP)]" = None,
    pip_url: "Annotated[str | None, Parameter(help='Optional pip URL for the destination (Python connectors only). ' + PIP_URL_HELP)]" = None,
    use_python: Annotated[str | None, Parameter(help=USE_PYTHON_HELP)] = None,
    scenarios: Annotated[str, Parameter(help="Which smoke test scenarios to run. Use \'fast\' (default) for all fast predefined scenarios (excludes large_batch_stream), \'all\' for every predefined scenario including large batch, or provide a comma-separated list of scenario names. Available scenarios: basic_types, timestamp_types, large_decimals_and_numbers, nested_json_objects, null_handling, column_naming_edge_cases, table_naming_edge_cases, CamelCaseStreamName, wide_table_50_columns, empty_stream, single_record_stream, unicode_and_special_strings, schema_with_no_primary_key, long_column_names, large_batch_stream.")] = 'fast',
    custom_scenarios: Annotated[str | None, Parameter(help="Path to a JSON or YAML file containing additional custom test scenarios. Each scenario should define \'name\', \'json_schema\', and optionally \'records\' and \'primary_key\'. These are unioned with the predefined scenarios.")] = None,
    namespace_suffix: Annotated[str | None, Parameter(help="Optional suffix appended to the auto-generated namespace. Defaults to \'smoke_test\' (format: \'zz_deleteme_yyyymmdd_hhmm_{suffix}\'). Use this to distinguish concurrent runs.")] = None,
    reuse_namespace: "Annotated[str | None, Parameter(help='Exact namespace to reuse from a previous run. When set, no new namespace is generated. Useful for running a second test against an already-populated namespace.')]" = None,
    skip_preflight: "Annotated[bool, Parameter(help='Skip the automatic preflight check that runs basic_types before the requested scenarios. Use when you expect basic_types itself to fail or want to save time on repeated runs.', negative=[])]" = False,
) -> None
```

</ApiSignature>

Run smoke tests against a destination connector.

Sends synthetic test data from the smoke test source to the specified
destination and reports success or failure. The smoke test source
generates data across predefined scenarios covering common destination
failure patterns: type variations, null handling, naming edge cases,
schema variations, and batch sizes.

When the destination has a compatible cache implementation (DuckDB,
Postgres, Snowflake, BigQuery, MotherDuck), readback introspection
is automatically performed after a successful write. The readback
produces stats on the written data: table row counts, column
names/types, and per-column null/non-null counts.

Usage examples:

`pyab destination-smoke-test --destination=destination-dev-null`

`pyab destination-smoke-test --destination=destination-snowflake
--config=./secrets/snowflake.json`

`pyab destination-smoke-test --destination=destination-motherduck
--scenarios=basic_types,null_handling`

`pyab destination-smoke-test --destination=destination-snowflake
--config=./secrets/snowflake.json --scenarios=all`

`pyab destination-smoke-test --destination=destination-snowflake
--config=./secrets/snowflake.json --namespace-suffix=run2`

`pyab destination-smoke-test --destination=destination-snowflake
--config=./secrets/snowflake.json
--reuse-namespace=zz_deleteme_20260318_2256`

</ApiMember>

### `sync` {#airbyte.cli.pyab.sync}

<ApiMember kind="function">

<ApiSignature>

```python
def sync(
    *,
    source: Annotated[str, Parameter(help="The source name, with an optional version declaration. If the name contains a colon (\':\'), it will be interpreted as a docker image and tag. ")],
    destination: "Annotated[str, Parameter(help='The destination name, with an optional version declaration. If a path is provided, it will be interpreted as a path to the local executable. ')]",
    streams: Annotated[str | None, Parameter(help="A comma-separated list of stream names to select for reading. If set to \'*\', all streams will be selected. Defaults to \'*\'.")] = None,
    source_config: "Annotated[str | None, Parameter(name='--Sconfig', help='The source config. ' + CONFIG_HELP)]" = None,
    destination_config: "Annotated[str | None, Parameter(name='--Dconfig', help='The destination config. ' + CONFIG_HELP)]" = None,
    source_pip_url: "Annotated[str | None, Parameter(name='--Spip-url', help='Optional pip URL for the source (Python connectors only). ' + PIP_URL_HELP)]" = None,
    destination_pip_url: "Annotated[str | None, Parameter(name='--Dpip-url', help='Optional pip URL for the destination (Python connectors only). ' + PIP_URL_HELP)]" = None,
    use_python: Annotated[str | None, Parameter(help=USE_PYTHON_HELP)] = None,
) -> None
```

</ApiSignature>

CLI command to run a `sync` operation.

Currently, this only supports full refresh syncs. Incremental syncs are not yet supported.
Custom catalog syncs are not yet supported.

</ApiMember>

### `validate` {#airbyte.cli.pyab.validate}

<ApiMember kind="function">

<ApiSignature>

```python
def validate(
    *,
    connector: "Annotated[str | None, Parameter(help='The connector name or a path to the local executable.')]" = None,
    pip_url: "Annotated[str | None, Parameter(help='Optional. The location from which to install the connector. This can be anything pip accepts, including: a PyPI package name, a local path, a git repository, a git branch ref, etc.')]" = None,
    config: Annotated[str | None, Parameter(help=CONFIG_HELP)] = None,
    use_python: Annotated[str | None, Parameter(help=USE_PYTHON_HELP)] = None,
) -> None
```

</ApiSignature>

Validate the connector has a valid CLI and is able to run `spec`.

    If 'config' is provided, we will also run a `check` on the connector
    with the provided config.

----------------------

PyAirbyte CLI Guidance

Providing connector configuration:

When providing configuration via `--config`, you can providing any of the following:

1. A path to a configuration file, in yaml or json format.

2. An inline yaml string, e.g. `--config='{key: value}'`, --config='\{key: \{nested: value\}\}'.

When providing an inline yaml string, it is recommended to use single quotes to avoid shell
interpolation.

Providing secrets:

You can provide secrets in your configuration file by prefixing the secret value with `SECRET:`.
For example, --config='\{password: "SECRET:my_password"'\} will look for a secret named `my_password`
in the secret store. By default, PyAirbyte will look for secrets in environment variables and
dotenv (.env) files. If a secret is not found, you'll be prompted to provide the secret value
interactively in the terminal.

It is highly recommended to use secrets when using inline yaml strings, in order to avoid
exposing secrets in plain text in the terminal history. Secrets provided interactively will
not be echoed to the terminal.

</ApiMember>