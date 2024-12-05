# PostHog Source

This is the repository for the PostHog source connector, written in Python.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.io/integrations/sources/posthog).

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

**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.io/integrations/sources/posthog)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `source_posthog/spec.json` file.
Note that any directory named `secrets` is gitignored across the entire Airbyte repo, so there is no danger of accidentally checking in sensitive information.
See `sample_files/sample_config.json` for a sample config file.

**If you are an Airbyte core member**, copy the credentials in Lastpass under the secret name `source posthog test creds`
and place them into `secrets/config.json`.

### Locally running the connector

```
poetry run source-posthog spec
poetry run source-posthog check --config secrets/config.json
poetry run source-posthog discover --config secrets/config.json
poetry run source-posthog read --config secrets/config.json --catalog sample_files/configured_catalog.json
```

### Building the docker image

1. Install [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md)
2. Run the following command to build the docker image:
```bash
airbyte-ci connectors --name=source-posthog build
```

An image will be available on your host with the tag `airbyte/source-posthog:dev`.

### Running as a docker container

Then run any of the connector commands as follows:

```
docker run --rm airbyte/source-posthog:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-posthog:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-posthog:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/sample_files:/sample_files airbyte/source-posthog:dev read --config /secrets/config.json --catalog /sample_files/configured_catalog.json
```

### Running our CI test suite

You can run our full test suite locally using [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md):
```bash
airbyte-ci connectors --name=source-posthog test
```

### Customizing acceptance Tests

Customize `acceptance-test-config.yml` file to configure tests. See [Connector Acceptance Tests](https://docs.airbyte.com/connector-development/testing-connectors/connector-acceptance-tests-reference) for more information.
If your connector requires to create or destroy resources for use during acceptance tests create fixtures for it and place them inside integration_tests/acceptance.py.

## Dependency Management

All of your dependencies should go in `setup.py`, NOT `requirements.txt`. The requirements file is only used to connect internal Airbyte dependencies in the monorepo for local development.
We split dependencies between two groups, dependencies that are:

- required for your connector to work need to go to `MAIN_REQUIREMENTS` list.
- required for the testing need to go to `TEST_REQUIREMENTS` list

### Publishing a new version of the connector

You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?

1. Make sure your changes are passing our test suite: `airbyte-ci connectors --name=source-posthog test`
2. Bump the connector version in `metadata.yaml`: increment the `dockerImageTag` value. Please follow [semantic versioning for connectors](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#semantic-versioning-for-connectors).
3. Make sure the `metadata.yaml` content is up to date.
4. Make the connector documentation and its changelog is up to date (`docs/integrations/sources/posthog.md`).
5. Create a Pull Request: use [our PR naming conventions](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#pull-request-title-convention).
6. Pat yourself on the back for being an awesome contributor.
7. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.