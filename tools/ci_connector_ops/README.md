# CI_CONNECTOR_OPS

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
pip install -e . # assuming you are in the ./tools/ci_connector_ops directory
```

pip will make binaries for all the commands in setup.py, so you can run `allowed-hosts-checks` directly from the virtual-env
