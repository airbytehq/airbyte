# Exact Source

This is the repository for the Exact source connector, written in Python.

## Local development

### Prerequisites

- Python `~= 3.11.0`
- Poetry `~= 1.8` - installation instructions [here](https://python-poetry.org/docs/#installation)

Note: it is quite difficult to work with Poetry 1.8 at the moment because tools like Homebrew update Poetry to 2.0 
which have some differences. Create a virtual environment and install Poetry version 1.8 and use Poetry from there.

### Create credentials

**If you are a community contributor**, follow the instructions in
the [documentation](https://docs.airbyte.io/integrations/sources/exact)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the
`source_exact/spec.yaml` file.
Note that any directory named `secrets` is gitignored across the entire Airbyte repo, so there is no danger of
accidentally checking in sensitive information.
See `integration_tests/sample_config.json` for a sample config file.

**If you are an Airbyte core member**, copy the credentials in Lastpass under the secret name `source exact test creds`
and place them into `secrets/config.json`.

### Installing the connector

From this connector directory, run:

```shell
poetry install --with dev
```

### Locally running the connector

Using Poetry

```shell
poetry run source-exact spec
```

Or with the current virtual environment activated

```shell
python main.py spec
python main.py check --config secrets/config.json
python main.py discover --config secrets/config.json
python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

### Optional flags

```
--debug
```

## Testing

Make sure to familiarize yourself
with [pytest test discovery](https://docs.pytest.org/en/latest/goodpractices.html#test-discovery) to know how your test
files and methods should be named.
First install test dependencies into your virtual environment:

```shell
uv sync --dev
```

### Unit Tests

To run unit tests locally, from the connector directory `source_exact` run:

```
uv run pytest unit_tests/
```

Via airbyte-cdk
```shell
airbyte-cdk image test
```
