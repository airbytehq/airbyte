# Azure Blob Storage

## Overview

This destination writes data to Azure Blob Storage.

Airbyte writes each stream to its own directory inside the container you configure. A stream can span several blobs, because Airbyte starts a new part when the current blob reaches its size limit. Blob names follow this pattern:

```text
<container>/<stream_namespace>/<stream_name>/<yyyy_mm_dd>_<epoch_milliseconds>_<part_number>.<file_extension>
```

The date and timestamp record when Airbyte wrote the blob, not when the source produced the records. You can't customize this path.

## Network access

If you're using Airbyte Cloud and this destination uses IP-based access controls,
add Airbyte's [IP addresses](/platform/operating-airbyte/ip-allowlist) to your
allowlist.

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | Yes |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | No |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | No |

In overwrite syncs, Airbyte writes the new generation of blobs first, then deletes blobs from previous generations after the stream finishes successfully. Old data stays in place if the sync fails partway through.

## Copy raw files

This destination supports the [copy raw files](/platform/using-airbyte/delivery-methods#copy-raw-files) delivery method, which moves files from a file-based source without parsing them. Airbyte preserves each file's path from the source, relative to the stream's directory:

```text
<container>/<stream_namespace>/<stream_name>/<path_of_file_in_source>
```

## Configuration

| Parameter                                | Required | Type    | Notes                                                                                                                                                                                                                                                                          |
| :--------------------------------------- | :------- | :------ | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Azure Blob Storage Account Name          | Yes      | string  | The name of your Azure storage account.                                                                                                                                                                                                                                        |
| Azure Blob Storage Container Name        | Yes      | string  | The name of the container Airbyte writes to. Create this container before you set up the destination. Airbyte doesn't create it for you.                                                                                                                                       |
| Azure Blob Storage Endpoint Domain Name  | No       | string  | Keep the default value, `blob.core.windows.net`. In version 1.1.7, the connector always connects to `https://<account name>.blob.core.windows.net` and ignores other values, so sovereign clouds and custom endpoints aren't supported.                                        |
| Azure Blob Storage Account Key           | No       | string  | Azure Blob Storage account key. If this is set, the `Shared Access Signature`, `Azure Tenant ID`, `Azure Client ID`, and `Azure Client Secret` fields must not be set. Example: `abcdefghijklmnopqrstuvwxyz/0123456789+ABCDEFGHIJKLMNOPQRSTUVWXYZ/0123456789%++sampleKey==`.    |
| Shared Access Signature                  | No       | string  | Azure Blob Storage shared access signature (SAS). If this is set, the `Azure Blob Storage Account Key`, `Azure Tenant ID`, `Azure Client ID`, and `Azure Client Secret` fields must not be set. Example: `sv=2025-01-01&ss=b&srt=co&sp=abcdefghijk&se=2026-01-31T07:00:00Z&st=2025-01-31T20:30:29Z&spr=https&sig=YWJjZGVmZ2hpamthYmNkZWZnaGlqa2FiY2RlZmdoaWp%3D`. |
| Azure Tenant ID                          | No       | string  | Azure Active Directory (Entra ID) tenant ID. Required for Entra ID authentication. If this is set, `Azure Client ID` and `Azure Client Secret` must also be set. Example: `12345678-1234-1234-1234-123456789012`.                                                               |
| Azure Client ID                          | No       | string  | Azure Active Directory (Entra ID) client ID. Required for Entra ID authentication. If this is set, `Azure Tenant ID` and `Azure Client Secret` must also be set. Example: `87654321-4321-4321-4321-210987654321`.                                                               |
| Azure Client Secret                      | No       | string  | Azure Active Directory (Entra ID) client secret. Required for Entra ID authentication. If this is set, `Azure Tenant ID` and `Azure Client ID` must also be set.                                                                                                                |
| Azure Blob Storage Target Blob Size (MB) | No       | integer | Intended to control how large each blob is before Airbyte starts a new part. Version 1.1.7 ignores this value and starts a new blob after about 200 MB.                                                                                                                        |
| Output Format                            | Yes      | object  | The file format Airbyte writes, either `CSV: Comma-Separated Values` or `JSON Lines: Newline-delimited JSON`. Each format takes a **Flattening** option: `No flattening` or `Root level flattening`. See [Output schema](#output-schema).                                       |

You must provide exactly one authentication method: an account key, a shared access signature, or all three Entra ID fields. The connector fails the connection check if you provide none or more than one.

## Output schema

### CSV

Like most other Airbyte destination connectors, the output contains your data, along with some [metadata fields](/platform/understanding-airbyte/airbyte-metadata-fields).
If you select the "root level flattening" option, your data will be promoted to additional columns; if you select "no flattening", your data
will be left as a JSON blob inside the `_airbyte_data` column.

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

With no flattening, the output CSV is:

| `_airbyte_raw_id`                      | `_airbyte_extracted_at` | `_airbyte_generation_id` | `_airbyte_meta`                     | `_airbyte_data`                                                |
| :------------------------------------- | :---------------------- | :----------------------- | ----------------------------------- | :------------------------------------------------------------- |
| `26d73cde-7eb1-4e1e-b7db-a4c03b4cf206` | 1622135805000           | 11                       | `{"changes":[], "sync_id": 10111 }` | `{ "user_id": 123, name: { "first": "John", "last": "Doe" } }` |

With root level flattening, the output CSV is:

| `_airbyte_raw_id`                      | `_airbyte_extracted_at` | `_airbyte_generation_id` | `_airbyte_meta`                     | `user_id` | `name.first` | `name.last` |
| :------------------------------------- | :---------------------- | :----------------------- | ----------------------------------- | :-------: | :----------: | :---------: |
| `26d73cde-7eb1-4e1e-b7db-a4c03b4cf206` | 1622135805000           | 11                       | `{"changes":[], "sync_id": 10111 }` |    123    |     John     |     Doe     |

### JSON Lines \(JSONL\)

[JSON Lines](https://jsonlines.org/) is a text format with one JSON per line. As with the [CSV](#csv) format, this connector will write your data along
with some [metadata fields](/platform/understanding-airbyte/airbyte-metadata-fields). You can enable "root level flattening" to promote your data to the root
of the JSON object, or use "no flattening" to leave your data inside the `_airbyte_data` object.

For example, given the following two JSON object from a source:

```json
{
  "user_id": 123,
  "name": {
    "first": "John",
    "last": "Doe"
  }
}
{
  "user_id": 456,
  "name": {
    "first": "Jane",
    "last": "Roe"
  }
}
```

With no flattening, the output JSONL is:

```text
{ "_airbyte_raw_id": "26d73cde-7eb1-4e1e-b7db-a4c03b4cf206", "_airbyte_extracted_at": "1622135805000", "_airbyte_generation_id": "11", "_airbyte_meta": { "changes": [], "sync_id": 10111 }, "_airbyte_data": { "user_id": 123, "name": { "first": "John", "last": "Doe" } } }
{ "_airbyte_raw_id": "0a61de1b-9cdd-4455-a739-93572c9a5f20", "_airbyte_extracted_at": "1631948170000", "_airbyte_generation_id": "12", "_airbyte_meta": { "changes": [], "sync_id": 10112 }, "_airbyte_data": { "user_id": 456, "name": { "first": "Jane", "last": "Roe" } } }
```

With root level flattening, the output JSONL is:

```text
{ "_airbyte_raw_id": "26d73cde-7eb1-4e1e-b7db-a4c03b4cf206", "_airbyte_extracted_at": "1622135805000", "_airbyte_generation_id": "11", "_airbyte_meta": { "changes": [], "sync_id": 10111 }, "user_id": 123, "name": { "first": "John", "last": "Doe" } }
{ "_airbyte_raw_id": "0a61de1b-9cdd-4455-a739-93572c9a5f20", "_airbyte_extracted_at": "1631948170000", "_airbyte_generation_id": "12", "_airbyte_meta": { "changes": [], "sync_id": 10112 }, "user_id": 456, "name": { "first": "Jane", "last": "Roe" } }
```

## Getting started

### Requirements

1. An [Azure storage account](https://learn.microsoft.com/azure/storage/common/storage-account-create?tabs=azure-portal) in the Azure public cloud. Sovereign clouds like Azure Government and Azure China aren't supported.
2. A [blob container](https://learn.microsoft.com/azure/storage/blobs/blob-containers-portal) in that account. Airbyte doesn't create the container, so create it first.
3. Credentials for one of the following authentication methods. All three need permission to list, read, write, and delete blobs in the container, because overwrite syncs delete blobs from previous generations.
   - **Azure Entra ID (service principal)**, which Microsoft recommends. Create a [service principal](https://learn.microsoft.com/entra/identity-platform/howto-create-service-principal-portal) with a client secret, then assign it the [Storage Blob Data Contributor](https://learn.microsoft.com/azure/storage/blobs/assign-azure-role-data-access) role on the container or storage account.
   - **Shared access signature (SAS)**. Create a [SAS token](https://learn.microsoft.com/azure/storage/common/storage-sas-overview) scoped to the container with read, add, create, write, delete, and list permissions. Syncs fail after the token expires, so track the expiry date.
   - **Account key**. Use one of the storage account's [access keys](https://learn.microsoft.com/azure/storage/common/storage-account-keys-manage). An account key grants full access to the whole storage account.

### Setup guide

1. In the Airbyte UI, add a new **Azure Blob Storage** destination.
2. Enter your **Azure Blob Storage Account Name** and **Azure Blob Storage Container Name**.
3. Leave **Azure Blob Storage Endpoint Domain Name** at its default value.
4. Fill in the fields for exactly one authentication method. Leave the fields for the other methods empty.
5. Choose an **Output Format**, either CSV or JSON Lines, and choose whether to flatten your records to the root level.
6. Make sure the machine running Airbyte can reach Azure. If your storage account restricts network access, allow traffic from that machine. On Airbyte Cloud, add Airbyte's [IP addresses](/platform/operating-airbyte/ip-allowlist) to the storage account's firewall rules.
7. Select **Set up destination**. The connection check uploads a test blob, reads its metadata, lists the container, and deletes the blob again, so it fails if your credentials are missing any of those permissions.

## Namespace support

This destination supports [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces). Airbyte uses the namespace as a directory in the blob path, above the stream name.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version  | Date       | Pull Request                                               | Subject                                                                                                                                                         |
|:---------|:-----------|:-----------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1.1.7 | 2026-05-20 | [78243](https://github.com/airbytehq/airbyte/pull/78243) | Keep existing blobs when a source stream fails partway through an overwrite sync. |
| 1.1.6 | 2026-01-26 | [72355](https://github.com/airbytehq/airbyte/pull/72355) | Fix sync failures for sources with empty schemas by upgrading CDK to 0.2.1 |
| 1.1.5 | 2026-01-20 | [72301](https://github.com/airbytehq/airbyte/pull/72301) | Upgrade CDK to 0.2.0 |
| 1.1.4 | 2025-11-05 | [69127](https://github.com/airbytehq/airbyte/pull/69127) | Upgrade to Bulk CDK 0.1.61. |
| 1.1.3 | 2025-10-21 | [67153](https://github.com/airbytehq/airbyte/pull/67153) | Implement new proto schema implementation |
| 1.1.2 | 2025-10-06 | [67078](https://github.com/airbytehq/airbyte/pull/67078) | Remove memory limit for sync jobs to improve performance and resource utilization. |
| 1.1.1 | 2025-09-10 | [66139](https://github.com/airbytehq/airbyte/pull/66139)   | Fix inconsistent field name casing and improve tooltip clarity. Field names now use consistent title casing and tooltips reference exact field names. |
| 1.1.0 | 2025-09-05 | [65933](https://github.com/airbytehq/airbyte/pull/65933)   | Add support for Azure Entra ID (Service Principal) authentication. You can now authenticate using Azure AD tenant ID, client ID, and client secret. |
| 1.0.4 | 2025-08-07 | [64556](https://github.com/airbytehq/airbyte/pull/64556)   | Promoting release candidate 1.0.4-rc.1 to a main version. |
| 1.0.4-rc.1 | 2025-08-05 | [59710](https://github.com/airbytehq/airbyte/pull/59710)   | Release Azure blob destination on latest CDK                                                                                                                    |
| 1.0.3    | 2025-05-07 | [59710](https://github.com/airbytehq/airbyte/pull/59710)   | CDK backpressure bugfix                                                                                                                                         |
| 1.0.2    | 2025-04-14 | [57563](https://github.com/airbytehq/airbyte/pull/57563)   | Fix signature spec example                                                                                                                                      |
| 1.0.1    | 2025-04-09 | [57541](https://github.com/airbytehq/airbyte/pull/57541)   | Fix metadata to actually certify.                                                                                                                               |
| 1.0.0    | 2025-04-03 | [56391](https://github.com/airbytehq/airbyte/pull/56391)   | Bring into compliance with modern connector standards; certify connector.                                                                                       |
| 0.2.5    | 2025-03-21 | [55906](https://github.com/airbytehq/airbyte/pull/55906)   | Upgrade to airbyte/java-connector-base:2.0.1 to be M4 compatible.                                                                                               |
| 0.2.4    | 2025-01-10 | [51507](https://github.com/airbytehq/airbyte/pull/51507)   | Use a non root base image                                                                                                                                       |
| 0.2.3    | 2024-12-18 | [49910](https://github.com/airbytehq/airbyte/pull/49910)   | Use a base image: airbyte/java-connector-base:1.0.0                                                                                                             |
| 0.2.2    | 2024-06-12 | [\#38061](https://github.com/airbytehq/airbyte/pull/38061) | File Extensions added for the output files                                                                                                                      |
| 0.2.1    | 2023-09-13 | [\#30412](https://github.com/airbytehq/airbyte/pull/30412) | Switch noisy logging to debug                                                                                                                                   |
| 0.2.0    | 2023-01-18 | [\#21467](https://github.com/airbytehq/airbyte/pull/21467) | Support spilling of objects exceeding configured size threshold                                                                                                 |
| 0.1.6    | 2022-08-08 | [\#15318](https://github.com/airbytehq/airbyte/pull/15318) | Support per-stream state                                                                                                                                        |
| 0.1.5    | 2022-06-16 | [\#13852](https://github.com/airbytehq/airbyte/pull/13852) | Updated stacktrace format for any trace message errors                                                                                                          |
| 0.1.4    | 2022-05-17 | [12820](https://github.com/airbytehq/airbyte/pull/12820)   | Improved 'check' operation performance                                                                                                                          |
| 0.1.3    | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256)   | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                                                                                    |
| 0.1.2    | 2022-01-20 | [\#9682](https://github.com/airbytehq/airbyte/pull/9682)   | Each data synchronization for each stream is written to a new blob to the folder with stream name.                                                              |
| 0.1.1    | 2021-12-29 | [\#9190](https://github.com/airbytehq/airbyte/pull/9190)   | Added BufferedOutputStream wrapper to blob output stream to improve performance and fix issues with 50,000 block limit. Also disabled autoflush on PrintWriter. |
| 0.1.0    | 2021-08-30 | [\#5332](https://github.com/airbytehq/airbyte/pull/5332)   | Initial release with JSONL and CSV output.                                                                                                                      |

</details>
