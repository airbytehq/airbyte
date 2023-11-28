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
./gradlew :airbyte-integrations:connectors:destination-dev-null:buildConnectorImage
```
Once built, the docker image name and tag on your host will be `airbyte/destination-dev-null:dev`.
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
1. Make sure your changes are passing our test suite: `airbyte-ci connectors --name=destination-dev-null test`
2. Bump the connector version in `metadata.yaml`: increment the `dockerImageTag` value. Please follow [semantic versioning for connectors](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#semantic-versioning-for-connectors).
3. Make sure the `metadata.yaml` content is up to date.
4. Make the connector documentation and its changelog is up to date (`docs/integrations/destinations/e2e-test.md`).
5. Create a Pull Request: use [our PR naming conventions](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#pull-request-title-convention).
6. Pat yourself on the back for being an awesome contributor.
7. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.

