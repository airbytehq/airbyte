# Destination Databricks Lakehouse

This is the repository for the Databricks destination connector in Java.
For information about how to use this connector within Airbyte, see [the User Documentation](https://docs.airbyte.io/integrations/destinations/databricks).

## Databricks JDBC Driver
This connector requires a JDBC driver to connect to Databricks cluster. Before using this connector, you must agree to the [JDBC ODBC driver license](https://databricks.com/jdbc-odbc-driver-license). This means that you can only use this driver to connector third party applications to Apache Spark SQL within a Databricks offering using the ODBC and/or JDBC protocols.

## Local development

#### Building via Gradle
From the Airbyte repository root, run:
```
./gradlew :airbyte-integrations:connectors:destination-databricks:build
```

#### Create credentials
**If you are a community contributor**, you will need access to AWS S3, Azure blob storage, and Databricks cluster to run the integration tests:

- Create a Databricks cluster. See [documentation](https://docs.databricks.com/clusters/create.html).
- Create an S3 bucket. See [documentation](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys).
- Create an Azure storage container.
- Grant the Databricks cluster full access to the S3 bucket and Azure container. Or mount it as Databricks File System (DBFS). See [documentation](https://docs.databricks.com/data/data-sources/aws/amazon-s3.html).
- Place both Databricks and S3 credentials in `sample_secrets/config.json`, which conforms to the spec file in `src/main/resources/spec.json`.
- Place both Databricks and Azure credentials in `sample_secrets/azure_config.json`, which conforms to the spec file in `src/main/resources/spec.json`.
- Rename the directory from `sample_secrets` to `secrets`.
- Note that the `secrets` directory is git-ignored by default, so there is no danger of accidentally checking in sensitive information.

**If you are an Airbyte core member**:

- Get the `destination databricks creds` secrets on Last Pass, and put it in `sample_secrets/config.json`.
- Rename the directory from `sample_secrets` to `secrets`.

### Locally running the connector docker image

#### Build
Build the connector image via Gradle:
```
./gradlew :airbyte-integrations:connectors:destination-databricks:airbyteDocker
```
When building via Gradle, the docker image name and tag, respectively, are the values of the `io.airbyte.name` and `io.airbyte.version` `LABEL`s in
the Dockerfile.

#### Run
Then run any of the connector commands as follows:
```
docker run --rm airbyte/destination-databricks:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/destination-databricks:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/destination-databricks:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/destination-databricks:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

## Testing
We use `JUnit` for Java tests.

### Unit and Integration Tests
Place unit tests under `src/test/io/airbyte/integrations/destinations/databricks`.

#### Acceptance Tests
Airbyte has a standard test suite that all destination connectors must pass. Implement the `TODO`s in
`src/test-integration/java/io/airbyte/integrations/destinations/databricksDestinationAcceptanceTest.java`.

### Using gradle to run tests
All commands should be run from airbyte project root.
To run unit tests:
```
./gradlew :airbyte-integrations:connectors:destination-databricks:unitTest
```
To run acceptance and custom integration tests:
```
./gradlew :airbyte-integrations:connectors:destination-databricks:integrationTest
```

## Dependency Management

### Publishing a new version of the connector
You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?
1. Make sure your changes are passing unit and integration tests.
1. Bump the connector version in `Dockerfile` -- just increment the value of the `LABEL io.airbyte.version` appropriately (we use [SemVer](https://semver.org/)).
1. Create a Pull Request.
1. Pat yourself on the back for being an awesome contributor.
1. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.
