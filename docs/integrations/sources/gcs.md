# GCS

This page guides you through the process of setting up the GCS source connector. This connector supports loading multiple CSV files (non compressed) from a GCS directory. The conntector will check for all files ending in `.csv`, even nested files.

## Prerequisites

* JSON credentials for the service account that has access to GCS. For more details check [instructions](https://cloud.google.com/iam/docs/creating-managing-service-accounts)
* GCS bucket
* Path to file(s)

## Set up Source

### Create a Service Account

First, you need to select existing or create a new project in the Google Cloud Console:

1. Sign in to the Google Account.
2. Go to the [Service Accounts](https://console.developers.google.com/iam-admin/serviceaccounts) page.
3. Click `Create service account`.
4. Create a JSON key file for the service user. The contents of this file will be provided as the `service_account` in the UI.

### Grant permisison to GCS

Use the service account ID from above, grant read access to your target bucket. Click [here](https://cloud.google.com/storage/docs/access-control/using-iam-permissions) for more details.

### Set up the source in Airbyte UI

* Paste the service account JSON key to `service_account`
* Enter your GCS bucket name to `gcs_bucket`
* Enter path to your file(s) to `gcs_path`

## Changelog
| Version | Date       | Pull Request                                             | Subject                     |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------- |
| 0.1.0   | 2023-02-16 | [23186](https://github.com/airbytehq/airbyte/pull/23186) | New Source: GCS             |
