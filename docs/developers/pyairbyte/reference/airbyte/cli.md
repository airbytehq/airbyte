---
sidebar_label: cli
title: airbyte.cli
---

CLI for PyAirbyte.

The PyAirbyte CLI provides a command-line interface for testing connectors and running benchmarks.

After installing PyAirbyte, the CLI can be invoked with the `pyairbyte` CLI executable, or the
shorter `pyab` alias.

These are equivalent:

```bash
python -m airbyte.cli --help
pyairbyte --help
pyab --help
```

You can also use `pipx` or the fast and powerful `uv` tool to run the PyAirbyte CLI
without pre-installing:

```bash
# Install `uv` if you haven&#x27;t already:
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

## annotations

## re

## sys

## Path

## TYPE\_CHECKING

## Any

## click

## yaml

## get\_destination

## get\_noop\_destination

## PyAirbyteInputError

## get\_secret

## get\_benchmark\_source

## get\_source

#### CLI\_GUIDANCE

#### CONFIG\_HELP

#### PIP\_URL\_HELP

#### \_resolve\_config

```python
def _resolve_config(config: str) -> dict[str, Any]
```

Resolve the configuration file into a dictionary.

#### \_is\_docker\_image

```python
def _is_docker_image(image: str | None) -> bool
```

Check if the source or destination is a docker image.

#### \_is\_executable\_path

```python
def _is_executable_path(connector_str: str) -> bool
```

#### \_get\_connector\_name

```python
def _get_connector_name(connector: str) -> str
```

#### \_parse\_use\_python

```python
def _parse_use_python(use_python_str: str | None) -> bool | Path | str | None
```

Parse the use_python CLI parameter.

**Arguments**:

- `use_python_str` - The raw string value from CLI input.
  

**Returns**:

  - None: No parameter provided
  - True: Use current Python interpreter (&quot;true&quot;)
  - False: Use Docker instead (&quot;false&quot;)
  - Path: Use interpreter at this path (paths containing / or \ or starting with .)
  - str: Use uv-managed Python version (semver patterns like &quot;3.12&quot;, &quot;3.11.5&quot;)
  or existing interpreter name (non-semver strings like &quot;python3.10&quot;)

#### \_resolve\_source\_job

```python
def _resolve_source_job(*,
                        source: str | None = None,
                        config: str | None = None,
                        streams: str | None = None,
                        pip_url: str | None = None,
                        use_python: str | None = None) -> Source
```

Resolve the source job into a configured Source object.

**Arguments**:

- `source` - The source name or source reference.
  If a path is provided, the source will be loaded from the local path.
  If the source contains a colon (&#x27;:&#x27;), it will be interpreted as a docker image and tag.
- `config` - The path to a configuration file for the named source or destination.
- `streams` - A comma-separated list of stream names to select for reading. If set to &quot;*&quot;,
  all streams will be selected. If not provided, all streams will be selected.
- `pip_url` - Optional. A location from which to install the connector.
- `use_python` - Optional. Python interpreter specification.

#### \_get\_noop\_destination\_config

```python
def _get_noop_destination_config() -> dict[str, Any]
```

#### \_resolve\_destination\_job

```python
def _resolve_destination_job(*,
                             destination: str,
                             config: str | None = None,
                             pip_url: str | None = None,
                             use_python: str | None = None) -> Destination
```

Resolve the destination job into a configured Destination object.

**Arguments**:

- `destination` - The destination name or source reference.
  If a path is provided, the source will be loaded from the local path.
  If the destination contains a colon (&#x27;:&#x27;), it will be interpreted as a docker image
  and tag.
- `config` - The path to a configuration file for the named source or destination.
- `pip_url` - Optional. A location from which to install the connector.
- `use_python` - Optional. Python interpreter specification.

#### validate

```python
@click.command(help=(
    "Validate the connector has a valid CLI and is able to run `spec`. "
    "If 'config' is provided, we will also run a `check` on the connector "
    "with the provided config.\n\n" + CLI_GUIDANCE), )
@click.option(
    "--connector",
    type=str,
    help="The connector name or a path to the local executable.",
)
@click.option(
    "--pip-url",
    type=str,
    help=
    ("Optional. The location from which to install the connector. "
     "This can be a anything pip accepts, including: a PyPI package name, a local path, "
     "a git repository, a git branch ref, etc."),
)
@click.option(
    "--config",
    type=str,
    required=False,
    help=CONFIG_HELP,
)
@click.option(
    "--use-python",
    type=str,
    help=("Python interpreter specification. Use 'true' for current Python, "
          "'false' for Docker, a path for specific interpreter, or a version "
          "string for uv-managed Python (e.g., '3.11', 'python3.12')."),
)
def validate(connector: str | None = None,
             config: str | None = None,
             pip_url: str | None = None,
             use_python: str | None = None) -> None
```

CLI command to run a `benchmark` operation.

#### benchmark

```python
@click.command()
@click.option(
    "--source",
    type=str,
    help=
    ("The source name, with an optional version declaration. "
     "If the name contains a colon (':'), it will be interpreted as a docker image and tag. "
     ),
)
@click.option(
    "--streams",
    type=str,
    default="*",
    help=
    ("A comma-separated list of stream names to select for reading. If set to '*', all streams "
     "will be selected. Defaults to '*'."),
)
@click.option(
    "--num-records",
    type=str,
    default="5e5",
    help=
    ("The number of records to generate for the benchmark. Ignored if a source is provided. "
     "You can specify the number of records to generate using scientific notation. "
     "For example, `5e6` will generate 5 million records. By default, 500,000 records will "
     "be generated (`5e5` records). If underscores are providing within a numeric a string, "
     "they will be ignored."),
)
@click.option(
    "--destination",
    type=str,
    help=
    ("The destination name, with an optional version declaration. "
     "If a path is provided, it will be interpreted as a path to the local executable. "
     ),
)
@click.option(
    "--config",
    type=str,
    help=CONFIG_HELP,
)
@click.option(
    "--use-python",
    type=str,
    help=("Python interpreter specification. Use 'true' for current Python, "
          "'false' for Docker, a path for specific interpreter, or a version "
          "string for uv-managed Python (e.g., '3.11', 'python3.12')."),
)
def benchmark(source: str | None = None,
              streams: str = "*",
              num_records: int | str = "5e5",
              destination: str | None = None,
              config: str | None = None,
              use_python: str | None = None) -> None
```

CLI command to run a `benchmark` operation.

You can provide either a source or a destination, but not both. If a destination is being
benchmarked, you can use `--num-records` to specify the number of records to generate for the
benchmark.

If a source is being benchmarked, you can provide a configuration file or a job
definition file to run the source job.

#### sync

```python
@click.command()
@click.option(
    "--source",
    type=str,
    help=
    ("The source name, with an optional version declaration. "
     "If the name contains a colon (':'), it will be interpreted as a docker image and tag. "
     ),
)
@click.option(
    "--destination",
    type=str,
    help=
    ("The destination name, with an optional version declaration. "
     "If a path is provided, it will be interpreted as a path to the local executable. "
     ),
)
@click.option(
    "--streams",
    type=str,
    help=
    ("A comma-separated list of stream names to select for reading. If set to '*', all streams "
     "will be selected. Defaults to '*'."),
)
@click.option(
    "--Sconfig",
    "source_config",
    type=str,
    help="The source config. " + CONFIG_HELP,
)
@click.option(
    "--Dconfig",
    "destination_config",
    type=str,
    help="The destination config. " + CONFIG_HELP,
)
@click.option(
    "--Spip-url",
    "source_pip_url",
    type=str,
    help="Optional pip URL for the source (Python connectors only). " +
    PIP_URL_HELP,
)
@click.option(
    "--Dpip-url",
    "destination_pip_url",
    type=str,
    help="Optional pip URL for the destination (Python connectors only). " +
    PIP_URL_HELP,
)
@click.option(
    "--use-python",
    type=str,
    help=("Python interpreter specification. Use 'true' for current Python, "
          "'false' for Docker, a path for specific interpreter, or a version "
          "string for uv-managed Python (e.g., '3.11', 'python3.12')."),
)
def sync(*,
         source: str,
         source_config: str | None = None,
         source_pip_url: str | None = None,
         destination: str,
         destination_config: str | None = None,
         destination_pip_url: str | None = None,
         streams: str | None = None,
         use_python: str | None = None) -> None
```

CLI command to run a `sync` operation.

Currently, this only supports full refresh syncs. Incremental syncs are not yet supported.
Custom catalog syncs are not yet supported.

#### cli

```python
@click.group()
def cli() -> None
```

@private PyAirbyte CLI.

