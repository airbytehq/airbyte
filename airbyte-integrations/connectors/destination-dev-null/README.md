# Destination Dev Null

This destination is a "safe" version of the [E2E Test destination](https://docs.airbyte.io/integrations/destinations/e2e-test). It only allows the "silent" mode. 

## Local development

#### Building via Gradle
From the Airbyte repository root, run:
```
./gradlew :airbyte-integrations:connectors:destination-dev-null:build
```

### Locally running the connector docker image

#### Build
Build the connector image via Gradle:
```
./gradlew :airbyte-integrations:connectors:destination-dev-null:airbyteDocker
```
When building via Gradle, the docker image name and tag, respectively, are the values of the `io.airbyte.name` and `io.airbyte.version` `LABEL`s in
the Dockerfile.

#### Run
Then run any of the connector commands as follows:
```
docker run --rm airbyte/destination-dev-null:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/destination-dev-null:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/destination-dev-null:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/destination-dev-null:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

### Using gradle to run tests
All commands should be run from airbyte project root.
To run unit tests:
```
./gradlew :airbyte-integrations:connectors:destination-dev-null:unitTest
```
To run acceptance and custom integration tests:
```
./gradlew :airbyte-integrations:connectors:destination-dev-null:integrationTest
```

## Dependency Management

### Publishing a new version of the connector
You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?
1. Make sure your changes are passing unit and integration tests.
1. Bump the connector version in `Dockerfile` -- just increment the value of the `LABEL io.airbyte.version` appropriately (we use [SemVer](https://semver.org/)).
1. Create a Pull Request.
1. Pat yourself on the back for being an awesome contributor.
1. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.
