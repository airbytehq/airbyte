# Source Declarative Manifest CLI

The source-declarative-manifest CLI is included in the airbyte-cdk package.
This CLI enables connector interfaces to be run locally on manifest-only connectors,
much like we already do with Python connectors.

## Installation

The airbyte-cdk library can be installed globally using pipx:

```bash
pipx install airbyte-cdk
```

If you are using a cloned airbyte-python-cdk repo locally,
you can also create a virtual environment to enable the CLI.
From the root directory of airbyte-python-cdk:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

### Options

--help: displays the list of available commands

### Commands

- spec: Outputs the JSON configuration specification. NOTE: This currently just outputs the base source-declarative-manifest spec
- check: Runs a connection_check to verify a connection can be made with the passed config
- discover: Outputs a catalog describing the source's schema
- read: Reads the source using the passed config and catalog, and outputs messages to STDOUT

### Command options

- --config: The relative path to the config to inject into SDM.
- --catalog: The relative path to the configured catalog.
- --state: The relative path to the state object to pass. Only used when running an incremental read.
- --manifest-path: The relative path to the local YAML manifest to inject into SDM.
- --components-path: The relative path to the custom components to mount, if they exist.

| Option              | spec | check    | discover | read     |
| ------------------- | ---- | -------- | -------- | -------- |
| `--config`          | ❌   | required | required | required |
| `--catalog`         | ❌   | ❌       | required | required |
| `--state`           | ❌   | ❌       | ❌       | optional |
| `--manifest-path`   | ❌   | required | required | required |
| `--components-path` | ❌   | optional | optional | optional |

### Examples

Here are some basic examples of how to run source-declarative-manifest commands locally.
Note that the paths are relative. These examples assume the user is currently at the root level of a connector dir:

```bash
source-declarative-manifest check --config secrets/config.json --manifest-path manifest.yaml
```

```bash
source-declarative-manifest read --config secrets/config.json --catalog integration_tests/configured_catalog.json --manifest-path manifest.yaml --components-path components.py
```
