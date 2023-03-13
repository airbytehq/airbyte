# Connector Orchestrator (WIP)
This is the Orchestrator for Airbyte metadata built on Dagster.


# Setup
## Local
All commands below assume you are in the `metadata_service/orchestrator` directory.
### Installation
```bash
poetry install
cp .env.template .env
```

### Create a GCP Service Account and Dev Bucket
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
    - `GCP_GSM_CREDENTIALS`

Note that the `GCP_GSM_CREDENTIALS` should be the raw json string of the service account credentials.

Here is an example of how to import the service account credentials into your environment:
```bash
export GCP_GSM_CREDENTIALS=`cat /path/to/credentials.json`
```

### Running
Start the orchestrator with the following command:
```bash
poetry run dagster dev -m orchestrator
```

Then you can access the dagit UI at http://localhost:3000

Note its important to use `dagster dev` instead of `dagit` because `dagster dev` start additional services that are required for the orchestrator to run. Namely the sensor service.


# WIP Notes

### possible ways to build this
https://github.com/slopp/dagster-dynamic-partitions/blob/cf312590bb3a2d95caee670433f00a7f20ddb50c/build/lib/dagster_project/definitions.py
https://github.com/mitodl/ol-data-platform/blob/59b785ab6bd5d73a05d598c9b39bfc8fa4eec65c/src/ol_orchestrate/repositories/edx_gcs_courses.py
https://github.com/dagster-io/dagster/tree/c607767076da21de66ac364f1501c4ed49c20b49/examples/project_fully_featured
https://github.com/DataBiosphere/hca-ingest/blob/61601a7830e224ac5f30c13bf0d605768f97d418/orchestration/hca_orchestration/repositories/common.py

### good way to restructure this
https://www.youtube.com/watch?v=ZmUjf3gL1VU
