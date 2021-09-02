# Azure Blob Storage

## Overview

This destination writes data to Azure Blob Storage.

The Airbyte Azure Blob Storage destination allows you to sync data to Azure Blob Storage. Each stream is written to its own blob under the container.

## Sync Mode

| Feature | Support | Notes |
| :--- | :---: | :--- |
| Full Refresh Sync | ✅ | Warning: this mode deletes all previously synced data in the configured blob. |
| Incremental - Append Sync | ✅ | The append mode would only work for "Append blobs" blobs as per Azure limitations, more details https://docs.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction#blobs |


## Configuration

| Parameter | Type | Notes |
| :--- | :---: | :--- |
| Endpoint Domain Name | string | This is Azure Blob Storage endpoint domain name. Leave default value (or leave it empty if run container from command line) to use Microsoft native one. |
| Azure blob storage container (Bucket) Name | string | A name of the Azure blob storage container. If not exists - will be created automatically. If leave empty, then will be created automatically airbytecontainer+timestamp. |
| Azure Blob Storage account name | string | The account's name of the Azure Blob Storage. |
| The Azure blob storage account key | string | Azure blob storage account key. Example: `abcdefghijklmnopqrstuvwxyz/0123456789+ABCDEFGHIJKLMNOPQRSTUVWXYZ/0123456789%++sampleKey==`. |
| Format | object | Format specific configuration. See below for details. |

⚠️ Please note that under "Full Refresh Sync" mode, data in the configured blob will be wiped out before each sync. We recommend you to provision a dedicated Azure Blob Storage Container resource for this sync to prevent unexpected data deletion from misconfiguration. ⚠️


## Output Schema

Each stream will be outputted to its dedicated Blob according to the configuration. The complete datastore of each stream includes all the output files under that Blob. You can think of the Blob as equivalent of a Table in the database world.

- Under Full Refresh Sync mode, old output files will be purged before new files are created.
- Under Incremental - Append Sync mode, new output files will be added that only contain the new data.

### CSV

Like most of the other Airbyte destination connectors, usually the output has three columns: a UUID, an emission timestamp, and the data blob. With the CSV output, it is possible to normalize (flatten) the data blob to multiple columns.

| Column | Condition | Description |
| :--- | :--- | :--- |
| `_airbyte_ab_id` | Always exists | A uuid assigned by Airbyte to each processed record. |
| `_airbyte_emitted_at` | Always exists. | A timestamp representing when the event was pulled from the data source. |
| `_airbyte_data` | When no normalization (flattening) is needed, all data reside under this column as a json blob. |
| root level fields | When root level normalization (flattening) is selected, the root level fields are expanded. |

For example, given the following json object from a source:

```json
{
  "user_id": 123,
  "name": {
    "first": "John",
    "last": "Doe"
  }
}
```

With no normalization, the output CSV is:

| `_airbyte_ab_id` | `_airbyte_emitted_at` | `_airbyte_data` |
| :--- | :--- | :--- |
| `26d73cde-7eb1-4e1e-b7db-a4c03b4cf206` | 1622135805000 | `{ "user_id": 123, name: { "first": "John", "last": "Doe" } }` |

With root level normalization, the output CSV is:

| `_airbyte_ab_id` | `_airbyte_emitted_at` | `user_id` | `name` |
| :--- | :--- | :--- | :--- |
| `26d73cde-7eb1-4e1e-b7db-a4c03b4cf206` | 1622135805000 | 123 | `{ "first": "John", "last": "Doe" }` |

### JSON Lines (JSONL)

[Json Lines](https://jsonlines.org/) is a text format with one JSON per line. Each line has a structure as follows:

```json
{
  "_airbyte_ab_id": "<uuid>",
  "_airbyte_emitted_at": "<timestamp-in-millis>",
  "_airbyte_data": "<json-data-from-source>"
}
```

For example, given the following two json objects from a source:

```json
[
  {
    "user_id": 123,
    "name": {
      "first": "John",
      "last": "Doe"
    }
  },
  {
    "user_id": 456,
    "name": {
      "first": "Jane",
      "last": "Roe"
    }
  }
]
```

They will be like this in the output file:

```jsonl
{ "_airbyte_ab_id": "26d73cde-7eb1-4e1e-b7db-a4c03b4cf206", "_airbyte_emitted_at": "1622135805000", "_airbyte_data": { "user_id": 123, "name": { "first": "John", "last": "Doe" } } }
{ "_airbyte_ab_id": "0a61de1b-9cdd-4455-a739-93572c9a5f20", "_airbyte_emitted_at": "1631948170000", "_airbyte_data": { "user_id": 456, "name": { "first": "Jane", "last": "Roe" } } }
```

## Getting started

### Requirements

1. Create an AzureBlobStorage account. 
2. Check if it works under https://portal.azure.com/ -> "Storage explorer (preview)".

### Setup guide

* Fill up AzureBlobStorage info
  * **Endpoint Domain Name**
    * Leave default value (or leave it empty if run container from command line) to use Microsoft native one or use your own.
  * **Azure blob storage container**
    * If not exists - will be created automatically. If leave empty, then will be created automatically airbytecontainer+timestamp..
  * **Azure Blob Storage account name**
      * See [this](https://docs.microsoft.com/en-us/azure/storage/common/storage-account-create?tabs=azure-portal) on how to create an account.
  * **The Azure blob storage account key**
    * Corresponding key to the above user.
  * **Format**
    * Data format that will be use for a migrated data representation in blob.
* Make sure your user has access to Azure from the machine running Airbyte.
  * This depends on your networking setup.
  * The easiest way to verify if Airbyte is able to connect to your Azure blob storage container is via the check connection tool in the UI.



## CHANGELOG

| Version | Date | Pull Request | Subject |
| :--- | :---  | :--- | :--- |
| 0.1.0 | 2021-08-30 | [#5332](https://github.com/airbytehq/airbyte/pull/5332) | Initial release with JSONL and CSV output. |
