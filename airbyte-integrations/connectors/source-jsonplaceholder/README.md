# JSONPlaceholder source connector

This directory contains the manifest-only connector for `source-jsonplaceholder`.
This _manifest-only_ connector is not a Python package on its own, as it runs inside of the base `source-declarative-manifest` image.

For information about how to configure and use this connector within Airbyte, see [the connector's full documentation](https://docs.airbyte.com/integrations/sources/jsonplaceholder).

## Local development

We recommend using the Connector Builder to edit this connector.
Using either Airbyte Cloud or your local Airbyte OSS instance, navigate to the **Builder** tab and select **Import a YAML**.
Then select the connector's `manifest.yaml` file to load the connector into the Builder. You're now ready to make changes to the connector!

If you prefer to develop locally, you can follow the instructions below.

### Building the docker image

You can build any manifest-only connector with `airbyte-ci`:

1. Install [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md)
2. Run the following command to build the docker image:

```bash
airbyte-ci connectors --name=source-jsonplaceholder build
```

An image will be available on your host with the tag `airbyte/source-jsonplaceholder:dev`.

### Creating credentials

This connector does not require any credentials. JSONPlaceholder is a free, public API.
Create a file `secrets/config.json` with an empty JSON object `{}`.

### Running as a docker container

Then run any of the standard source connector commands:

```bash
docker run --rm airbyte/source-jsonplaceholder:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-jsonplaceholder:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-jsonplaceholder:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-jsonplaceholder:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

### Running the CI test suite

You can run our full test suite locally using [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md):

```bash
airbyte-ci connectors --name=source-jsonplaceholder test
```
