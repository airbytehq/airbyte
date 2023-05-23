# Azure Blob Storage

This page contains the setup guide and reference information for the Azure Blob Storage source connector.

:::info
Cloud storage may incur egress costs. Egress refers to data that is transferred out of the cloud storage system, such as when you download files or access them from a different location. For more information, see the [Azure Blob Storage pricing guide](https://azure.microsoft.com/en-us/pricing/details/storage/blobs/).
:::

## Setup guide

### Step 1: Set up Azure Blob Storage

1. Sign in to the [Azure portal](https://portal.azure.com/).
2. Create a storage account by following the detailed instructions provided in the [Azure Blob Storage documentation](https://docs.microsoft.com/en-us/azure/storage/common/storage-account-create?tabs=azure-portal).

### Step 2: Obtain Azure Blob Storage credentials

1. In the Azure portal, navigate to your storage account.
2. Under the "Settings" section, click on "Access keys" to view your storage account name and account key.

### Step 3: Collect the container name

1. In the Azure portal, under the storage account blade, click on "Containers".
2. Identify the container where your blobs are located, and note down the container name.

### Step 4: Set up the Azure Blob Storage connector in Airbyte

1. Create a new Azure Blob Storage source with a suitable name.
2. Set the `azure_blob_storage_account_name` with the storage account name obtained from Step 2.
3. Set `azure_blob_storage_account_key` with the storage account key obtained from Step 2.
4. Set `azure_blob_storage_container_name` with the container name collected in Step 3.
5. (Optional) If you are only interested in blobs containing some prefix in the container, set the `azure_blob_storage_blobs_prefix` property.
6. (Optional) Set `azure_blob_storage_schema_inference_limit` if you want to limit the number of blobs being considered for constructing the schema.
7. Choose the format corresponding to the format of your files. Currently, only line-delimited JSON (JSONL) is supported.

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

