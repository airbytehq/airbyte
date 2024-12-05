# Braintree Source

This is the repository for the Braintree source connector, written in Python.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.io/integrations/sources/braintree).

## Local development

### Prerequisites
* Python (~=3.9)
* Poetry (~=1.7) - installation instructions [here](https://python-poetry.org/docs/#installation)

### Installing the connector
From this connector directory, run:
```bash
poetry install --with dev
```

#### Create credentials

**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.io/integrations/sources/braintree)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `source_braintree/spec.json` file.
Note that the `secrets` directory is gitignored by default, so there is no danger of accidentally checking in sensitive information.
See `integration_tests/sample_config.json` for a sample config file.

**If you are an Airbyte core member**, copy the credentials in Lastpass under the secret name `source braintree test creds`
and place them into `secrets/config.json`.

### Locally running the connector

```
poetry run source-braintree spec
poetry run source-braintree check --config secrets/config.json
poetry run source-braintree discover --config secrets/config.json
poetry run source-braintree read --config secrets/config.json --catalog sample_files/configured_catalog.json
```

### Running unit tests
To run unit tests locally, from the connector directory run:
```
poetry run pytest
```

### Locally running the connector docker image

#### Build

**Via [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md) (recommended):**

```bash
airbyte-ci connectors --name=source-braintree build
```

An image will be built with the tag `airbyte/source-braintree:dev`.


#### Run

Then run any of the connector commands as follows:

```
docker run --rm airbyte/source-braintree:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-braintree:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-braintree:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-braintree:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

## Testing

You can run our full test suite locally using [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md):

```bash
airbyte-ci connectors --name=source-braintree test
```

### Customizing acceptance Tests

Customize `acceptance-test-config.yml` file to configure tests. See [Connector Acceptance Tests](https://docs.airbyte.com/connector-development/testing-connectors/connector-acceptance-tests-reference) for more information.
If your connector requires to create or destroy resources for use during acceptance tests create fixtures for it and place them inside integration_tests/acceptance.py.

## Dependency Management

All of your dependencies should be managed via Poetry. 
To add a new dependency, run:
```bash
poetry add <package-name>
```

Please commit the changes to `pyproject.toml` and `poetry.lock` files.

### Publishing a new version of the connector

You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?

1. Make sure your changes are passing our test suite: `airbyte-ci connectors --name=source-braintree test`
2. Bump the connector version (please follow [semantic versioning for connectors](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#semantic-versioning-for-connectors)): 
    - bump the `dockerImageTag` value in in `metadata.yaml`
    - bump the `version` value in `pyproject.toml`
3. Make sure the `metadata.yaml` content is up to date.
4. Make the connector documentation and its changelog is up to date (`docs/integrations/sources/braintree.md`).
5. Create a Pull Request: use [our PR naming conventions](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#pull-request-title-convention).
6. Pat yourself on the back for being an awesome contributor.
7. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.
8. Once your PR is merged, the new version of the connector will be automatically published to Docker Hub and our connector registry.
