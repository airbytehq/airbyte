# Azure Blob Storage Test Configuration

In order to test the Azure Blob Storage destination, you need a Microsoft account.

## Community Contributor

As a community contributor, you will need access to Azure to run the integration tests.

- Create an AzureBlobStorage account for testing. Check if it works under https://portal.azure.com/ -> "Storage explorer (preview)".
- Get your `azure_blob_storage_account_name` and `azure_blob_storage_account_key` that can read and write to the Azure Container.
- Paste the accountName and key information into the config files under [`./sample_secrets`](./sample_secrets).
- Rename the directory from `sample_secrets` to `secrets`.
- Feel free to modify the config files with different settings in the acceptance test file (e.g. `AzureBlobStorageJsonlDestinationAcceptanceTest.java`, method `getFormatConfig`), as long as they follow the schema defined in [spec.json](src/main/resources/spec.json).

## Airbyte Employee
- Access the `Azure Blob Storage Account` secrets on Last Pass.
- Replace the `config.json` under `sample_secrets`.
- Rename the directory from `sample_secrets` to `secrets`.

## Add New Output Format
- Add a new enum in `AzureBlobStorageFormat'.
- Modify `spec.json` to specify the configuration of this new format.
- Update `AzureBlobStorageFormatConfigs` to be able to construct a config for this new format.
- Create a new package under `io.airbyte.integrations.destination.azure_blob_storage`.
- Implement a new `AzureBlobStorageWriter`. The implementation can extend `BaseAzureBlobStorageWriter`.
- Write an acceptance test for the new output format. The test can extend `AzureBlobStorageDestinationAcceptanceTest`.
