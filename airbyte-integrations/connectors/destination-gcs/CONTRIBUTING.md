# destination-gcs: Contributor notes

## Test configuration

You can modify the format config used by acceptance tests, such as `GcsCsvDestinationAcceptanceTest.getFormatConfig`, as long as the config follows `src/main/resources/spec.json`.

The test suite includes an insufficient-role configuration that omits `storage.multipartUploads` permissions so `check` can validate multipart permission failures.

## Adding an output format

To add a new output format:

1. Add an enum value in `S3Format`.
2. Update `spec.json` with the new format configuration.
3. Update `S3FormatConfigs` so it can construct the new format config.
4. Create a package under `io.airbyte.integrations.destination.gcs`.
5. Implement a new `GcsWriter`.
6. Add an acceptance test for the new format. The test can extend `GcsDestinationAcceptanceTest`.
