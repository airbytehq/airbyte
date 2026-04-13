---
id: airbyte-cli
title: airbyte.cli
---

Module airbyte.cli
==================
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