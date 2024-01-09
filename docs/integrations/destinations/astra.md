# Astra Destination

This page contains the setup guide and reference information for the destination-astra connector.

## Prerequisites

#### Minimum Python version required `= 3.9.0`

## Setup Guide

#### Activate Virtual Environment and install dependencies
From this connector directory, create a virtual environment:
```
python -m venv .venv
```

This will generate a virtualenv for this module in `.venv/`. Make sure this venv is active in your
development environment of choice. To activate it from the terminal, run:
```
source .venv/bin/activate
pip install -r requirements.txt
```
If you are in an IDE, follow your IDE's instructions to activate the virtualenv.

Note that while we are installing dependencies from `requirements.txt`, you should only edit `setup.py` for your dependencies. `requirements.txt` is
used for editable installs (`pip install -e`) to pull in Python dependencies from the monorepo and will call `setup.py`.

#### Create credentials
**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.com/integrations/destinations/astra)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `destination_astra/spec.json` file.
Note that the `secrets` directory is gitignored by default, so there is no danger of accidentally checking in sensitive information.
See `integration_tests/sample_config.json` for a sample config file.

**If you are an Airbyte core member**, copy the credentials in Lastpass under the secret name `destination astra test creds`
and place them into `secrets/config.json`.

### Locally running the connector
```
python main.py spec
python main.py check --config secrets/config.json
python main.py discover --config secrets/config.json
python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

### Locally running the connector docker image

#### Use `airbyte-ci` to build your connector
The Airbyte way of building this connector is to use our `airbyte-ci` tool.
You can follow install instructions [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md#L1).
Then running the following command will build your connector:

```bash
airbyte-ci connectors --name destination-astra build
```
Once the command is done, you will find your connector image in your local docker registry: `airbyte/destination-astra:dev`.

## Supported Sync Modes

## Supported Streams

## Changelog
| Version | Date       | Pull Request                                             | Subject                     |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------- |
| 0.1.0   | 2024-01-08 |                                                          | Initial Release             |
