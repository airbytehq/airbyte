# MongoDb Source

## Documentation
This is the repository for the MongoDb source connector in Java.
For information about how to use this connector within Airbyte, see [User Documentation](https://docs.airbyte.io/integrations/sources/mongodb-v2)

## Local development

#### Building via Gradle
From the Airbyte repository root, run:
```
./gradlew :airbyte-integrations:connectors:source-mongodb-v2:build
```

### Locally running the connector docker image

#### Build
Build the connector image via Gradle:
```
./gradlew :airbyte-integrations:connectors:source-mongodb-v2:airbyteDocker
```
When building via Gradle, the docker image name and tag, respectively, are the values of the `io.airbyte.name` and `io.airbyte.version` `LABEL`s in
the Dockerfile.

## Testing
We use `JUnit` for Java tests.

### Test Configuration
No specific configuration needed for testing, MongoDb Test Container is used.

#### Acceptance Tests
To run acceptance and custom integration tests:
```
./gradlew :airbyte-integrations:connectors:source-mongodb-v2:integrationTest
```
