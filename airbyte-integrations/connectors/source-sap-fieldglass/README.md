# Sap Fieldglass Source

This is the repository for the Sap Fieldglass configuration based source connector.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.io/integrations/sources/sap-fieldglass).

## Local development

#### Building via Gradle
You can also build the connector in Gradle. This is typically used in CI and not needed for your development workflow.

To build using Gradle, from the Airbyte repository root, run:
```
./gradlew :airbyte-integrations:connectors:source-sap-fieldglass:build
```

#### Create credentials
**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.io/integrations/sources/sap-fieldglass)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `source_sap_fieldglass/spec.yaml` file.
Note that any directory named `secrets` is gitignored across the entire Airbyte repo, so there is no danger of accidentally checking in sensitive information.
See `integration_tests/sample_config.json` for a sample config file.

**If you are an Airbyte core member**, copy the credentials in Lastpass under the secret name `source sap-fieldglass test creds`
and place them into `secrets/config.json`.

### Locally running the connector docker image

#### Build
First, make sure you build the latest Docker image:
```
docker build . -t airbyte/source-sap-fieldglass:dev
```

You can also build the connector image via Gradle:
```
./gradlew :airbyte-integrations:connectors:source-sap-fieldglass:airbyteDocker
```
When building via Gradle, the docker image name and tag, respectively, are the values of the `io.airbyte.name` and `io.airbyte.version` `LABEL`s in
the Dockerfile.

#### Run
Then run any of the connector commands as follows:
```
docker run --rm airbyte/source-sap-fieldglass:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-sap-fieldglass:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-sap-fieldglass:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-sap-fieldglass:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```
## Testing

#### Acceptance Tests
Customize `acceptance-test-config.yml` file to configure tests. See [Source Acceptance Tests](https://docs.airbyte.io/connector-development/testing-connectors/source-acceptance-tests-reference) for more information.
If your connector requires to create or destroy resources for use during acceptance tests create fixtures for it and place them inside integration_tests/acceptance.py.

To run your integration tests with docker

### Using gradle to run tests
All commands should be run from airbyte project root.
To run unit tests:
```
./gradlew :airbyte-integrations:connectors:source-sap-fieldglass:unitTest
```
To run acceptance and custom integration tests:
```
./gradlew :airbyte-integrations:connectors:source-sap-fieldglass:integrationTest
```

## Dependency Management
All of your dependencies should go in `setup.py`, NOT `requirements.txt`. The requirements file is only used to connect internal Airbyte dependencies in the monorepo for local development.
We split dependencies between two groups, dependencies that are:
* required for your connector to work need to go to `MAIN_REQUIREMENTS` list.
* required for the testing need to go to `TEST_REQUIREMENTS` list

### Publishing a new version of the connector
You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?
1. Make sure your changes are passing unit and integration tests.
1. Bump the connector version in `Dockerfile` -- just increment the value of the `LABEL io.airbyte.version` appropriately (we use [SemVer](https://semver.org/)).
1. Create a Pull Request.
1. Pat yourself on the back for being an awesome contributor.
1. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.
