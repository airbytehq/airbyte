## Local development

#### Building via Gradle

From the Airbyte repository root, run:

```
./gradlew :airbyte-integrations:connectors:destination-bigquery:build
```

#### Create credentials

**If you are a community contributor**, generate the necessary credentials and place them in `secrets/config.json` conforming to the spec file in `src/main/resources/spec.json`.
Note that the `secrets` directory is git-ignored by default, so there is no danger of accidentally checking in sensitive information.

**If you are an Airbyte core member**, follow the [instructions](https://docs.airbyte.io/connector-development#using-credentials-in-ci) to set up the credentials.

### Locally running the connector docker image

#### Build

Build the connector image via Gradle:

```
./gradlew :airbyte-integrations:connectors:destination-bigquery:buildConnectorImage
```

Once built, the docker image name and tag on your host will be `airbyte/destination-bigquery:dev`.
the Dockerfile.

#### Run

Then run any of the connector commands as follows:

```
docker run --rm airbyte/destination-bigquery:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/destination-bigquery:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/destination-bigquery:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/destination-bigquery:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

## Testing

We use `JUnit` for Java tests.

### Unit and Integration Tests

Place unit tests under `src/test/io/airbyte/integrations/destinations/bigquery`.

#### Acceptance Tests

Airbyte has a standard test suite that all destination connectors must pass. Implement the `TODO`s in
`src/test-integration/java/io/airbyte/integrations/destinations/BigQueryDestinationAcceptanceTest.java`.

### Using gradle to run tests

All commands should be run from airbyte project root.
To run unit tests:

```
./gradlew :airbyte-integrations:connectors:destination-bigquery:unitTest
```

To run acceptance and custom integration tests:

```
./gradlew :airbyte-integrations:connectors:destination-bigquery:integrationTest
```

## Dependency Management

### Publishing a new version of the connector

You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?

1. Make sure your changes are passing our test suite: `airbyte-ci connectors --name=destination-bigquery test`
2. Bump the connector version in `metadata.yaml`: increment the `dockerImageTag` value. Please follow [semantic versioning for connectors](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#semantic-versioning-for-connectors).
3. Make sure the `metadata.yaml` content is up to date.
4. Make the connector documentation and its changelog is up to date (`docs/integrations/destinations/bigquery.md`).
5. Create a Pull Request: use [our PR naming conventions](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#pull-request-title-convention).
6. Pat yourself on the back for being an awesome contributor.
7. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.

## Managing BigQuery Permissions

Before testing the bigquery connector, add the necessary permissions using the following steps:

1. Create a service account using the Google Cloud console or use an existing account. To create a new service account, go to IAM & Admin -> Service Accounts in the left navigation menu and click the "CREATE SERVICE ACCOUNT" link

2. Create a customer permissions role using the Google Cloud console by using IAM & Admin -> Roles in the left navigation menu and click the "CREATE ROLE" link. Add the following permissions for the role:
 
   bigquery.datasets.create  
   bigquery.datasets.get  
   bigquery.jobs.create  
   bigquery.tables.create  
   bigquery.tables.delete  
   bigquery.tables.get  
   bigquery.tables.updateData  

3. Assign the custom role to the newly created service account from the Service Account page.

