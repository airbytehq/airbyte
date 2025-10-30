# Amazon Amp Source

This is the repository for the Amazon Amp configuration based source connector.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.com/integrations/sources/amazon-amp).

## Local development

### Prerequisites

* Python (`^3.9`)
* Poetry (`^1.7`) - installation instructions [here](https://python-poetry.org/docs/#installation)

### Installing the connector

From this connector directory, run:
```bash
poetry install --with dev
```

### Create credentials

Create a file `secrets/config.json` based on the `integration_tests/sample_config.json` file.
Note that any directory named `secrets` is gitignored across the entire Airbyte repo, so there is no danger of accidentally checking in sensitive information.

### Locally running the connector

```
poetry run source-amazon-amp spec
poetry run source-amazon-amp check --config secrets/config.json
poetry run source-amazon-amp discover --config secrets/config.json
poetry run source-amazon-amp read --config secrets/config.json --catalog integration_tests/catalog.json
```

### Running tests

To run tests locally, from the connector directory run:

```
poetry run pytest tests
```

### Building the docker image

1. Install [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md)
2. Run the following command to build the docker image:
```bash
airbyte-ci connectors --name=source-amazon-amp build
```

An image will be available on your host with the tag `airbyte/source-amazon-amp:dev`.

### Running as a docker container

Then run any of the connector commands as follows:
```
docker run --rm airbyte/source-amazon-amp:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-amazon-amp:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-amazon-amp:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-amazon-sqs:dev read --config /secrets/config.json --catalog /integration_tests/catalog.json
```

### Running our CI test suite

You can run our full test suite locally using [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md):
```bash
airbyte-ci connectors --name=source-amazon-amp test
```

### Dependency Management

All of your dependencies should be managed via Poetry. 
To add a new dependency, run:
```bash
poetry add <package-name>
```

Please commit the changes to `pyproject.toml` and `poetry.lock` files.

## Publishing a new version of the connector

You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?
1. Make sure your changes are passing our test suite: `airbyte-ci connectors --name=source-amazon-amp test`
2. Bump the connector version (please follow [semantic versioning for connectors](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#semantic-versioning-for-connectors)): 
    - bump the `dockerImageTag` value in in `metadata.yaml`
    - bump the `version` value in `pyproject.toml`
3. Make sure the `metadata.yaml` content is up to date.
4. Make sure the connector documentation and its changelog is up to date (`docs/integrations/sources/amazon-amp.md`).
5. Create a Pull Request: use [our PR naming conventions](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#pull-request-title-convention).
6. Pat yourself on the back for being an awesome contributor.
7. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.
8. Once your PR is merged, the new version of the connector will be automatically published to Docker Hub and our connector registry.
