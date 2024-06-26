# Destination Google Cloud Storage (GCS)

In order to test the D3 destination, you need an Google Cloud Platform account.

## Community Contributor

As a community contributor, you can follow these steps to run integration tests.

- Create an GCS bucket for testing.
- Generate a [HMAC key](https://cloud.google.com/storage/docs/authentication/hmackeys) for the bucket with reading and writing permissions. Please note that currently only the HMAC key credential is supported. More credential types will be added in the future.
- Paste the bucket and key information into the config files under [`./sample_secrets`](./sample_secrets).
- Rename the directory from `sample_secrets` to `secrets`.
- Feel free to modify the config files with different settings in the acceptance test file (e.g. `GcsCsvDestinationAcceptanceTest.java`, method `getFormatConfig`), as long as they follow the schema defined in [spec.json](src/main/resources/spec.json).

## Airbyte Employee

- Access the `SECRET_DESTINATION-GCS__CREDS` secrets on SecretManager, and put it in `sample_secrets/config.json`.
  \_ Access the `SECRET_DESTINATION-GCS_NO_MULTIPART_ROLE_CREDS` secrets on SecretManager, and put it in `sample_secrets/insufficient_roles_config.json`.
- Rename the directory from `sample_secrets` to `secrets`.

### GCP Service Account for Testing

Two service accounts have been created in our GCP for testing this destination. Both of them have access to Cloud Storage through HMAC keys. The keys are persisted together with the connector integration test credentials in LastPass.

- Account: `gcs-destination-connector-test@dataline-integration-testing.iam.gserviceaccount.com`

  - This account has the required permission to pass the integration test. Note that the uploader needs `storage.multipartUploads` permissions, which may not be intuitive.
  - Role: `GCS Destination User`
    - Permissions:
      ```
      storage.multipartUploads.abort
      storage.multipartUploads.create
      storage.objects.create
      storage.objects.delete
      storage.objects.get
      storage.objects.list
      ```
  - LastPass entry: `destination gcs creds`

- Account: `gcs-destination-failure-test@dataline-integration-testing.iam.gserviceaccount.com`
  - This account does not have the `storage.multipartUploads` permissions, and will fail the integration test. The purpose of this account is to test that the `check` command can correctly detect the lack of these permissions and return an error message.
  - Role: `GCS Destination User Without Multipart Permission`
    - Permissions:
      ```
      storage.objects.create
      storage.objects.delete
      storage.objects.get
      storage.objects.list
      ```
  - LastPass entry: `destination gcs creds (no multipart permission)`

## Add New Output Format

- Add a new enum in `S3Format`.
- Modify `spec.json` to specify the configuration of this new format.
- Update `S3FormatConfigs` to be able to construct a config for this new format.
- Create a new package under `io.airbyte.integrations.destination.gcs`.
- Implement a new `GcsWriter`. The implementation can extend `BaseGcsWriter`.
- Write an acceptance test for the new output format. The test can extend `GcsDestinationAcceptanceTest`.
