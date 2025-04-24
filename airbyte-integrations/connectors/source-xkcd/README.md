# Xkcd Source

This directory contains xkcd source connector for Airbyte.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.com/integrations/sources/xkcd).

## Local development

`source-xkcd` is a _manifest-only_ connector. Meaning, it's not a Python package on it's own, and it runs inside of the `source-declarative-manifest`.

### Building the docker image

You can build any manifest-only connector just as any other connector with `airbyte-ci`:


1. Install [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md)
2. Run the following command to build the docker image:
```bash
airbyte-ci connectors --name=source-xkcd build
```

An image will be available on your host with the tag `airbyte/source-xkcd:dev`.

### Running as a docker container

Then run any of the connector commands as follows:
```
docker run --rm airbyte/source-xkcd:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-xkcd:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-xkcd:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-xkcd:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

### Running the CI test suite

You can run our full test suite locally using [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md):
```bash
airbyte-ci connectors --name=source-xkcd test
```

## Publishing a new version of the connector

If you want to contribute changes to `source-xkcd`, here's how you can do that:
1. Make sure your changes are passing our test suite: `airbyte-ci connectors --name=source-xkcd test`
2. Bump the connector version (please follow [semantic versioning for connectors](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#semantic-versioning-for-connectors)):
    - bump the `dockerImageTag` value in in `metadata.yaml`
    - bump the `version` value in `pyproject.toml`
3. Make sure the `metadata.yaml` content is up to date.
4. Make sure the connector documentation and its changelog is up to date (`docs/integrations/sources/xkcd.md`).
5. Create a Pull Request: use [our PR naming conventions](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#pull-request-title-convention).
6. Pat yourself on the back for being an awesome contributor.
7. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.
8. Once your PR is merged, the new version of the connector will be automatically published to Docker Hub and our connector registry.
