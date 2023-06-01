# Azure Blob Storage

This page contains the setup guide and reference information for the Azure Blob Storage source connector.

:::info
Cloud storage may incur egress costs. Egress refers to data that is transferred out of the cloud storage system, such as when you download files or access them from a different location. For more information, see the [Azure Blob Storage pricing guide](https://azure.microsoft.com/en-us/pricing/details/storage/blobs/).
:::

## Setup guide

### Step 1: Set up Azure Blob Storage

* Create a storage account with the permissions [details](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-create?tabs=azure-portal) 

### Step 2: Set up the Azure Blob Storage connector in Airbyte


1. Create a new Azure Blob Storage source with a suitable name.
2. Set `container` appropriately. This will be the name of the container where the blobs are located.
3. If you are only interested in blobs containing some prefix in the container set the blobs prefix property
4. Set schema inference limit if you want to limit the number of blobs being considered for constructing the schema
5. Choose the format corresponding to the format of your files.


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
