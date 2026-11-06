# destination-azure-blob-storage: Contributor notes

## Test configuration

You can modify the format config used by acceptance tests, such as `AzureBlobStorageJsonlDestinationAcceptanceTest.getFormatConfig`, as long as the config follows `src/main/resources/spec.json`.

## Adding an output format

To add a new output format:

1. Add an enum value in `AzureBlobStorageFormat`.
2. Update `spec.json` with the new format configuration.
3. Update `AzureBlobStorageFormatConfigs` so it can construct the new format config.
4. Create a package under `io.airbyte.integrations.destination.azure_blob_storage`.
5. Implement an `AzureBlobStorageWriter`. The writer can extend `BaseAzureBlobStorageWriter`.
6. Add an acceptance test for the new format. The test can extend `AzureBlobStorageDestinationAcceptanceTest`.
