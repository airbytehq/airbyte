# HubSpot source connector

This directory contains the manifest-only connector for `source-hubspot`.
This _manifest-only_ connector is not a Python package on its own, as it runs inside of the base `source-declarative-manifest` image.

For information about how to configure and use this connector within Airbyte, see [the connector's full documentation](https://docs.airbyte.com/integrations/sources/hubspot).

## Local development

If you prefer to develop locally, you can follow the instructions below.

### Building the docker image

You can build any manifest-only connector with `airbyte-ci`:

1. Install [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md)
2. Run the following command to build the docker image:

```bash
airbyte-ci connectors --name=source-hubspot build
```

An image will be available on your host with the tag `airbyte/source-hubspot:dev`.

### Creating credentials

**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.com/integrations/sources/hubspot)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `spec` object in the connector's `manifest.yaml` file.
Note that any directory named `secrets` is gitignored across the entire Airbyte repo, so there is no danger of accidentally checking in sensitive information.

### Running as a docker container

Then run any of the standard source connector commands:

```bash
docker run --rm airbyte/source-hubspot:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-hubspot:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-hubspot:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-hubspot:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

### Running the CI test suite

You can run our full test suite locally using [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md):

```bash
airbyte-ci connectors --name=source-hubspot test
```
