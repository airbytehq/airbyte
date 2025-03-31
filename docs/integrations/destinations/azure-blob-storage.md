# Azure Blob Storage

## Overview

This destination writes data to Azure Blob Storage.

The Airbyte Azure Blob Storage destination allows you to sync data to Azure Blob Storage. Each stream is written to its own blob under the container,
as `<stream_namespace>/<stream_name>/yyyy_mm_dd_<unix_epoch>_<part_number>.<file_extension>`.

## Sync Mode

| Feature                        | Support |
| :----------------------------- | :-----: |
| Full Refresh Sync              |   ✅    |
| Incremental - Append Sync      |   ✅    |
| Incremental - Append + Deduped |   ❌    |

## Configuration

| Parameter                                    |  Type   | Notes                                                                                                                                                                     |
| :------------------------------------------- | :-----: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Endpoint Domain Name                         | string  | This is Azure Blob Storage endpoint domain name. Leave default value \(or leave it empty if run container from command line\) to use Microsoft native one.                |
| Azure blob storage container \(Bucket\) Name | string  | A name of the Azure blob storage container. If not exists - will be created automatically. If leave empty, then will be created automatically airbytecontainer+timestamp. |
| Azure Blob Storage account name              | string  | The account's name of the Azure Blob Storage.                                                                                                                             |
| The Azure blob storage account key           | string  | Azure blob storage account key. If this is set, the `shared access signature` option must not be set. Example: `abcdefghijklmnopqrstuvwxyz/0123456789+ABCDEFGHIJKLMNOPQRSTUVWXYZ/0123456789%++sampleKey==`.                                     |
| The Azure blob shared access signature       | string  | Azure blob storage shared account signature (SAS). If this is set, the `storage account key` option must not be set. Example: `sv=2025-01-01&ss=b&srt=co&sp=abcdefghijk&se=2026-01-31T07:00:00Z&st=2025-01-31T20:30:29Z&spr=https&sig=YWJjZGVmZ2hpamthYmNkZWZnaGlqa2FiY2RlZmdoaWp%3D`.                  |
| Azure Blob Storage target blob size          | integer | How large each blob should be, in megabytes. Example: 500. After a blob exceeds this size, the connector will start writing to a new blob, and increment the part number. |
| Format                                       | object  | Format specific configuration. See below for details.                                                                                                                     |

## Output Schema

### CSV

Like most of the other Airbyte destination connectors, usually the output has three columns: a UUID, an emission timestamp, and the data blob. With the CSV output, it is possible to normalize \(flatten\) the data blob to multiple columns.

| Column                   | Condition                                                                                          | Description                                                                 |
| :----------------------- | :------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------- |
| `_airbyte_raw_id`        | Always exists.                                                                                     | A uuid assigned by Airbyte to each processed record.                        |
| `_airbyte_extracted_at`  | Always exists.                                                                                     | A timestamp representing when the event was extracted from the data source. |
| `_airbyte_generation_id` | Always exists.                                                                                     | An integer id that increases with each new refresh.                         |
| `_airbyte_meta`          | Always exists.                                                                                     | A structured object containing metadata about the record.                   |
| `_airbyte_data`          | When no normalization \(flattening\) is needed, all data resides under this column as a JSON blob. |                                                                             |
| root level fields        | When root level normalization \(flattening\) is selected, the root level fields are expanded.      |                                                                             |

The schema for `_airbyte_meta` is:

| Field Name | Type    | Description                             |
| :--------- | :------ | :-------------------------------------- |
| `changes`  | list    | A list of structured change objects.    |
| `sync_id`  | integer | An integer identifier for the sync job. |

The schema for a change object is:

| Field Name | Type   | Description                                                                                                              |
| :--------- | :----- | :----------------------------------------------------------------------------------------------------------------------- |
| `field`    | string | The name of the field that changed.                                                                                      |
| `change`   | string | The type of change (eg, `NULLED`, `TRUNCATED`).                                                                          |
| `reason`   | string | The reason for the change, including its system of origin (ie, whether it was a source, destination, or platform error). |

For example, given the following JSON object from a source:

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

| `_airbyte_raw_id`                      | `_airbyte_extracted_at` | `_airbyte_generation_id` | `_airbyte_meta`                     | `_airbyte_data`                                                |
| :------------------------------------- | :---------------------- | :----------------------- | ----------------------------------- | :------------------------------------------------------------- |
| `26d73cde-7eb1-4e1e-b7db-a4c03b4cf206` | 1622135805000           | 11                       | `{"changes":[], "sync_id": 10111 }` | `{ "user_id": 123, name: { "first": "John", "last": "Doe" } }` |

With root level normalization, the output CSV is:

| `_airbyte_raw_id`                      | `_airbyte_extracted_at` | `_airbyte_generation_id` | `_airbyte_meta`                     | `user_id` | `name.first` | `name.last` |
| :------------------------------------- | :---------------------- | :----------------------- | ----------------------------------- | :-------: | :----------: | :---------: |
| `26d73cde-7eb1-4e1e-b7db-a4c03b4cf206` | 1622135805000           | 11                       | `{"changes":[], "sync_id": 10111 }` |    123    |     John     |     Doe     |

### JSON Lines \(JSONL\)

[JSON Lines](https://jsonlines.org/) is a text format with one JSON per line. Each line has a
structure as follows:

```json
{
  "_airbyte_raw_id": "<uuid>",
  "_airbyte_extracted_at": "<timestamp>",
  "_airbyte_generation_id": "<generation-id>",
  "_airbyte_meta": "<json-meta>",
  "_airbyte_data": "<json-data-from-source>"
}
```

For example, given the following two JSON objects from a source:

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

```text
{ "_airbyte_raw_id": "26d73cde-7eb1-4e1e-b7db-a4c03b4cf206", "_airbyte_extracted_at": "1622135805000", "_airbyte_generation_id": "11", "_airbyte_meta": { "changes": [], "sync_id": 10111 }, "_airbyte_data": { "user_id": 123, "name": { "first": "John", "last": "Doe" } } }
{ "_airbyte_ab_id": "0a61de1b-9cdd-4455-a739-93572c9a5f20", "_airbyte_extracted_at": "1631948170000", "_airbyte_generation_id": "12", "_airbyte_meta": { "changes": [], "sync_id": 10112 }, "_airbyte_data": { "user_id": 456, "name": { "first": "Jane", "last": "Roe" } } }
```

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
  * **Authentication** - you must use exactly one of these:
    * **The Azure blob storage shared acces signature** (recommended)
      * See [this](https://learn.microsoft.com/en-us/azure/ai-services/translator/document-translation/how-to-guides/create-sas-tokens?tabs=Containers#create-sas-tokens-in-the-azure-portal) for how to create an SAS.
    * **The Azure blob storage account key**
      * Corresponding key to the above user.
  * **Format**
    * Data format that will be use for a migrated data representation in blob.
* Make sure your user has access to Azure from the machine running Airbyte.
  * This depends on your networking setup.
  * The easiest way to verify if Airbyte is able to connect to your Azure blob storage container is via the check connection tool in the UI.


## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                               | Subject                                                                                                                                                         |
|:--------|:-----------|:-----------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1.0.0   | 2025-04-03 | [56391](https://github.com/airbytehq/airbyte/pull/56391)   | Bring into compliance with modern connector standards; certify connector.                                                                                       |
| 0.2.5   | 2025-03-21 | [55906](https://github.com/airbytehq/airbyte/pull/55906)   | Upgrade to airbyte/java-connector-base:2.0.1 to be M4 compatible.                                                                                               |
| 0.2.4   | 2025-01-10 | [51507](https://github.com/airbytehq/airbyte/pull/51507)   | Use a non root base image |
| 0.2.3   | 2024-12-18 | [49910](https://github.com/airbytehq/airbyte/pull/49910)   | Use a base image: airbyte/java-connector-base:1.0.0 |
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
