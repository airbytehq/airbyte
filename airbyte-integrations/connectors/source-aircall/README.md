# Aircall source connector

This directory contains the manifest-only connector for `source-aircall`.
This _manifest-only_ connector is not a Python package on its own, as it runs inside of the base `source-declarative-manifest` image.

For information about how to configure and use this connector within Airbyte, see [the connector's full documentation](https://docs.airbyte.com/integrations/sources/aircall).

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
airbyte-ci connectors --name=source-aircall build
```

An image will be available on your host with the tag `airbyte/source-aircall:dev`.

### Creating credentials

**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.com/integrations/sources/aircall)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `spec` object in the connector's `manifest.yaml` file.
Note that any directory named `secrets` is gitignored across the entire Airbyte repo, so there is no danger of accidentally checking in sensitive information.

### Running as a docker container

Then run any of the standard source connector commands:

```bash
docker run --rm airbyte/source-aircall:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-aircall:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-aircall:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-aircall:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

### Running the CI test suite

You can run our full test suite locally using [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md):

```bash
airbyte-ci connectors --name=source-aircall test
```

## Publishing a new version of the connector

If you want to contribute changes to `source-aircall`, here's how you can do that:
1. Make your changes locally, or load the connector's manifest into Connector Builder and make changes there.
2. Make sure your changes are passing our test suite with `airbyte-ci connectors --name=source-aircall test`
3. Bump the connector version (please follow [semantic versioning for connectors](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#semantic-versioning-for-connectors)):
    - bump the `dockerImageTag` value in in `metadata.yaml`
4. Make sure the connector documentation and its changelog is up to date (`docs/integrations/sources/aircall.md`).
5. Create a Pull Request: use [our PR naming conventions](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#pull-request-title-convention).
6. Pat yourself on the back for being an awesome contributor.
7. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.
8. Once your PR is merged, the new version of the connector will be automatically published to Docker Hub and our connector registry.