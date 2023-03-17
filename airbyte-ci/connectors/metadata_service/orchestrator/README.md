# Connector Orchestrator (WIP)
This is the Orchestrator for Airbyte metadata built on Dagster.


# Setup

## Prerequisites

#### Poetry

Before you can start working on this project, you will need to have Poetry installed on your system. Please follow the instructions below to install Poetry:

1. Open your terminal or command prompt.
2. Install Poetry using the recommended installation method:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Alternatively, you can use `pip` to install Poetry:

```bash
pip install --user poetry
```

3. After the installation is complete, close and reopen your terminal to ensure the newly installed `poetry` command is available in your system's PATH.

For more detailed instructions and alternative installation methods, please refer to the official Poetry documentation: https://python-poetry.org/docs/#installation

### Using Poetry in the Project

Once Poetry is installed, you can use it to manage the project's dependencies and virtual environment. To get started, navigate to the project's root directory in your terminal and follow these steps:


## Installation
```bash
poetry install
cp .env.template .env
```

## Create a GCP Service Account and Dev Bucket
Developing against the orchestrator requires a development bucket in GCP.

The orchestrator will use this bucket to:
- store important output files. (e.g. Reports)
- watch for changes to the `catalog` directory in the bucket.

However all tmp files will be stored in a local directory.

To create a development bucket:
1. Create a GCP Service Account with the following permissions:
    - Storage Admin
    - Storage Object Admin
    - Storage Object Creator
    - Storage Object Viewer
2. Create a GCS bucket
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

The orchestrator (built using Dagster) is responsible for orchestrating various the metadata processes.

Dagster has a number of concepts that are important to understand before working on the orchestrator.
1. Assets
2. Resources
3. Schedules
4. Sensors
5. Ops

Refer to the [Dagster documentation](https://docs.dagster.io/concepts) for more information on these concepts.

### Starting the Dagster Daemons
Start the orchestrator with the following command:
```bash
poetry run dagster dev -m orchestrator
```

Then you can access the Dagster UI at http://localhost:3000

Note its important to use `dagster dev` instead of `dagit` because `dagster dev` start additional services that are required for the orchestrator to run. Namely the sensor service.

### Materializing Assets with the UI
When you navigate to the orchestrator in the UI, you will see a list of assets that are available to be materialized.

From here you have the following options
1. Materialize all assets
2. Select a subset of assets to materialize
3. Enable a sensor to automatically materialize assets

### Materializing Assets without the UI

In some cases you may want to run the orchestrator without the UI. To learn more about Dagster's CLI commands, see the [Dagster CLI documentation](https://docs.dagster.io/_apidocs/cli).

## Running Tests
```bash
poetry run pytest
```

