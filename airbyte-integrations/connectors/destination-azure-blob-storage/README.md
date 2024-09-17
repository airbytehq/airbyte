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

### Infra setup

1. Log in to the [Azure portal](https://portal.azure.com/#home) using the `integration-test@airbyte.io` account
1. Go to [Storage Accounts](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Storage%2FStorageAccounts)
1. Create a new storage account with a reasonable name (currently `airbyteteststorage`), under the `integration-test-rg` resource group.
1. In the `Redundancy` setting, choose `Locally-redundant storage (LRS)`.
1. Hit `Review` (you can leave all the other settings as the default) and then `Create`.
1. Navigate into that storage account -> `Containers`. Make a new container with a reasonable name (currently `airbytetescontainername`).
1. Then go back up to the storage account -> `Access keys`. This is the `azure_blob_storage_account_key` config field.
1. There are two keys; use the first one. We don't need 100% uptime on our integration tests, so there's no need to alternate between the two keys.

## Add New Output Format

- Add a new enum in `AzureBlobStorageFormat'.
- Modify `spec.json` to specify the configuration of this new format.
- Update `AzureBlobStorageFormatConfigs` to be able to construct a config for this new format.
- Create a new package under `io.airbyte.integrations.destination.azure_blob_storage`.
- Implement a new `AzureBlobStorageWriter`. The implementation can extend `BaseAzureBlobStorageWriter`.
- Write an acceptance test for the new output format. The test can extend `AzureBlobStorageDestinationAcceptanceTest`.
