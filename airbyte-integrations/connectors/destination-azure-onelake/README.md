# OneLake Airbyte Destination Connector

An **Airbyte destination connector** that writes data to **Microsoft Fabric OneLake** (Lakehouse Files) via the Azure Blob–compatible API. Supports **Service Principal** and **Managed Identity** authentication, configurable output paths, and CSV/JSONL formats.

## Documentation

- **[Build, deploy & operations](docs/BUILD_AND_DEPLOY.md)** — Build image, deploy to Kind/Kubernetes, configure, troubleshoot.
- **[GitHub repo setup](docs/GITHUB_SETUP.md)** — Create and push the repo (e.g. **OneLake Airbyte Destination Connector**).
- **[LinkedIn posts](docs/LINKEDIN_POSTS.md)** — Ready-to-use post drafts and promo image (`assets/onelake-airbyte-promo.png`) for promotion.
- **Sample configs** — [`sample_secrets/`](sample_secrets/) for Service Principal (`config.json`) and Managed Identity (`config_managed_identity.json`).

## Quick start

1. **Build & tag image** (from [Airbyte](https://github.com/airbytehq/airbyte) monorepo root):
   ```bash
   ./gradlew :airbyte-integrations:connectors:destination-azure-onelake:assemble --no-daemon -q
   docker tag airbyte/destination-azure-onelake:dev airbyte/destination-azure-onelake:1.1
   ```
2. **Load into Kind** (if using Kind): `kind load docker-image airbyte/destination-azure-onelake:1.1 --name airbyte-abctl`
3. **In Airbyte**: Add destination → Custom connector → Image `airbyte/destination-azure-onelake:1.1`. Set Fabric workspace, Lakehouse, auth (SP or MI), and **Output Path Format** (e.g. `Direct_Onelake_Connector_Data/`).

---

## Authentication

### Option 1: Service Principal (default)

Use Azure Tenant ID, Client ID, and Client Secret. The service principal must have **Storage Blob Data Contributor** (or equivalent) on the Fabric workspace.

### Option 2: Managed Identity

Set **Use Managed Identity** to `true` in the destination configuration. Leave Tenant ID, Client ID, and Client Secret empty.

**What you need when using Managed Identity:**

1. **Where the connector runs** must have an Azure Managed Identity attached:
   - **Azure VM / VMSS:** enable System-assigned or assign a User-assigned identity.
   - **Azure Container Apps / App Service:** enable Managed identity in the resource’s Identity blade.
   - **AKS:** use [Azure AD pod identity](https://learn.microsoft.com/en-us/azure/aks/use-azure-ad-pod-identity) or [workload identity](https://learn.microsoft.com/en-us/azure/aks/workload-identity-overview) so the Airbyte worker pod runs with a managed identity.
   - **Airbyte Cloud:** use the identity Airbyte provides for your destination (if supported) or continue using Service Principal.

2. **Permissions:** The managed identity needs **Storage Blob Data Contributor** (or at least **Storage Blob Data Owner**) on the **Fabric workspace** that backs your OneLake account.
   - In **Azure Portal:** find the workspace’s underlying storage (Microsoft Fabric uses a storage account per workspace) or use **Microsoft Fabric** admin to assign the identity to the workspace with the right role.
   - In **Fabric:** Workspace → Manage access → Add the identity (by name or client ID for user-assigned) and grant **Contributor** or the role that includes write to the Lakehouse.

3. **User-assigned identity (optional):** If you use a **user-assigned** managed identity, set **Managed Identity Client ID** in the destination config to that identity’s client ID. Leave it empty for **system-assigned** identity.

4. **No secrets:** With Managed Identity you do not store Tenant ID, Client ID, or Client Secret; the host obtains a token automatically.

---

# Azure OneLake Test Configuration

In order to test the Azure OneLake destination, you need a Microsoft account.

## Community Contributor

As a community contributor, you will need access to Azure to run the integration tests.

- Create an Azure Storage account (or identify your OneLake-compatible endpoint) for testing. Check if it works under https://portal.azure.com/ -> "Storage explorer (preview)".
- Get your `azure_blob_storage_account_name` and `azure_blob_storage_account_key` that can read and write to the target container.
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
- Create a new package under `io.airbyte.integrations.destination.azure_onelake` (or reuse the existing `azure_blob_storage` package if only rebranding).
- Implement a new `AzureBlobStorageWriter`. The implementation can extend `BaseAzureBlobStorageWriter`.
- Write an acceptance test for the new output format. The test can extend `AzureBlobStorageDestinationAcceptanceTest`.
