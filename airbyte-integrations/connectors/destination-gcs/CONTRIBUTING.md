# destination-gcs: Contributor notes

## Test configuration

To run integration tests, you need a Google Cloud Storage bucket and HMAC credentials with read and write permissions.

If you're a community contributor:

1. Create a GCS bucket for testing.
2. Generate an HMAC key for the bucket. The connector currently supports HMAC credentials for these tests.
3. Copy the bucket and key information into the config files under `sample_secrets`.
4. Rename `sample_secrets` to `secrets`.
5. You can modify the format config used by acceptance tests, such as `GcsCsvDestinationAcceptanceTest.getFormatConfig`, as long as the config follows `src/main/resources/spec.json`.

If you're an Airbyte employee:

1. Get `SECRET_DESTINATION-GCS__CREDS` from Secret Manager and put it in `sample_secrets/config.json`.
2. Get `SECRET_DESTINATION-GCS_NO_MULTIPART_ROLE_CREDS` from Secret Manager and put it in `sample_secrets/insufficient_roles_config.json`.
3. Rename `sample_secrets` to `secrets`.

## GCP service accounts for testing

Two shared service accounts exist for destination integration tests. Both use HMAC keys, and the keys are stored with the connector integration test credentials.

`gcs-destination-connector-test@dataline-integration-testing.iam.gserviceaccount.com` has the permissions needed to pass integration tests.

Role: `GCS Destination User`

```text
storage.multipartUploads.abort
storage.multipartUploads.create
storage.objects.create
storage.objects.delete
storage.objects.get
storage.objects.list
```

LastPass entry: `destination gcs creds`

`gcs-destination-failure-test@dataline-integration-testing.iam.gserviceaccount.com` does not have `storage.multipartUploads` permissions. Use it to test that `check` detects missing multipart permissions and returns an error.

Role: `GCS Destination User Without Multipart Permission`

```text
storage.objects.create
storage.objects.delete
storage.objects.get
storage.objects.list
```

LastPass entry: `destination gcs creds (no multipart permission)`

## Adding an output format

To add a new output format:

1. Add an enum value in `S3Format`.
2. Update `spec.json` with the new format configuration.
3. Update `S3FormatConfigs` so it can construct the new format config.
4. Create a package under `io.airbyte.integrations.destination.gcs`.
5. Implement a new `GcsWriter`.
6. Add an acceptance test for the new format. The test can extend `GcsDestinationAcceptanceTest`.
