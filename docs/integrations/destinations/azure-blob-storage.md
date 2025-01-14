# Azure Blob Storage

## Overview

This destination writes data to Azure Blob Storage.

The Airbyte Azure Blob Storage destination allows you to sync data to Azure Blob Storage. Each stream is written to its own blob under the container.

## Prerequisites

- For Airbyte Open Source users using the [Postgres](https://docs.airbyte.com/integrations/sources/postgres) source connector, [upgrade](https://docs.airbyte.com/operator-guides/upgrading-airbyte/) your Airbyte platform to version `v0.40.0-alpha` or newer and upgrade your AzureBlobStorage connector to version `0.1.6` or newer

## Sync Mode

| Feature                        | Support | Notes                                                                                                                                                                                                                                                                           |
| :----------------------------- | :-----: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Full Refresh Sync              |   ✅    | Warning: this mode deletes all previously synced data in the configured blob.                                                                                                                                                                                                   |
| Incremental - Append Sync      |   ✅    | The append mode would only work for "Append blobs" blobs as per Azure limitations, more details [https://docs.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction\#blobs](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction#blobs) |
| Incremental - Append + Deduped |   ❌    | destination.                                                                                                                                                                                                                                                                    |

## Configuration

| Parameter                                    |  Type   | Notes                                                                                                                                                                     |
| :------------------------------------------- | :-----: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Endpoint Domain Name                         | string  | This is Azure Blob Storage endpoint domain name. Leave default value \(or leave it empty if run container from command line\) to use Microsoft native one.                |
| Azure blob storage container \(Bucket\) Name | string  | A name of the Azure blob storage container. If not exists - will be created automatically. If leave empty, then will be created automatically airbytecontainer+timestamp. |
| Azure Blob Storage account name              | string  | The account's name of the Azure Blob Storage.                                                                                                                             |
| The Azure blob storage account key           | string  | Azure blob storage account key. Example: `abcdefghijklmnopqrstuvwxyz/0123456789+ABCDEFGHIJKLMNOPQRSTUVWXYZ/0123456789%++sampleKey==`.                                     |
| Azure Blob Storage output buffer size        | integer | Azure Blob Storage output buffer size, in megabytes. Example: 5                                                                                                           |
| Azure Blob Storage spill size                | integer | Azure Blob Storage spill size, in megabytes. Example: 500. After exceeding threshold connector will create new blob with incremented sequence number 'prefix_name'\_seq+1 |
| Format                                       | object  | Format specific configuration. See below for details.                                                                                                                     |

⚠️ Please note that under "Full Refresh Sync" mode, data in the configured blob will be wiped out before each sync. We recommend you to provision a dedicated Azure Blob Storage Container resource for this sync to prevent unexpected data deletion from misconfiguration. ⚠️

## Output Schema

Each stream will be outputted to its dedicated Blob according to the configuration. The complete datastore of each stream includes all the output files under that Blob. You can think of the Blob as equivalent of a Table in the database world.
If stream replication exceeds configured threshold data will continue to be replicated in a new blob file for better read performance

- Under Full Refresh Sync mode, old output files will be purged before new files are created.
- Under Incremental - Append Sync mode, new output files will be added that only contain the new data.

### CSV

Like most of the other Airbyte destination connectors, usually the output has three columns: a UUID, an emission timestamp, and the data blob. With the CSV output, it is possible to normalize \(flatten\) the data blob to multiple columns.

| Column                | Condition                                                                                         | Description                                                              |
| :-------------------- | :------------------------------------------------------------------------------------------------ | :----------------------------------------------------------------------- |
| `_airbyte_ab_id`      | Always exists                                                                                     | A uuid assigned by Airbyte to each processed record.                     |
| `_airbyte_emitted_at` | Always exists.                                                                                    | A timestamp representing when the event was pulled from the data source. |
| `_airbyte_data`       | When no normalization \(flattening\) is needed, all data reside under this column as a json blob. |                                                                          |
| root level fields     | When root level normalization \(flattening\) is selected, the root level fields are expanded.     |                                                                          |

For example, given the following json object from a source:

```javascript
{
  "user_id": 123,
  "name": {
    "first": "John",
    "last": "Doe"
  }
}
```

With no normalization, the output CSV is:

| `_airbyte_ab_id`                       | `_airbyte_emitted_at` | `_airbyte_data`                                                |
| :------------------------------------- | :-------------------- | :------------------------------------------------------------- |
| `26d73cde-7eb1-4e1e-b7db-a4c03b4cf206` | 1622135805000         | `{ "user_id": 123, name: { "first": "John", "last": "Doe" } }` |

With root level normalization, the output CSV is:

| `_airbyte_ab_id`                       | `_airbyte_emitted_at` | `user_id` | `name`                               |
| :------------------------------------- | :-------------------- | :-------- | :----------------------------------- |
| `26d73cde-7eb1-4e1e-b7db-a4c03b4cf206` | 1622135805000         | 123       | `{ "first": "John", "last": "Doe" }` |

With the field `File Extension`, it is possible to save the output files with extension. It is an optional field with default value as `false`. Enable this to store the files with `csv` extension.

### JSON Lines \(JSONL\)

[Json Lines](https://jsonlines.org/) is a text format with one JSON per line. Each line has a structure as follows:

```javascript
{
  "_airbyte_ab_id": "<uuid>",
  "_airbyte_emitted_at": "<timestamp-in-millis>",
  "_airbyte_data": "<json-data-from-source>"
}
```

For example, given the following two json objects from a source:

```javascript
[
  {
    user_id: 123,
    name: {
      first: "John",
      last: "Doe",
    },
  },
  {
    user_id: 456,
    name: {
      first: "Jane",
      last: "Roe",
    },
  },
];
```

They will be like this in the output file:

```text
{ "_airbyte_ab_id": "26d73cde-7eb1-4e1e-b7db-a4c03b4cf206", "_airbyte_emitted_at": "1622135805000", "_airbyte_data": { "user_id": 123, "name": { "first": "John", "last": "Doe" } } }
{ "_airbyte_ab_id": "0a61de1b-9cdd-4455-a739-93572c9a5f20", "_airbyte_emitted_at": "1631948170000", "_airbyte_data": { "user_id": 456, "name": { "first": "Jane", "last": "Roe" } } }
```

With the field `File Extension`, it is possible to save the output files with extension. It is an optional field with default value as `false`. Enable this to store the files with `jsonl` extension.

## Getting started

### Requirements

1. Create an AzureBlobStorage account.
2. Check if it works under [https://portal.azure.com/](https://portal.azure.com/) -&gt; "Storage explorer \(preview\)".

### Setup guide

* Fill up AzureBlobStorage info
  * **Endpoint Domain Name**
    * Leave default value \(or leave it empty if run container from command line\) to use Microsoft native one or use your own.
  * **Azure blob storage container**
    * If not exists - will be created automatically. If leave empty, then will be created automatically airbytecontainer+timestamp..
  * **Azure Blob Storage account name**
    * See [this](https://docs.microsoft.com/en-us/azure/storage/common/storage-account-create?tabs=azure-portal) on how to create an account.
  * **The Azure blob storage account key**
    * Corresponding key to the above user.
  * **Format**
    * Data format that will be use for a migrated data representation in blob.
    * With the field **File Extension**, it is possible to save the output files with extension. It is an optional field with default value as `false`. Enable this to store the files with extension.
* Make sure your user has access to Azure from the machine running Airbyte.
  * This depends on your networking setup.
  * The easiest way to verify if Airbyte is able to connect to your Azure blob storage container is via the check connection tool in the UI.


## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                               | Subject                                                                                                                                                         |
|:--------|:-----------|:-----------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0.2.3 | 2024-12-18 | [49910](https://github.com/airbytehq/airbyte/pull/49910) | Use a base image: airbyte/java-connector-base:1.0.0 |
| 0.2.2   | 2024-06-12 | [\#38061](https://github.com/airbytehq/airbyte/pull/38061) | File Extensions added for the output files                                                                                                                      |
| 0.2.1   | 2023-09-13 | [\#30412](https://github.com/airbytehq/airbyte/pull/30412) | Switch noisy logging to debug                                                                                                                                   |
| 0.2.0   | 2023-01-18 | [\#21467](https://github.com/airbytehq/airbyte/pull/21467) | Support spilling of objects exceeding configured size threshold                                                                                                 |
| 0.1.6   | 2022-08-08 | [\#15318](https://github.com/airbytehq/airbyte/pull/15318) | Support per-stream state                                                                                                                                        |
| 0.1.5   | 2022-06-16 | [\#13852](https://github.com/airbytehq/airbyte/pull/13852) | Updated stacktrace format for any trace message errors                                                                                                          |
| 0.1.4   | 2022-05-17 | [12820](https://github.com/airbytehq/airbyte/pull/12820)   | Improved 'check' operation performance                                                                                                                          |
| 0.1.3   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256)   | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                                                                                    |
| 0.1.2   | 2022-01-20 | [\#9682](https://github.com/airbytehq/airbyte/pull/9682)   | Each data synchronization for each stream is written to a new blob to the folder with stream name.                                                              |
| 0.1.1   | 2021-12-29 | [\#9190](https://github.com/airbytehq/airbyte/pull/9190)   | Added BufferedOutputStream wrapper to blob output stream to improve performance and fix issues with 50,000 block limit. Also disabled autoflush on PrintWriter. |
| 0.1.0   | 2021-08-30 | [\#5332](https://github.com/airbytehq/airbyte/pull/5332)   | Initial release with JSONL and CSV output.                                                                                                                      |

</details>
