# Altertable Destination

This is the repository for the Altertable destination connector, written in Python.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.com/integrations/destinations/altertable).

## Local development

### Prerequisites

**To iterate on this connector, make sure to complete this prerequisites section.**

#### Minimum Python version required `= 3.10`

#### Build & Activate Virtual Environment and install dependencies

From this connector directory, create a virtual environment:

```bash
poetry install --with dev
```

#### Create credentials

**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.com/integrations/destinations/altertable)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `destination_altertable/spec.json` file.
Note that the `secrets` directory is gitignored by default, so there is no danger of accidentally checking in sensitive information.
See `integration_tests/invalid_config.json` for a sample config file structure.

**If you are an Airbyte core member**, copy the credentials in Lastpass under the secret name `destination altertable test creds`
and place them into `secrets/config.json`.

### Locally running the connector

```bash
python main.py spec
python main.py check --config secrets/config.json
# messages.jsonl is a file containing line-separated JSON representing AirbyteMessages
cat integration_tests/messages.jsonl | python main.py write --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

### Locally running the connector docker image

#### Build

**Via [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md) (recommended):**

```bash
airbyte-ci connectors --name=destination-altertable build
```

An image will be built with the tag `airbyte/destination-altertable:dev`.

**Via `docker build`:**

```bash
docker build -t airbyte/destination-altertable:dev .
```

#### Run

Then run any of the connector commands as follows:

```bash
docker run --rm airbyte/destination-altertable:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/destination-altertable:dev check --config /secrets/config.json
# messages.jsonl is a file containing line-separated JSON representing AirbyteMessages
cat integration_tests/messages.jsonl | docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/destination-altertable:dev write --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

## Testing

You can run our full test suite locally using [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md):

```bash
airbyte-ci connectors --name=destination-altertable test
```

### Unit tests (no external service required)

```bash
poetry run pytest unit_tests/
```

### Integration tests (requires Docker, spins up altertable-mock via testcontainers)

```bash
poetry run pytest integration_tests/
```

### Customizing acceptance tests

Customize `acceptance-test-config.yml` to configure tests. See [Connector Acceptance Tests](https://docs.airbyte.com/connector-development/testing-connectors/connector-acceptance-tests-reference) for more information.
If your connector requires to create or destroy resources for use during acceptance tests, create fixtures for it and place them inside `integration_tests/acceptance.py`.

## Dependency Management

All of your dependencies should go in `pyproject.toml`. We split dependencies between two groups:

- Required for your connector to work: `[tool.poetry.dependencies]`
- Required for testing: `[tool.poetry.group.dev.dependencies]`

### Publishing a new version of the connector

1. Make sure your changes are passing our test suite: `airbyte-ci connectors --name=destination-altertable test`
2. Bump the connector version in `metadata.yaml`: increment the `dockerImageTag` value. Please follow [semantic versioning for connectors](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#semantic-versioning-for-connectors).
3. Make sure the `metadata.yaml` content is up to date.
4. Make sure the connector documentation and its changelog are up to date (`docs/integrations/destinations/altertable.md`).
5. Create a Pull Request: use [our PR naming conventions](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#pull-request-title-convention).
6. Pat yourself on the back for being an awesome contributor.
7. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.
