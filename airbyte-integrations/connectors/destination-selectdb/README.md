# Destination Selectdb

This is the repository for the Selectdb destination connector in Java.
For information about how to use this connector within Airbyte, see [the User Documentation](https://docs.airbyte.com/integrations/destinations/selectdb).

## Local development

#### Building via Gradle
From the Airbyte repository root, run:
```
./gradlew :airbyte-integrations:connectors:destination-selectdb:build
```

#### Create credentials
**If you are a community contributor**, generate the necessary credentials and place them in `secrets/config.json` conforming to the spec file in `src/main/resources/spec.json`.
Note that the `secrets` directory is git-ignored by default, so there is no danger of accidentally checking in sensitive information.

**If you are an Airbyte core member**, follow the [instructions](https://docs.airbyte.com/connector-development#using-credentials-in-ci) to set up the credentials.

### Locally running the connector docker image

#### Build
Build the connector image via Gradle:
```
./gradlew :airbyte-integrations:connectors:destination-selectdb:airbyteDocker
```
When building via Gradle, the docker image name and tag, respectively, are the values of the `io.airbyte.name` and `io.airbyte.version` `LABEL`s in
the Dockerfile.

#### Run
Then run any of the connector commands as follows:
```
docker run --rm airbyte/destination-selectdb:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/destination-selectdb:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/destination-selectdb:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/destination-selectdb:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

## Testing
We use `JUnit` for Java tests.

### Unit and Integration Tests
Place unit tests under `src/test/io/airbyte/integrations/destinations/selectdb`.

#### Acceptance Tests
Airbyte has a standard test suite that all destination connectors must pass. Implement the `TODO`s in
`src/test-integration/java/io/airbyte/integrations/destinations/selectdbDestinationAcceptanceTest.java`.

### Using gradle to run tests
All commands should be run from airbyte project root.
To run unit tests:
```
./gradlew :airbyte-integrations:connectors:destination-selectdb:unitTest
```
To run acceptance and custom integration tests:
```
./gradlew :airbyte-integrations:connectors:destination-selectdb:integrationTest
```

## Dependency Management

### Publishing a new version of the connector
You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?
1. Make sure your changes are passing unit and integration tests.
1. Bump the connector version in `Dockerfile` -- just increment the value of the `LABEL io.airbyte.version` appropriately (we use [SemVer](https://semver.org/)).
1. Create a Pull Request.
1. Pat yourself on the back for being an awesome contributor.
1. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.
