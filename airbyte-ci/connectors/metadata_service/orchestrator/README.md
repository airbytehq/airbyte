# Connector Orchestrator

This is the Orchestrator for Airbyte metadata built on Dagster.

# Setup

## Installation

Metadata Orchestrator uses Poetry as dependency manager and build system. The guide below
assumes you have Poetry installed.

```bash
poetry install
cp .env.template .env
```

## Create a GCP Service Account and Dev Bucket

Developing against the orchestrator requires a development bucket in GCP.

The orchestrator will use this bucket to:

- store important output files. (e.g. Reports)
- watch for changes to the `registry` directory in the bucket.

However all tmp files will be stored in a local directory.

To create a development bucket:

1. Create a GCP Service Account with the following permissions:
   - Storage Admin
   - Storage Object Admin
   - Storage Object Creator
   - Storage Object Viewer
2. Create a PUBLIC GCS bucket
3. Add the service account as a member of the bucket with the following permissions:

   - Storage Admin
   - Storage Object Admin
   - Storage Object Creator
   - Storage Object Viewer

4. Add the following environment variables to your `.env` file:
   - `METADATA_BUCKET`
   - `GCS_CREDENTIALS`

Note that the `GCS_CREDENTIALS` should be the raw json string of the service account credentials.

Here is an example of how to import the service account credentials into your environment:

```bash
export GCS_CREDENTIALS=`cat /path/to/credentials.json`
```

## The Orchestrator

The orchestrator (built using Dagster) is responsible for orchestrating various the metadata
processes.

Dagster has a number of concepts that are important to understand before working on the
orchestrator.

1. Assets
2. Resources
3. Schedules
4. Sensors
5. Ops

Refer to the [Dagster documentation](https://docs.dagster.io/concepts) for more information on these
concepts.

### Starting the Dagster Daemons

Start the orchestrator with the following command:

```bash
poetry run dagster dev
```

Then you can access the Dagster UI at http://localhost:3000

Note its important to use `dagster dev` instead of `dagit` because `dagster dev` start additional
services that are required for the orchestrator to run. Namely the sensor service.

### Materializing Assets with the UI

When you navigate to the orchestrator in the UI, you will see a list of assets that are available to
be materialized.

From here you have the following options

1. Materialize all assets
2. Select a subset of assets to materialize
3. Enable a sensor to automatically materialize assets

### Materializing Assets without the UI

In some cases you may want to run the orchestrator without the UI. To learn more about Dagster's CLI
commands, see the [Dagster CLI documentation](https://docs.dagster.io/_apidocs/cli).

## Running Tests

```bash
poetry run pytest
```

## Deploying to Dagster Automatically

GitHub Actions is used to automatically deploy the orchestrator to Dagster Cloud
([Github Action](https://github.com/airbytehq/airbyte/blob/master/.github/workflows/metadata_service_deploy_orchestrator_dagger.yml)).

1. Update the version of your code (`../lib`) and update the version of the package in
   `pyproject.toml`
1. In this project (`../orchestrator`) Run `poetry lock --no-update` to bump the version of the
   requirements you may have changed in
   `airbyte-ci/connectors/metadata_service/orchestrator/poetry.lock`
1. Push your changes to the `master` branch and the orchestrator will be automatically deployed to
   Dagster Cloud.

## Deploying to Dagster Cloud manually

This should only be needed if the above (automatic deployment) fails.

### Installing the dagster-cloud cli

```bash
pip install dagster-cloud
dagster-cloud config
```

### Deploying the orchestrator

```bash
cd orchestrator
DAGSTER_CLOUD_API_TOKEN=<YOU-DAGSTER-CLOUD-TOKEN> airbyte-ci metadata deploy orchestrator
```

# Using the Orchestrator to create a Connector Registry for Development

The orchestrator can be used to create a connector registry for development purposes.

## Setup

First you will need to setup the orchestrator as described above.

Then you will want to do the following

### 1. Mirror the production bucket

Use the Google Cloud Console to mirror the production bucket
(prod-airbyte-cloud-connector-metadata-service) to your development bucket.

[Docs](https://cloud.google.com/storage-transfer/docs/cloud-storage-to-cloud-storage)

### 2. Upload any local metadata files you want to test changes with

```bash
# assuming your terminal is in the same location as this readme
cd ../lib
export GCS_CREDENTIALS=`cat /path/to/gcs_credentials.json`
poetry run metadata_service upload <PATH TO METADATA FILE> <NAME OF YOUR BUCKET>
```

### 3. Generate the registry

```bash
poetry run dagster dev
open http://localhost:3000
```

And run the `generate_registry` job

## Additional Notes
### How to publish to Dagster Cloud Dev
Pre-requisites:
- You need to have `airbyte-ci` installed. You can install it by running `make tools.airbyte-ci-dev.install` from the root of the repository.
- You need to have the `DAGSTER_CLOUD_METADATA_API_TOKEN` environment variable set to an API token from the Airbyte Dagster Cloud account.

```sh
DAGSTER_CLOUD_METADATA_API_TOKEN=<SECRET> DAGSTER_CLOUD_DEPLOYMENT="dev" airbyte-ci metadata deploy orchestrator
```

### Testing Slack Notifications
You will need to add the following environment variables to your `.env` file:

- `SLACK_TOKEN`: Set to an OAuth token for the [Connector Ops Dagster Bot](https://airbytehq-team.slack.com/apps/A05K845HBE0-connector-ops-dagster-bot?settings=1)
- `PUBLISH_UPDATE_CHANNEL`: Set to `#test-ci-slack-intergrations`
- `SLACK_NOTIFICATIONS_DISABLED`: Set to `False`
