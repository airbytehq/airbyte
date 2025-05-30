# Source TiDB

This is the repository for the TiDB source connector in Java.
For information about how to use this connector within Airbyte, see [the User Documentation](https://docs.airbyte.io/integrations/sources/tidb).

## Local development

#### Building via Gradle

From the Airbyte repository root, run:

```
./gradlew :airbyte-integrations:connectors:source-tidb:build
```

#### Create credentials

**If you are a community contributor**, generate the necessary credentials and place them in `secrets/config.json` conforming to the spec file in `src/main/resources/spec.json`.
Note that the `secrets` directory is git-ignored by default, so there is no danger of accidentally checking in sensitive information.

**If you are an Airbyte core member**, follow the [instructions](https://docs.airbyte.io/connector-development#using-credentials-in-ci) to set up the credentials.

### Locally running the connector docker image

#### Build

Build the connector image via Gradle:

```
./gradlew :airbyte-integrations:connectors:source-tidb:buildConnectorImage
```

Once built, the docker image name and tag on your host will be `airbyte/source-tidb:dev`.
the Dockerfile.

#### Run

Then run any of the connector commands as follows:

```
docker run --rm airbyte/source-tidb:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-tidb:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-tidb:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-tidb:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

## Testing

We use `JUnit` for Java tests.

### Unit and Integration Tests

Place unit tests under `src/test/...`
Place integration tests in `src/test-integration/...`

#### Acceptance Tests

Airbyte has a standard test suite that all source connectors must pass. Implement the `TODO`s in
`src/test-integration/java/io/airbyte/integrations/sources/TiDBSourceAcceptanceTest.java`.

### Using gradle to run tests

All commands should be run from airbyte project root.
To run unit tests:

```
./gradlew :airbyte-integrations:connectors:source-tidb:unitTest
```

To run acceptance and custom integration tests:

```
./gradlew :airbyte-integrations:connectors:source-tidb:integrationTest
```

## Dependency Management

### Publishing a new version of the connector

You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?

1. Make sure your changes are passing our test suite: `airbyte-ci connectors --name=source-tidb test`
2. Bump the connector version in `metadata.yaml`: increment the `dockerImageTag` value. Please follow [semantic versioning for connectors](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#semantic-versioning-for-connectors).
3. Make sure the `metadata.yaml` content is up to date.
4. Make the connector documentation and its changelog is up to date (`docs/integrations/sources/tidb.md`).
5. Create a Pull Request: use [our PR naming conventions](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#pull-request-title-convention).
6. Pat yourself on the back for being an awesome contributor.
7. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.
