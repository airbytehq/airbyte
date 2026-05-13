# destination-azure-blob-storage: Contributor notes

## Test configuration

To run integration tests, you need a Microsoft account and an Azure Blob Storage account with a container that the connector can read from and write to.

If you're a community contributor:

1. Create an Azure Blob Storage account for testing. You can verify it in the Azure portal under Storage explorer.
2. Create a container.
3. Copy the storage account name and access key into the config files under `sample_secrets`.
4. Rename `sample_secrets` to `secrets`.
5. You can modify the format config used by acceptance tests, such as `AzureBlobStorageJsonlDestinationAcceptanceTest.getFormatConfig`, as long as the config follows `src/main/resources/spec.json`.

If you're an Airbyte employee:

1. Access the `Azure Blob Storage Account` secret in LastPass.
2. Replace `sample_secrets/config.json`.
3. Rename `sample_secrets` to `secrets`.

## Azure test infrastructure

To create or refresh the shared Azure test resources:

1. Log in to the Azure portal with the `integration-test@airbyte.io` account.
2. Open Storage Accounts.
3. Create a storage account under the `integration-test-rg` resource group. The current shared account is `airbyteteststorage`.
4. Choose Locally-redundant storage (LRS) for redundancy.
5. Open the storage account and create a container. The current shared container is `airbytetescontainername`.
6. Open Access keys on the storage account. Use the first key for `azure_blob_storage_account_key`.

The tests do not require alternating between the two Azure access keys.

## Adding an output format

To add a new output format:

1. Add an enum value in `AzureBlobStorageFormat`.
2. Update `spec.json` with the new format configuration.
3. Update `AzureBlobStorageFormatConfigs` so it can construct the new format config.
4. Create a package under `io.airbyte.integrations.destination.azure_blob_storage`.
5. Implement an `AzureBlobStorageWriter`. The writer can extend `BaseAzureBlobStorageWriter`.
6. Add an acceptance test for the new format. The test can extend `AzureBlobStorageDestinationAcceptanceTest`.
