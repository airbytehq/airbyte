# End-to-End Testing Destination

This is the repository for the Null destination connector in Java. For information about how to use this connector within Airbyte, see [the User Documentation](https://docs.airbyte.io/integrations/destinations/e2e-test).

## Local development

#### Building via Gradle
From the Airbyte repository root, run:
```
./gradlew :airbyte-integrations:connectors:destination-e2e-test:build
```

#### Create credentials
No credential is needed for this connector.

### Locally running the connector docker image

#### Build
Build the connector image via Gradle:
```
./gradlew :airbyte-integrations:connectors:destination-e2e-test:airbyteDocker
```
When building via Gradle, the docker image name and tag, respectively, are the values of the `io.airbyte.name` and `io.airbyte.version` `LABEL`s in
the Dockerfile.

#### Run
Then run any of the connector commands as follows:
```
docker run --rm airbyte/destination-e2e-test:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/destination-e2e-test:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/destination-e2e-test:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/destination-e2e-test:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

#### Cloud variant
The cloud variant of this connector is Dev Null Destination. It only allows the "silent" mode. When this mode is changed, please make sure that the Dev Null Destination is updated and published accordingly as well.

## Testing
We use `JUnit` for Java tests.

### Unit and Integration Tests
Place unit tests under `src/test/io/airbyte/integrations/destinations/e2e-test`.

#### Acceptance Tests
Airbyte has a standard test suite that all destination connectors must pass. See example(s) in
`src/test-integration/java/io/airbyte/integrations/destinations/e2e-test/`.

### Using gradle to run tests
All commands should be run from airbyte project root.
To run unit tests:
```
./gradlew :airbyte-integrations:connectors:destination-e2e-test:unitTest
```
To run acceptance and custom integration tests:
```
./gradlew :airbyte-integrations:connectors:destination-e2e-test:integrationTest
```

## Dependency Management

### Publishing a new version of the connector
You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?
1. Make sure your changes are passing unit and integration tests.
2. Bump the connector version in `Dockerfile` -- just increment the value of the `LABEL io.airbyte.version` appropriately (we use [SemVer](https://semver.org/)).
3. Create a Pull Request.
4. Pat yourself on the back for being an awesome contributor.
5. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.
