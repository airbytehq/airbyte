# Azure Blob Storage

This page contains the setup guide and reference information for the Azure Blob Storage source connector.

## Setup guide

### Step 1: Set up Azure Blob Storage

Before you can set up the Azure Blob Storage connector, you need to create a storage account in Azure Blob Storage. Follow the instructions below to create a storage account with appropriate permissions:

1. Sign in to the [Azure portal](https://portal.azure.com/).
2. In the left-hand navigation pane, select "Storage accounts."
3. Select "+ Add" to create a new storage account.
4. Choose your subscription and resource group, or create a new one.
5. Enter a unique name for your storage account. The name must be between 3 and 24 characters long, and can contain only numbers and lowercase letters.
6. Choose the performance tier and replication settings.
7. In the "Networking" tab, select "Add existing virtual network" and then select your virtual network from the dropdown list.
8. In the "Data protection" tab, leave all the settings at their defaults.
9. Review your choices and select "Create" to create the storage account.

For more details on how to create a storage account with the appropriate permissions, refer to the [official Azure Blob Storage documentation](https://docs.microsoft.com/en-us/azure/storage/common/storage-account-create?tabs=azure-portal).

### Step 2: Set up the Azure Blob Storage connector in Airbyte

Now that you've set up your Azure Blob Storage account, you can proceed with setting up the connector in Airbyte. 

1. In the Airbyte UI, select "Create New Connection" and then select "azure-blob-storage" from the dropdown list.
2. Enter a unique name for the connector.
3. Under "Azure Blob Storage Connection Configuration" section, enter the following information:
   * **Endpoint Domain Name**: This is the Azure Blob Storage endpoint domain name. Leave the default value (or leave it empty if you run container from command line) to use Microsoft native from example.
   * **Azure Blob Storage container (Bucket) Name**: The name of the Azure Blob Storage container you want to connect to.
   * **Azure Blob Storage account name**: The account name of the Azure Blob Storage account you want to connect to.
   * **Azure Blob Storage account key**: The account key of the Azure Blob Storage account you want to connect to.
   * **Azure Blob Storage blobs prefix**: (Optional) If you're only interested in blobs containing some prefix in the container, enter the blobs prefix in this field.
   * **Azure Blob Storage schema inference limit**: (Optional) If you want to limit the number of blobs being considered for constructing the schema, enter the number here.
   * **Input Format**: Select the input format of your blobs.
4. Select "Test" to test your connection. If everything is set up correctly, you should see a success message.
5. Select "Save" to save your connector configuration.

**Note:**
The credential fields (e.g., Azure Blob Storage account key) should be set as [Airbyte Secrets](https://docs.airbyte.io/tutorials/using-airbyte/using-airbyte-secrets). 

## Supported sync modes

The Azure Blob Storage source connector supports the following [sync modes](https://docs.airbyte.io/cloud-core-concepts/connection-mode-overview):

| Feature                                        | Supported? |
|:-----------------------------------------------|:-----------|
| Full Refresh Sync                              | Yes        |
| Incremental Sync                               | Yes        |
| Replicate Incremental Deletes                  | No         |
| Replicate Multiple Files (blob prefix)         | Yes        |
| Replicate Multiple Streams (distinct tables)   | No         |
| Namespaces                                     | No         |

## Azure Blob Storage Settings

Here are the detailed descriptions for each of the Azure Blob Storage settings for the connector:

* **azure_blob_storage_endpoint**: Azure Blob Storage endpoint domain name, for example, `blob.core.windows.net`. This domain name gets appended to the container URL while making the API request. Leave it empty to use Microsoft native from the example.
* **azure_blob_storage_container_name**: Name of the Azure Blob Storage container.
* **azure_blob_storage_account_name**: Name of the Azure Blob Storage account.
* **azure_blob_storage_account_key**: Key of the Azure Blob Storage account.
* **azure_blob_storage_blobs_prefix**: (Optional) Prefix for getting files that contain that prefix. For example, `FolderA/FolderB/` will get files named `FolderA/FolderB/blob.json`, but not `FolderA/blob.json`.
* **azure_blob_storage_schema_inference_limit**: (Optional) Limits the number of blobs being scanned for inferring the schema, useful for large amounts of data with consistent structure.
* **format**: File format of the blobs in the container.

**File Format Settings**

### Jsonl

Only the line-delimited [JSON](https://jsonlines.org/) format is supported for now.

## Changelog 21210

| Version | Date       | Pull Request                                     | Subject                                                                 |
|:--------|:-----------|:-------------------------------------------------|:------------------------------------------------------------------------|
| 0.1.0   | 2023-02-17 | https://github.com/airbytehq/airbyte/pull/23222  | Initial release with full-refresh and incremental sync with JSONL files |

For more details on setting up and using Azure Blob Storage, refer to the [official Azure Blob Storage documentation](https://docs.microsoft.com/en-us/azure/storage/blobs/).