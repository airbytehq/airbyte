# Azure Blob Storage

This page contains the setup guide and reference information for the Azure Blob Storage source connector.

## Setup guide

### Step 1: Set up Azure Blob Storage

1. Create an Azure account or log in to your existing account. If you don't have an account, you can [create a new one](https://azure.microsoft.com/free/).
2. Create a storage account with the permissions to access and manage blob objects. Follow the instructions [here](https://docs.microsoft.com/en-us/azure/storage/common/storage-account-create?tabs=azure-portal).

### Step 2: Set up the Azure Blob Storage connector in Airbyte

1. In the Airbyte Connector configuration form, choose the **azure-blob-storage** source connector.
2. In the **Connection Configuration** section of the form, enter the following required fields:
   * `azure_blob_storage_account_name`: Enter the account name of your Azure Blob Storage.
   * `azure_blob_storage_account_key`: Enter the account key for your Azure Blob Storage account. You can find it by following the instructions [here](https://docs.microsoft.com/en-us/azure/storage/common/storage-account-keys-manage?tabs=azure-portal).
   * `azure_blob_storage_container_name`: Enter the name of the container where your blobs are located.
   * `format`: Choose the format of your files. Currently, only the line-delimited [JSON](https://jsonlines.org/) format is supported.
3. (Optional) To limit the number of blobs being considered for constructing the schema, enter the `azure_blob_storage_schema_inference_limit` property.
4. (Optional) If you are only interested in blobs containing a specific prefix in the container, enter the `azure_blob_storage_blobs_prefix` property.
5. Click on the **Test** button to verify that the connection is successful.
6. Click on the **Create** button to save the connection.

## Supported sync modes

The azure-blob-storage source connector supports the following [sync modes](https://docs.airbyte.io/integrations/sources/azure-blob-storage):

| Feature                                        | Supported? |
|:-----------------------------------------------| :--------- |
| Full Refresh Sync                              | Yes        |
| Incremental Sync                               | Yes        |
| Replicate Incremental Deletes                  | No         |
| Replicate Multiple Files \(blob prefix\)       | Yes        |
| Replicate Multiple Streams \(distinct tables\) | No         |
| Namespaces                                     | No         |

## Azure Blob Storage Settings

* `azure_blob_storage_account_name` : name of your account
* `azure_blob_storage_account_key` : key of your account
* `azure_blob_storage_container_name` : name of the container where your blobs are located
* `azure_blob_storage_blobs_prefix` : prefix for getting files which contain that prefix. For example, `FolderA/FolderB/` will get files named `FolderA/FolderB/blob.json` but not `FolderA/blob.json`.
* `azure_blob_storage_schema_inference_limit` : limits the number of files being scanned for schema inference and can increase speed and efficiency
* `format` : file format of the blobs in the container

### Jsonl

Only the line-delimited [JSON](https://jsonlines.org/) format is supported for now.

## Changelog 21210

The Changelog section cannot be updated. Please refer to the Airbyte documentation for updates.