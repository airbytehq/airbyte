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

### Acceptance Tests
To run acceptance and custom integration tests:
```
./gradlew :airbyte-integrations:connectors:source-mysql:integrationTest
```

### Performance Tests

To run performance tests in commandline:
```shell
./gradlew :airbyte-integrations:connectors:source-mysql:performanceTest [--cpulimit=cpulimit/<limit>] [--memorylimit=memorylimit/<limit>]
```

In pull request:
```shell
/test-performance connector=connectors/source-mysql [--cpulimit=cpulimit/<limit>] [--memorylimit=memorylimit/<limit>]
```

- `cpulimit`: Limit the number of CPUs. The minimum is `2`. E.g. `--cpulimit=cpulimit/2`.
- `memorylimit`: Limit the size of the memory. Must include the unit at the end (e.g. `MB`, `GB`). The minimum size is `6MB`. E.g. `--memorylimit=memorylimit/4GB`.
- When none of the CPU or memory limit is provided, the performance tests will run without memory or CPU limitations. The available resource will be bound that those specified in `ResourceRequirements.java`.

#### Use MySQL script to populate the benchmark database

In order to create a database with a certain number of tables, and a certain number of records in each of them,
you need to follow a few simple steps.

1. Create a new database.
2. Follow the TODOs in [create_mysql_benchmarks.sql](src/test-performance/sql/create_mysql_benchmarks.sql) to change the number of tables, and the number of records of different sizes.
3. Execute the script with your changes for the new database. You can run the script using the MySQL command line client:
   ```shell
   cd airbyte-integrations/connectors/source-mysql
   mysql -h hostname -u user database < src/test-performance/sql/create_mysql_benchmarks.sql
   ```   
4. After the script finishes its work, you will receive the number of tables specified in the script, with names starting with **test_0** and ending with **test_(the number of tables minus 1)**.
