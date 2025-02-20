# Microsoft SQL Server V2 (Bulk CDK) Destination

## Build

### airbyte-ci

To build the connector via the [Airbyte CI CLI tool](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md), navigate to the root of the [Airbyte repository](https://github.com/airbytehq/airbyte) and execute the following command:

```shell
> airbyte-ci connectors --name=destination-mssql-v2 build
```

###  Gradle

To build the connector via [Gradle](https://gradle.org/), navigate to the root of the [Airbyte repository](https://github.com/airbytehq/airbyte) and execute the following command:

```shell
> ./gradlew :airbyte-integrations:connectors:destination-mssql-v2:build
```
## Execute

### Local Execution via Docker

In order to run the connector image locally, first either build the connector's [Docker](https://www.docker.com/) image using the commands found
in this section of this document OR build the image using the following command:

```shell
> ./gradlew :airbyte-integrations:connectors:destination-mssql-v2:buildConnectorImage
```

The built image will automatically be tagged with the `dev` label.  To run the connector image, use the following commands:

```shell
docker run --rm airbyte/destination-mssql-v2:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/destination-mssql-v2:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/destination-mssql-v2:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/destination-mssql-v2:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

## Test

The connector contains both unit and acceptance tests which can each be executed from the local environment.  

### Unit Tests

The connector uses a combination of [Kotlin](https://kotlinlang.org/), [JUnit 5](https://junit.org/junit5/) and [MockK](https://mockk.io/)
to implement unit tests.  Existing tests can be found within the destination-mssql-v2 module in the conventional `src/test/kotlin` source folder.  New tests should also be added to this location.

The unit tests can be executed either via the [Airbyte CI CLI tool](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md) or [Gradle](https://gradle.org/):

###### Airbyte CI CLI
```shell
> airbyte-ci connectors --name=destination-mssql-v2 test
```

###### Gradle
```shell
> ./gradlew :airbyte-integrations:connectors:destination-mssql-v2:test
```

### Acceptance Tests

The [Airbyte project](https://github.com/airbytehq/airbyte) a standard test suite that all destination connectors must pass.  The tests require specific implementations of a few components in order to connect the acceptance test suite with the connector's specific logic.  The existing acceptance test scaffolding can be found in the conventional `src/test-integration/kotlin` source folder.  

The acceptance tests can be executed either via the [Airbyte CI CLI tool](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md) or [Gradle](https://gradle.org/):

###### Airbyte CI CLI
```shell
> airbyte-ci connectors --name=destination-mssql-v2 test
```

###### Gradle
```shell
> ./gradlew :airbyte-integrations:connectors:destination-mssql-v2:integrationTest
```

## Release

### Publishing a new version of the connector

You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?

1. Make sure your changes are passing our test suite: `airbyte-ci connectors --name=destination-mssql-v2 test`
2. Bump the connector version in `metadata.yaml`: increment the `dockerImageTag` value. Please follow [semantic versioning for connectors](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#semantic-versioning-for-connectors).
3. Make sure the `metadata.yaml` content is up to date.
4. Make the connector documentation and its changelog is up to date (`docs/integrations/destinations/mssql-v2.md`).
5. Create a Pull Request: use [our PR naming conventions](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#pull-request-title-convention).
6. Pat yourself on the back for being an awesome contributor.
7. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.


