# Build and run the Starburst Galaxy destination

This is the repository for the Starburst Galaxy destination connector, written in Java.
For information about how to use this connector within Airbyte, see [the user documentation](https://docs.airbyte.com/integrations/destinations/starburst-galaxy).

## Local development

#### Build with Gradle

From the Airbyte repository root, run:
```
./gradlew :airbyte-integrations:connectors:destination-starburst-galaxy:build
```

#### Create credentials

If you are a community contributor, you must generate the necessary credentials and place them in `secrets/config.json`, conforming to the spec file in `src/main/resources/spec.json`.
**Note**: The `secrets` directory is git-ignored by default; sensitive information cannot be checked in.

If you are an Airbyte core member, you must follow the [instructions](https://docs.airbyte.com/connector-development#using-credentials-in-ci) to set up your credentials.

### Build and run a local Docker image for the connector

#### Build

Build the connector image with Gradle:
```
./gradlew :airbyte-integrations:connectors:destination-starburst-galaxy:airbyteDocker
```
When building with Gradle, the Docker image name and tag, respectively, are the values of the `io.airbyte.name` and `io.airbyte.version` labels in
the Dockerfile.

#### Run

Following example commands are Starburst Galaxy-specific version of the [Airbyte protocol commands](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol):  
```
docker run --rm airbyte/destination-starburst-galaxy:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/destination-starburst-galaxy:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/destination-starburst-galaxy:dev write --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

### Run tests with Gradle

All commands should be run from airbyte project root. 

To run unit tests:
```
./gradlew :airbyte-integrations:connectors:destination-starburst-galaxy:unitTest
```
To run acceptance and custom integration tests:
```
./gradlew :airbyte-integrations:connectors:destination-starburst-galaxy:integrationTest
```

## Dependency management

### Publish a new version of the connector

After you have implemented a feature, bug fix or enhancement, you must do the following:

1. Ensure all unit and integration tests pass.
2. Update the connector version by incrementing the value of the `io.airbyte.version` label in the Dockerfile by following the [SemVer](https://semver.org/) versioning rules.
3. Create a Pull Request.

Airbyte will review your PR and request any changes necessary to merge it into master.