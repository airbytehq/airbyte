# BigGeo Destination

This is the repository for the BigGeo destination connector, written in Python.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.com/integrations/destinations/biggeo).

## Features

### Batched Chunking

This connector supports efficient batched data ingestion for handling large datasets. Instead of sending records one at a time, the connector batches records together and sends them in configurable chunks.

**How it works:**

1. **Session initialization**: The connector generates a `sync_id` to track the sync session
2. **Record buffering**: Records are buffered in memory until the batch size is reached
3. **Batch sending**: When the buffer is full, records are sent to the API as chunks
4. **State handling**: When a STATE message is received, the current buffer is flushed
5. **Finalization**: The last batch is sent with `is_final=True` to trigger data export

**Configuration:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_key` | string | Yes | - | API Key for authenticating with BigGeo |
| `batch_size` | integer | No | 1000 | Number of records to batch before sending (1-10000) |

**Example configuration with custom batch size:**

```json
{
  "api_key": "your-biggeo-api-key",
  "batch_size": 5000
}
```

**Benefits:**

- **Network efficient**: Reduces HTTP overhead by batching multiple records per request
- **Session tracking**: Uses `sync_id` for reliable session management on the server
- **Resumable syncs**: Server maintains state via Redis for fault tolerance
- **Configurable throughput**: Adjust `batch_size` based on your data and network conditions

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

**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.com/integrations/destinations/biggeo)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `destination_biggeo/spec.json` file.
Note that any directory named `secrets` is gitignored across the entire Airbyte repo, so there is no danger of accidentally checking in sensitive information.

**Example `secrets/config.json`:**

```json
{
  "api_key": "your-biggeo-api-key",
  "batch_size": 1000
}
```

Note: `batch_size` is optional and defaults to 1000 records per batch.

### Locally running the connector

```bash
poetry run destination-biggeo spec
poetry run destination-biggeo check --config secrets/config.json
poetry run destination-biggeo write --config secrets/config.json --catalog integration_tests/configured_catalog.json
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
airbyte-ci connectors --name=destination-biggeo build
```

An image will be available on your host with the tag `airbyte/destination-biggeo:dev`.

### Running as a docker container

Then run any of the connector commands as follows:

```bash
docker run --rm airbyte/destination-biggeo:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/destination-biggeo:dev check --config /secrets/config.json
# messages.jsonl is a file containing line-separated JSON representing AirbyteMessages
cat messages.jsonl | docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/destination-biggeo:dev write --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

### Running our CI test suite

You can run our full test suite locally using [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md):

```bash
airbyte-ci connectors --name=destination-biggeo test
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

1. Make sure your changes are passing our test suite: `airbyte-ci connectors --name=destination-biggeo test`
2. Bump the connector version (please follow [semantic versioning for connectors](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#semantic-versioning-for-connectors)):
    - bump the `dockerImageTag` value in `metadata.yaml`
    - bump the `version` value in `pyproject.toml`
3. Make sure the `metadata.yaml` content is up to date.
4. Make sure the connector documentation and its changelog is up to date (`docs/integrations/destinations/biggeo.md`).
5. Create a Pull Request: use [our PR naming conventions](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#pull-request-title-convention).
6. Pat yourself on the back for being an awesome contributor.
7. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.
8. Once your PR is merged, the new version of the connector will be automatically published to Docker Hub and our connector registry.