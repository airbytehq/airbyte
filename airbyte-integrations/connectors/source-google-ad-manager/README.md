# Google Ad Manager Source

This is the repository for the Google Ad Manager source connector, written in Python.
For information about how to use this connector within Airbyte, see [the documentation](./google-ad-manager.md).

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

**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.com/integrations/sources/google-ad-manager)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `src/source_google_ad_manager/spec.yaml` file.
Note that any directory named `secrets` is gitignored across the entire Airbyte repo, so there is no danger of accidentally checking in sensitive information.
See `sample_files/sample_config.json` for a sample config file.


### Locally running the connector

```
poetry run source-google-ad-manager spec
poetry run source-google-ad-manager check --config secrets/config.json
poetry run source-google-ad-manager discover --config secrets/config.json
poetry run source-google-ad-manager read --config secrets/config.json --catalog sample_files/configured_catalog.json
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
airbyte-ci connectors --name=source-google-ad-manager build
```

An image will be available on your host with the tag `airbyte/source-google-ad-manager:dev`.


### Running as a docker container

Then run any of the connector commands as follows:
```
docker run --rm airbyte/source-google-ad-manager:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-google-ad-manager:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-google-ad-manager:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-google-ad-manager:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

### Running our CI test suite

Please note: the following command works only in the airbyte root directory

You can run our full test suite locally using [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md):

```bash
airbyte-ci connectors --name=source-google-ad-manager test
```

### Customizing acceptance Tests

Customize `acceptance-test-config.yml` file to configure acceptance tests. See [Connector Acceptance Tests](https://docs.airbyte.com/connector-development/testing-connectors/connector-acceptance-tests-reference) for more information.
If your connector requires to create or destroy resources for use during acceptance tests create fixtures for it and place them inside integration_tests/acceptance.py.

#### Running acceptance tests 
In order to do so you need to download the airbyte repo from github.
After that go on the `airbyte-integrations/bases/connector-acceptance-test`
subfolder of the airbyte repo and do a poetry install command:

```bash
poetry install
```

then switch back to the connector repo and launch:

```bash
poetry run pytest -p connector_acceptance_test.plugin --acceptance-test-config=./ --pdb
```
this will launche the acceptance tests needed to submit the repo to airbyte.

Please note that [acceptance-test-config.yml](acceptance-test-config.yml) will
likely contain a reference to the docker container with the connector.
you can build the docker container using the this [Dockerfile](Dockerfile).


### Dependency Management

All of your dependencies should be managed via Poetry. 
To add a new dependency, run:

```bash
poetry add <package-name>
```

Please commit the changes to `pyproject.toml` and `poetry.lock` files.

## Publishing a new version of the connector

You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?
1. Make sure your changes are passing our test suite: `airbyte-ci connectors --name=source-google-ad-manager test`
2. Bump the connector version (please follow [semantic versioning for connectors](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#semantic-versioning-for-connectors)): 
    - bump the `dockerImageTag` value in in `metadata.yaml`
    - bump the `version` value in `pyproject.toml`
3. Make sure the `metadata.yaml` content is up to date.
4. Make sure the connector documentation and its changelog is up to date (`docs/integrations/sources/google-ad-manager.md`).
5. Create a Pull Request: use [our PR naming conventions](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#pull-request-title-convention).
6. Pat yourself on the back for being an awesome contributor.
7. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.
8. Once your PR is merged, the new version of the connector will be automatically published to Docker Hub and our connector registry.



## Notes about GitLab
* You can override the included template(s) by including variable overrides
* SAST customization: https://docs.gitlab.com/ee/user/application_security/sast/#customizing-the-sast-settings
* Secret Detection customization: https://docs.gitlab.com/ee/user/application_security/secret_detection/pipeline/#customization
* Dependency Scanning customization: https://docs.gitlab.com/ee/user/application_security/dependency_scanning/#customizing-the-dependency-scanning-settings
* Container Scanning customization: https://docs.gitlab.com/ee/user/application_security/container_scanning/#customizing-the-container-scanning-settings
* Note that environment variables can be set in several places
* See https://docs.gitlab.com/ee/ci/variables/#cicd-variable-precedence
