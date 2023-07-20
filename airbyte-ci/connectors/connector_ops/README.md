# connector_ops

A collection of tools and checks run by Github Actions

## Running Locally

From this directory, create a virtual environment:

```
python3 -m venv .venv
```

This will generate a virtualenv for this module in `.venv/`. Make sure this venv is active in your
development environment of choice. To activate it from the terminal, run:

```bash
source .venv/bin/activate
pip install -e . # assuming you are in the ./airbyte-ci/connectors/connector_ops directory
```

pip will make binaries for all the commands in setup.py, so you can run `allowed-hosts-checks` directly from the virtual-env

## Testing Locally

To install requirements to run unit tests, use:

```
pip install -e ".[tests]"
```

Unit tests are currently configured to be run from the base `airbyte` directory. You can run the tests from that directory with the following command:

```
pytest -s airbyte-ci/connector_ops/connectors/tests
```