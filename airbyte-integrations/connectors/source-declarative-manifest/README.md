# Declarative-Manifest source connector

This is the repository for the Declarative-Manifest source connector, written in Python.
The declarative manifest source connector is a special connector that can create an arbitrary source
connector from a declarative manifest file. This allows users to create a source connector without writing any code.

**Note**: This connector is managed by the Airbyte Python CDK release process. It can be run as a standalone connector
in Docker and PyAirbyte, but is not yet meant to be run in the platform as a standalone connector. This source is
an interface to the low-code CDK and as such, should not be modified without a corresponding CDK change.

## Local development

### Prerequisites

- Python (~=3.9)
- Poetry (~=1.7) - installation instructions [here](https://python-poetry.org/docs/#installation)

### Installing the connector

From this connector directory, run:

```bash
poetry install
```

### Create credentials

The credentials for source-declarative-manifest are a little different. Your `config` will need to contain the
injected declarative manifest, as indicated in the `spec`. It will also need to contain the fields that the spec
coming out of the manifest requires. An example is available in `integration_tests/pokeapi_config.json`. To use
this example in the following instructions, copy this file to `secrets/config.json`.

### Locally running the connector

```
poetry run source-declarative-manifest spec
poetry run source-declarative-manifest check --config secrets/config.json
poetry run source-declarative-manifest discover --config secrets/config.json
poetry run source-declarative-manifest read --config secrets/config.json --catalog sample_files/configured_catalog.json
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
airbyte-ci connectors --name=source-declarative-manifest build
```

An image will be available on your host with the tag `airbyte/source-declarative-manifest:dev`.

### Running as a docker container

Then run any of the connector commands as follows:

```
docker run --rm airbyte/source-declarative-manifest:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-declarative-manifest:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-declarative-manifest:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-declarative-manifest:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

### Running our CI test suite

You can run our full test suite locally using [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md):

```bash
airbyte-ci connectors --name=source-declarative-manifest test
```

This source does not currently pass the full test suite.

### Dependency Management

The manifest declarative source is built to be an interface to the low-code CDK source. This means that
this source should not have any production dependencies other than the Airbyte Python CDK. If for some reason
you feel that a new dependency is needed, you likely want to add it to the CDK instead. It is expected
that a given version of the source-declarative-manifest connector corresponds to the same version in
its CDK dependency.

## Publishing a new version of the connector

New versions of this connector should only be published (automatically) via the manual Airbyte CDK release process.
If you want to make a change to this connector that is not a result of a CDK change and a corresponding
CDK dependency bump, please reach out to the Connector Extensibility team for guidance.
