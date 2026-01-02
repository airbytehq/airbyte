# BigGeo Source

This is the repository for the BigGeo source connector, written in Python.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.com/integrations/sources/biggeo).

## Features

### Chunked Pagination

This connector supports efficient chunked pagination for handling large datasets. Instead of fetching all data at once (which can cause memory issues and timeouts), the connector fetches data in configurable chunks.

**How it works:**

1. **First request**: The connector makes an initial request without a cursor or syncId
2. **API response**: Returns `data[]`, `syncId`, `nextCursor`, and `hasMore`
3. **Subsequent requests**: Include the `syncId` and `cursor=nextCursor` from the previous response
4. **Completion**: Continue fetching until `hasMore=False`

**Configuration:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_key` | string | Yes | - | API Key for authenticating with BigGeo |
| `data_source_name` | string | No | - | Name of the data source to retrieve |
| `chunk_size` | integer | No | 1000 | Number of records per chunk (1-10000) |

**Example configuration with custom chunk size:**

```json
{
  "api_key": "your-biggeo-api-key",
  "data_source_name": "my_data_source",
  "chunk_size": 5000
}
```

## Local development

### Prerequisites

* Python (>=3.10, <3.14)
* Poetry (~=1.7) - installation instructions [here](https://python-poetry.org/docs/#installation)

### Installing the connector

From this connector directory, run:

```bash
poetry install --with dev
```

### Create credentials

**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.com/integrations/sources/biggeo)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `source_biggeo/spec.json` file.
Note that any directory named `secrets` is gitignored across the entire Airbyte repo, so there is no danger of accidentally checking in sensitive information.

**Example `secrets/config.json`:**

```json
{
  "api_key": "your-biggeo-api-key",
  "data_source_name": "my_data_source",
  "chunk_size": 1000
}
```

Note: `chunk_size` is optional and defaults to 1000 records per chunk.

### Locally running the connector

```bash
poetry run source-biggeo spec
poetry run source-biggeo check --config secrets/config.json
poetry run source-biggeo discover --config secrets/config.json
poetry run source-biggeo read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

### Running unit tests

To run unit tests locally, from the connector directory run:

```bash
poetry run pytest unit_tests
```

### Running integration tests

To run integration tests locally, make sure you have a `secrets/config.json` as explained above, and then run:

```bash
poetry run pytest integration_tests
```

### Building the docker image

1. Install [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md)
2. Run the following command to build the docker image:

```bash
airbyte-ci connectors --name=source-biggeo build
```

An image will be available on your host with the tag `airbyte/source-biggeo:dev`.

### Running as a docker container

Then run any of the connector commands as follows:

```bash
docker run --rm airbyte/source-biggeo:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-biggeo:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-biggeo:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-biggeo:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

### Running our CI test suite

You can run our full test suite locally using [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md):

```bash
airbyte-ci connectors --name=source-biggeo test
```

### Customizing acceptance Tests

Customize `acceptance-test-config.yml` file to configure acceptance tests. See [Connector Acceptance Tests](https://docs.airbyte.com/connector-development/testing-connectors/connector-acceptance-tests-reference) for more information.
If your connector requires to create or destroy resources for use during acceptance tests create fixtures for it and place them inside integration_tests/acceptance.py.

### Dependency Management

All of your dependencies should be managed via Poetry.
To add a new dependency, run:

```bash
poetry add <package-name>
```

Please commit the changes to `pyproject.toml` and `poetry.lock` files.

## Publishing a new version of the connector

You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?

1. Make sure your changes are passing our test suite: `airbyte-ci connectors --name=source-biggeo test`
2. Bump the connector version (please follow [semantic versioning for connectors](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#semantic-versioning-for-connectors)):
    - bump the `dockerImageTag` value in `metadata.yaml`
    - bump the `version` value in `pyproject.toml`
3. Make sure the `metadata.yaml` content is up to date.
4. Make sure the connector documentation and its changelog is up to date (`docs/integrations/sources/biggeo.md`).
5. Create a Pull Request: use [our PR naming conventions](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#pull-request-title-convention).
6. Pat yourself on the back for being an awesome contributor.
7. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.
8. Once your PR is merged, the new version of the connector will be automatically published to Docker Hub and our connector registry.
