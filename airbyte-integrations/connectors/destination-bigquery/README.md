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

As a community contributor, you will need access to a GCP project and BigQuery to run tests.

1. Go to the `Service Accounts` page on the GCP console
1. Click on `+ Create Service Account" button
1. Fill out a descriptive name/id/description
1. Click the edit icon next to the service account you created on the `IAM` page
1. Add the `BigQuery Data Editor`, `BigQuery User` and `GCS User` roles. For more details check https://cloud.google.com/storage/docs/access-control/iam-roles
1. Go back to the `Service Accounts` page and use the actions modal to `Create Key`
1. Download this key as a JSON file
1. Create an GCS bucket for testing.
1. Generate a [HMAC key](https://cloud.google.com/storage/docs/authentication/hmackeys) for the bucket with reading and writing permissions. Please note that currently only the HMAC key credential is supported. More credential types will be added in the future.
1. Paste the bucket and key information into the config files under [`./sample_secret`](./sample_secret).
1. Rename the directory from `sample_secret` to `secrets`.
1. Feel free to modify the config files with different settings in the acceptance test file as long as they follow the schema defined in [spec.json](src/main/resources/spec.json).
1. Move and rename this file to `secrets/credentials.json`

## Airbyte Employee

1. Access the `BigQuery Integration Test User` secret on Rippling under the `Engineering` folder
1. Create a file with the contents at `secrets/credentials.json`
