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

No specific configuration needed for testing Standalone MongoDb instance, MongoDb Test Container is used.
In order to test the MongoDb Atlas or Replica set, you need to provide configuration parameters.

## Community Contributor

As a community contributor, you will need to have an Atlas cluster to test MongoDb source.

1. Create `secrets/credentials.json` file
   1. Insert below json to the file with your configuration
       ```
      {
         "database": "database_name",
         "user": "user",
         "password": "password",
         "cluster_url": "cluster_url"
       }
      ```

## Airbyte Employee

1. Access the `MONGODB_TEST_CREDS` secret on LastPass
1. Create a file with the contents at `secrets/credentials.json`


#### Acceptance Tests
To run acceptance and custom integration tests:
```
./gradlew :airbyte-integrations:connectors:source-mongodb-v2:integrationTest
```
