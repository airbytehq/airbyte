# Azure Blob Storage

This page contains the setup guide and reference information for the Azure Blob Storage source connector.

:::info
Cloud storage may incur egress costs. Egress refers to data that is transferred out of the cloud storage system, such as when you download files or access them from a different location. For more information, see the [Azure Blob Storage pricing guide](https://azure.microsoft.com/en-us/pricing/details/storage/blobs/).
:::

## Setup Guide

### Step 1: Set Up Azure Blob Storage

To set up a storage account with the required permissions, follow the steps in the [Create an Azure Blob Storage Account](https://docs.microsoft.com/en-us/azure/storage/common/storage-account-create?tabs=azure-portal) documentation.

### Step 2: Obtain Storage Account Name and Key

1. Sign in to the [Azure portal](https://portal.azure.com/).
2. Navigate to your storage account.
3. In the storage account's menu, click on "Access keys" under Settings.
4. Copy the storage account name and key from the 'key1' section.

For more information, refer to the [Azure documentation on managing storage account access keys](https://docs.microsoft.com/en-us/azure/storage/common/storage-account-keys-manage).

### Step 3: Set up the Azure Blob Storage Connector in Airbyte

1. Enter the **Storage Account Name** obtained in Step 2 in the `azure_blob_storage_account_name` field.
2. Enter the **Storage Account Key** obtained in Step 2 in the `azure_blob_storage_account_key` field.
3. Set the `azure_blob_storage_container_name` field with the name of the container where the blobs are located.
4. (Optional) Enter the `azure_blob_storage_endpoint` field if you want to use a custom endpoint domain name. Default is `"blob.core.windows.net"`.
5. (Optional) If you are only interested in blobs containing some prefix in the container, enter the prefix in the `azure_blob_storage_blobs_prefix` field.
6. (Optional) If you want to limit the number of blobs being considered for constructing the schema, set the `azure_blob_storage_schema_inference_limit` field.
7. Choose the format corresponding to the format of your files in the `format` field. For example:

```json
{
  "format_type": "JSONL"
}
```

After entering all the required information, the Azure Blob Storage source connector in Airbyte should be properly configured.


## Supported sync modes

The Azure Blob Storage source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                                        | Supported? |
|:-----------------------------------------------| :--------- |
| Full Refresh Sync                              | Yes        |
| Incremental Sync                               | Yes        |
| Replicate Incremental Deletes                  | No         |
| Replicate Multiple Files \(blob prefix\)       | Yes        |
| Replicate Multiple Streams \(distinct tables\) | No         |
| Namespaces                                     | No         |


## Azure Blob Storage Settings

* `azure_blob_storage_endpoint` : azure blob storage endpoint to connect to
* `azure_blob_storage_container_name` : name of the container where your blobs are located
* `azure_blob_storage_account_name` : name of your account
* `azure_blob_storage_account_key` : key of your account
* `azure_blob_storage_blobs_prefix` : prefix for getting files which contain that prefix i.e. FolderA/FolderB/ will get files named FolderA/FolderB/blob.json but not FolderA/blob.json
* `azure_blob_storage_schema_inference_limit` : Limits the number of files being scanned for schema inference and can increase speed and efficiency
* `format` : File format of the blobs in the container

**File Format Settings**

### Jsonl

Only the line-delimited [JSON](https://jsonlines.org/) format is supported for now 

## Changelog 21210

| Version | Date       | Pull Request                                     | Subject                                                                 |
|:--------|:-----------|:-------------------------------------------------|:------------------------------------------------------------------------|
| 0.1.0   | 2023-02-17 | https://github.com/airbytehq/airbyte/pull/23222  | Initial release with full-refresh and incremental sync with JSONL files |
