# Destination Azure Service Bus

This is the repository for the Azure Service Bus destination connector in Java.

For information about how to use this connector within Airbyte, see [the User Documentation](https://docs.airbyte.com/integrations/destinations/azure-service-bus).

## Local development

#### Building via Gradle

From the Airbyte repository root, run:
```
./gradlew :airbyte-integrations:connectors:destination-azure-service-bus:build
```

### Locally running the connector docker image

#### Build
Build the connector image via Gradle:
```
./gradlew :airbyte-integrations:connectors:destination-azure-service-bus:airbyteDocker
```
When building via Gradle, the docker image name and tag, respectively, are the values of the `io.airbyte.name` and `io.airbyte.version` `LABEL`s in
the Dockerfile.

#### Run
Then run any of the connector commands as follows:
```
docker run --rm airbyte/destination-azure-service-bus:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/destination-azure-service-bus:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/destination-azure-service-bus:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/destination-azure-service-bus:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

### Using gradle to run tests
All commands should be run from airbyte project root.
To run unit tests:
```
./gradlew :airbyte-integrations:connectors:destination-azure-service-bus:test
```
To run acceptance and custom integration tests:
```
./gradlew :airbyte-integrations:connectors:destination-azure-service-bus:clean \
  :airbyte-integrations:connectors:destination-azure-service-bus:airbyteDocker --no-build-cache \
./gradlew :airbyte-integrations:connectors:destination-azure-service-bus:integrationTest
```

## Dependencies

The destination takes a low-deps approach, using only the relevant REST api endpoint, together with SAS signature auth.
