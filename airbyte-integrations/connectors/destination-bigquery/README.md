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
./gradlew :airbyte-integrations:connectors:destination-bigquery:airbyteDocker
```
When building via Gradle, the docker image name and tag, respectively, are the values of the `io.airbyte.name` and `io.airbyte.version` `LABEL`s in
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
1. Make sure your changes are passing unit and integration tests.
1. Bump the connector version in `Dockerfile` -- just increment the value of the `LABEL io.airbyte.version` appropriately (we use [SemVer](https://semver.org/)).
1. Create a Pull Request.
1. Pat yourself on the back for being an awesome contributor.
1. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.

## Uploading options
There are 2 available options to upload data to bigquery `Standard` and `GCS Staging`.
- `Standard` is option to upload data directly from your source to BigQuery storage. This way is faster and requires less resources than GCS one.
Please be aware you may see some fails for big datasets and slow sources, i.e. if reading from source takes more than 10-12 hours. 
It may happen if you have a slow connection to source and\or migrate a very big dataset. If that's a case, then select a GCS Uploading type.
This is caused by the Google BigQuery SDK client limitations. For more details please check https://github.com/airbytehq/airbyte/issues/3549
- `GCS Uploading (CSV format)`. This approach has been implemented in order to avoid the issue for big datasets mentioned above.
At the first step all data is uploaded to GCS bucket and then all moved to BigQuery at one shot stream by stream.
The destination-gcs connector is partially used under the hood here, so you may check its documentation for more details.
There is no sense to use this uploading method if your migration doesn't take more than 10 hours and if you don't see the error like this in logs: 
<!-- markdown-link-check-disable -->
"PUT https://www.googleapis.com/upload/bigquery/v2/projects/some-project-name/jobs?uploadType=resumable&upload_id=some_randomly_generated_upload_id".
<!-- markdown-link-check-enable -->

# BigQuery Test Configuration

In order to test the BigQuery destination, you need a service account key file.

## Community Contributor

Follow the setup guide in the [docs](https://docs.airbyte.io/integrations/destinations/bigquery) to obtain credentials.

## Airbyte Employee

1. Access the `BigQuery Integration Test User` secret on Lastpass under the `Engineering` folder
1. Create a file with the contents at `secrets/credentials.json`
