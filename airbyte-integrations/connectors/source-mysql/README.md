# MySQL Source

## Documentation
This is the repository for the MySQL only source connector in Java.
For information about how to use this connector within Airbyte, see [User Documentation](https://docs.airbyte.io/integrations/sources/mysql)

## Local development

#### Building via Gradle
From the Airbyte repository root, run:
```
./gradlew :airbyte-integrations:connectors:source-mysql:build
```

### Locally running the connector docker image

#### Build
Build the connector image via Gradle:
```
./gradlew :airbyte-integrations:connectors:source-mysql:airbyteDocker
```
When building via Gradle, the docker image name and tag, respectively, are the values of the `io.airbyte.name` and `io.airbyte.version` `LABEL`s in
the Dockerfile.

## Testing
We use `JUnit` for Java tests.

### Test Configuration
#### Acceptance Tests
To run acceptance and custom integration tests:
```
./gradlew :airbyte-integrations:connectors:source-mysql:integrationTest
```

#### Performance Tests
To run performance tests:
```
./gradlew :airbyte-integrations:connectors:source-mysql:performanceTest
```

### Use MySQL script to populate the benchmark database

In order to create a database with a certain number of tables, and a certain number of records in each of them,
you need to follow a few simple steps.

1. Create a new database.
2. Follow the TODOs in **mssql-script.sql** to change the number of tables, and the number of records of different sizes.
3. Execute the script with your changes for the new database.
   You can run the script use the MsSQL command line client: - **sqlcmd -S Serverinstance -E -i path/to/script/mssql-script.sql**
   After the script finishes its work, you will receive the number of tables specified in the script, with names starting with **test_0** and ending with **test_(the number of tables minus 1)**.


