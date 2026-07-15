# Google Cloud Storage (GCS)

## Overview

This destination writes data to a GCS bucket.

The Airbyte GCS destination allows you to sync data to cloud storage buckets. Each stream is written to its own directory under the bucket.

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | Yes |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | No |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | No |

## Getting started

### Requirements

1. Allow connections from Airbyte server to your GCS bucket \(if they exist in separate VPCs\).
2. A GCP bucket with credentials.

### Setup guide

- Fill up GCS info
  - **GCS Bucket Name**
    - See [this](https://cloud.google.com/storage/docs/creating-buckets) for instructions on how to create a GCS bucket. The bucket cannot have a retention policy. Set Protection Tools to none or Object versioning.
  - **GCS Bucket Region**
  - **HMAC Key Access ID**
    - See [this](https://cloud.google.com/storage/docs/authentication/managing-hmackeys) on how to generate an access key. For more information on hmac keys please reference the [GCP docs](https://cloud.google.com/storage/docs/authentication/hmackeys)
    - We recommend creating an Airbyte-specific user or service account. This user or account will require the following permissions for the bucket:
      ```
      storage.multipartUploads.abort
      storage.multipartUploads.create
      storage.objects.create
      storage.objects.delete
      storage.objects.get
      storage.objects.list
      ```
      You can set those by going to the permissions tab in the GCS bucket and adding the appropriate the email address of the service account or user and adding the aforementioned permissions.
  - **Secret Access Key**
    - Corresponding key to the above access ID.
- Make sure your GCS bucket is accessible from the machine running Airbyte. This depends on your networking setup. The easiest way to verify if Airbyte is able to connect to your GCS bucket is via the check connection tool in the UI.

## Configuration

| Parameter          |  Type  | Required | Notes                                                                                                                                                                                                                                                                      |
|:-------------------|:------:|:--------:|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| GCS Bucket Name    | string |   Yes    | Name of the bucket to sync data into.                                                                                                                                                                                                                                      |
| GCS Bucket Path    | string |   Yes    | Subdirectory under the above bucket to sync the data into.                                                                                                                                                                                                                 |
| GCS Bucket Region  | string |    No    | GCS bucket region. Defaults to `us`. See [here](https://cloud.google.com/storage/docs/locations) for all region codes.                                                                                                                                                     |
| HMAC Access Key    | string |   Yes    | HMAC key access ID for the GCS bucket. When linked to a service account, this ID is 61 characters long; when linked to a user account, it is 24 characters long. See [HMAC key](https://cloud.google.com/storage/docs/authentication/hmackeys) for details.                 |
| HMAC Secret        | string |   Yes    | The corresponding secret for the access key. It is a 40-character base-64 encoded string.                                                                                                                                                                                  |
| Output Format      | object |   Yes    | Format-specific configuration. See below [for details](https://docs.airbyte.com/integrations/destinations/gcs#output-schema).                                                                                                                                              |
| GCS Path Format    | string |    No    | Format string for the directory layout under the bucket path. Defaults to `${NAMESPACE}/${STREAM_NAME}/${YEAR}_${MONTH}_${DAY}_${EPOCH}_`. See [GCS Path Format](#gcs-path-format) for available variables.                                                                |
| File Name Pattern  | string |    No    | Pattern for output file names. Defaults to `{part_number}{format_extension}`. See [File Name Pattern](#file-name-pattern) for available variables.                                                                                                                         |

Currently, only the [HMAC key](https://cloud.google.com/storage/docs/authentication/hmackeys) is supported. More credential types will be added in the future, please [submit an issue](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=type%2Fenhancement%2C+needs-triage&template=feature-request.md&title=) with your request.

Both Google-managed and customer-managed encryption keys (CMEK) are supported. You can view the encryption setting under
the "Configuration" tab of your GCS bucket, in the `Encryption type` row.

⚠️ Please note that under "Full Refresh Sync" mode, existing data under each stream's output prefix will be
overwritten before each sync. We recommend you provision a dedicated GCS bucket for this sync to prevent unexpected
data deletion from misconfiguration. ⚠️

The full path of the output data is:

```text
<bucket-name>/<bucket-path>/<source-namespace-if-exists>/<stream-name>/<upload-date>_<upload-millis>_<partition-id>.<format-extension>
```

For example:

```text
testing_bucket/data_output_path/public/users/2021_01_01_1609541171643_0.csv.gz
↑              ↑                ↑      ↑     ↑          ↑             ↑ ↑
|              |                |      |     |          |             | format extension
|              |                |      |     |          |             partition id
|              |                |      |     |          upload time in millis
|              |                |      |     upload date in YYYY_MM_DD
|              |                |      stream name
|              |                source namespace (if it exists)
|              bucket path
bucket name
```

Please note that the stream name may contain a prefix, if it is configured on the connection.

The rationales behind this naming pattern are: 1. Each stream has its own directory. 2. The data output files can be sorted by upload time. 3. The upload time composes of a date part and millis part so that it is both readable and unique.

A data sync may create multiple files as the output files can be partitioned by size (targeting a size of 200MB compressed or lower) .

### GCS Path Format

The **GCS Path Format** field controls the directory structure under the bucket path. The default value is:

```
${NAMESPACE}/${STREAM_NAME}/${YEAR}_${MONTH}_${DAY}_${EPOCH}_
```

The following variables are available for path format:

| Variable         | Description                                           | Example             |
|:-----------------|:------------------------------------------------------|:--------------------|
| `${NAMESPACE}`   | Namespace of the stream (empty if none is configured) | `public`            |
| `${STREAM_NAME}` | Name of the stream                                    | `users`             |
| `${YEAR}`        | Year of the sync (UTC, 4-digit)                       | `2026`              |
| `${MONTH}`       | Month of the sync (UTC, zero-padded)                  | `07`                |
| `${DAY}`         | Day of the sync (UTC, zero-padded)                    | `14`                |
| `${HOUR}`        | Hour of the sync (UTC, zero-padded)                   | `09`                |
| `${MINUTE}`      | Minute of the sync (UTC, zero-padded)                 | `30`                |
| `${SECOND}`      | Second of the sync (UTC, zero-padded)                 | `45`                |
| `${MILLISECOND}` | Millisecond of the day (UTC)                          | `0123`              |
| `${EPOCH}`       | Milliseconds since Unix epoch                         | `1752489045000`     |
| `${UUID}`        | Random UUID                                           | `a1b2c3d4-e5f6-...` |
| `${SYNC_ID}`     | Unique ID of the sync                                 | `101`               |

### File Name Pattern

The **File Name Pattern** field controls the name of each output file. The default value is:

```
{part_number}{format_extension}
```

The following variables are available for file name pattern:

| Variable             | Description                                  | Example         |
|:---------------------|:---------------------------------------------|:----------------|
| `{date}`             | Date of the sync in `yyyy_MM_dd` format      | `2026_07_14`    |
| `{date:yyyy_MM}`     | Date of the sync in `yyyy_MM` format         | `2026_07`       |
| `{timestamp}`        | Current wall-clock timestamp in milliseconds | `1752489045123` |
| `{part_number}`      | File part number (0, 1, 2, ...)              | `0`             |
| `{sync_id}`          | Unique ID of the sync                        | `101`           |
| `{format_extension}` | File extension including compression suffix  | `.csv.gz`       |

:::note
Path format variables use the `${VARIABLE}` syntax, while file name pattern variables use the `{variable}` syntax.
Multiple `/` characters in the resolved path are collapsed into a single `/`.
:::

## Output Schema

Each stream will be outputted to its dedicated directory according to the configuration. The complete datastore of each stream includes all the output files under that directory. You can think of the directory as equivalent of a Table in the database world.

- Under Full Refresh Sync mode, old output files will be purged before new files are created.
- Under Incremental - Append Sync mode, new output files will be added that only contain the new data.

### Avro

[Apache Avro](https://avro.apache.org/) serializes data in a compact binary format. Currently, the Airbyte GCS Avro
connector always uses the [binary encoding](https://avro.apache.org/docs/1.12.0/specification/#binary-encoding), and
assumes that all data records follow the same schema.

#### Configuration

Here is the available compression codecs:

- No compression
- `deflate`
  - Compression level
    - Range `[0, 9]`. Default to 0.
    - Level 0: no compression & fastest.
    - Level 9: best compression & slowest.
- `bzip2`
- `xz`
  - Compression level
    - Range `[0, 9]`. Default to 6.
    - Level 0-3 are fast with medium compression.
    - Level 4-6 are fairly slow with high compression.
    - Level 7-9 are like level 6 but use bigger dictionaries and have higher memory requirements. Unless the uncompressed size of the file exceeds 8 MiB, 16 MiB, or 32 MiB, it is waste of memory to use the presets 7, 8, or 9, respectively.
- `zstandard`
  - Compression level
    - Range `[-5, 22]`. Default to 3.
    - Negative levels are 'fast' modes akin to `lz4` or `snappy`.
    - Levels above 9 are generally for archival purposes.
    - Levels above 18 use a lot of memory.
  - Include checksum
    - If set to `true`, a checksum will be included in each data block.
- `snappy`

#### Data schema

Under the hood, an Airbyte data stream in Json schema is first converted to an Avro schema, then the Json object is converted to an Avro record. Because the data stream can come from any data source, the Json to Avro conversion process has arbitrary rules and limitations. Learn more about how source data is converted to Avro and the current limitations [here](https://docs.airbyte.com/understanding-airbyte/json-avro-conversion).

### CSV

With the CSV output, it is possible to normalize \(flatten\) the data blob to multiple columns.

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

| Field Name | Type   | Description                                                                                                               |
| :--------- | :----- | :------------------------------------------------------------------------------------------------------------------------ |
| `field`    | string | The name of the field that changed.                                                                                       |
| `change`   | string | The type of change (eg, `NULLED`, `TRUNCATED`).                                                                           |
| `reason`   | string | The reason for the change, including its system of origin (ie, whether it was a source, destination, or platform error). |

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

| `_airbyte_raw_id`                      | `_airbyte_extracted_at` | `_airbyte_generation_id` | `_airbyte_meta`                     | `_airbyte_data`                                                |
| :------------------------------------- | :---------------------- | :----------------------- | ----------------------------------- | :------------------------------------------------------------- |
| `26d73cde-7eb1-4e1e-b7db-a4c03b4cf206` | 1622135805000           | 11                       | `{"changes":[], "sync_id": 10111 }` | `{ "user_id": 123, name: { "first": "John", "last": "Doe" } }` |

With root level normalization, the output CSV is:

| `_airbyte_raw_id`                      | `_airbyte_extracted_at` | `_airbyte_generation_id` | `_airbyte_meta`                     | `user_id` | `name`                               |
| :------------------------------------- | :---------------------- | :----------------------- | ----------------------------------- | :-------- | :----------------------------------- |
| `26d73cde-7eb1-4e1e-b7db-a4c03b4cf206` | 1622135805000           | 11                       | `{"changes":[], "sync_id": 10111 }` | 123       | `{ "first": "John", "last": "Doe" }` |

Output files can be compressed. In v1.0.0 and later, CSV output is **GZIP-compressed by default** (`.csv.gz`). Set
`format.compression.compression_type = "No Compression"` for uncompressed `.csv` output.

### JSON Lines \(JSONL\)

[Json Lines](https://jsonlines.org/) is a text format with one JSON per line. Like CSV, JSONL supports optional *
*flattening** (`"No flattening"` or `"Root level flattening"`). Each line has a structure as follows:

```json
{
  "_airbyte_raw_id": "<uuid>",
  "_airbyte_extracted_at": "<timestamp-in-millis>",
  "_airbyte_generation_id": "<generation-id>",
  "_airbyte_meta": "<json-meta>",
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

```text
{ "_airbyte_raw_id": "26d73cde-7eb1-4e1e-b7db-a4c03b4cf206", "_airbyte_extracted_at": "1622135805000", "_airbyte_generation_id": "11", "_airbyte_meta": { "changes": [], "sync_id": 10111 }, "_airbyte_data": { "user_id": 123, "name": { "first": "John", "last": "Doe" } } }
{ "_airbyte_raw_id": "0a61de1b-9cdd-4455-a739-93572c9a5f20", "_airbyte_extracted_at": "1631948170000", "_airbyte_generation_id": "12", "_airbyte_meta": { "changes": [], "sync_id": 10112 }, "_airbyte_data": { "user_id": 456, "name": { "first": "Jane", "last": "Roe" } } }
```

Output files can be compressed. In v1.0.0 and later, JSONL output is **GZIP-compressed by default** (`.jsonl.gz`). Set
`format.compression.compression_type = "No Compression"` for uncompressed `.jsonl` output.

### Parquet

#### Configuration

The following configuration is available to configure the Parquet output:

| Parameter                 |  Type   |    Default     | Description                                                                                                                                                                                                                       |
| :------------------------ | :-----: | :------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `compression_codec`       |  enum   | `UNCOMPRESSED` | **Compression algorithm**. Available candidates are: `UNCOMPRESSED`, `SNAPPY`, `GZIP`, `LZO`, `BROTLI`, `LZ4`, and `ZSTD`.                                                                                                        |
| `block_size_mb`           | integer |   128 \(MB\)   | **Block size \(row group size\)** in MB. This is the size of a row group being buffered in memory. It limits the memory usage when writing. Larger values will improve the IO when reading, but consume more memory when writing. |
| `max_padding_size_mb`     | integer |    8 \(MB\)    | **Max padding size** in MB. This is the maximum size allowed as padding to align row groups. This is also the minimum size of a row group.                                                                                        |
| `page_size_kb`            | integer |  1024 \(KB\)   | **Page size** in KB. The page size is for compression. A block is composed of pages. A page is the smallest unit that must be read fully to access a single record. If this value is too small, the compression will deteriorate. |
| `dictionary_page_size_kb` | integer |  1024 \(KB\)   | **Dictionary Page Size** in KB. There is one dictionary page per column per row group when dictionary encoding is used. The dictionary page size works like the page size but for dictionary.                                     |
| `dictionary_encoding`     | boolean |     `true`     | **Dictionary encoding**. This parameter controls whether dictionary encoding is turned on.                                                                                                                                        |

These parameters are related to the `ParquetOutputFormat`. See the [Java doc](https://www.javadoc.io/doc/org.apache.parquet/parquet-hadoop/1.12.0/org/apache/parquet/hadoop/ParquetOutputFormat.html) for more details. Also see [Parquet documentation](https://parquet.apache.org/docs/file-format/configurations) for their recommended configurations \(512 - 1024 MB block size, 8 KB page size\).

#### Data schema

Under the hood, an Airbyte data stream in Json schema is first converted to an Avro schema, then the Json object is converted to an Avro record, and finally the Avro record is outputted to the Parquet format. Because the data stream can come from any data source, the Json to Avro conversion process has arbitrary rules and limitations. Learn more about how source data is converted to Avro and the current limitations [here](https://docs.airbyte.com/understanding-airbyte/json-avro-conversion).

## Namespace support

This destination uses [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces) as part of
the output directory structure. The stream namespace is included as a path component via the `${NAMESPACE}` variable in
the [GCS Path Format](#gcs-path-format). If a stream has no namespace configured, the namespace segment is omitted from
the path.

## Upgrading to 1.0.0

See the [GCS Migration Guide](gcs-migrations.md) for detailed upgrade instructions.

## Performance

The connector uses tuned object-storage pipeline defaults and exposes no performance-tuning
settings, matching the other Bulk-CDK object-storage destinations. Throughput scales with the
destination pod's CPU/memory and — for SOCKET-mode syncs — with the source's read concurrency and
the number of streams synced in parallel. In SOCKET mode the CDK sizes the socket count, part size,
and upload parallelism from the negotiated CPU limits automatically.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|:--------|:-----------|:---------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1.0.0   | 2026-07-02 | [81376](https://github.com/airbytehq/airbyte/pull/81376) | Migrate to the Bulk Load CDK for significantly higher throughput. Preserves HMAC-key auth and AVRO+snappy/CSV/JSONL/Parquet output, with the same object paths and `<date>_<epoch>_0` file names as 0.4.x (verified byte-for-byte against a production object — see "Upgrading to 1.0.0"). Advertises the SOCKET/PROTOBUF high-throughput data channel (`connectorIPCOptions`), with STDIO/JSONL as the negotiated fallback. Ships tuned ObjectLoader defaults with no user-facing tuning knobs, matching the other Bulk-CDK object-storage destinations. |
| 0.4.9   | 2025-03-21 | [55906](https://github.com/airbytehq/airbyte/pull/55906) | Use M4 Compatible base image.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| 0.4.8   | 2025-01-10 | [51479](https://github.com/airbytehq/airbyte/pull/51479) | Use a non root base image                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| 0.4.7   | 2024-12-18 | [49884](https://github.com/airbytehq/airbyte/pull/49884) | Use a base image: airbyte/java-connector-base:1.0.0                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| 0.4.6   | 2024-02-15 | [35285](https://github.com/airbytehq/airbyte/pull/35285) | Adopt CDK 0.20.8                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| 0.4.5   | 2024-02-08 | [34745](https://github.com/airbytehq/airbyte/pull/34745) | Adopt CDK 0.19.0                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| 0.4.4   | 2023-07-14 | [28345](https://github.com/airbytehq/airbyte/pull/28345) | Increment patch to trigger a rebuild                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| 0.4.3   | 2023-07-05 | [27936](https://github.com/airbytehq/airbyte/pull/27936) | Internal code update                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| 0.4.2   | 2023-06-30 | [27891](https://github.com/airbytehq/airbyte/pull/27891) | Internal code update                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| 0.4.1   | 2023-06-28 | [27268](https://github.com/airbytehq/airbyte/pull/27268) | Internal code update                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| 0.4.0   | 2023-06-26 | [27725](https://github.com/airbytehq/airbyte/pull/27725) | License Update: Elv2                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| 0.3.0   | 2023-04-28 | [25570](https://github.com/airbytehq/airbyte/pull/25570) | Fix: all integer schemas should be converted to Avro longs                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 0.2.17  | 2023-04-27 | [25346](https://github.com/airbytehq/airbyte/pull/25346) | Internal code cleanup                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| 0.2.16  | 2023-03-17 | [23788](https://github.com/airbytehq/airbyte/pull/23788) | S3-Parquet: added handler to process null values in arrays                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 0.2.15  | 2023-03-10 | [23466](https://github.com/airbytehq/airbyte/pull/23466) | Changed S3 Avro type from Int to Long                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| 0.2.14  | 2022-11-23 | [21682](https://github.com/airbytehq/airbyte/pull/21682) | Add support for buckets with Customer-Managed Encryption Key                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| 0.2.13  | 2023-01-18 | [21087](https://github.com/airbytehq/airbyte/pull/21087) | Wrap Authentication Errors as Config Exceptions                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| 0.2.12  | 2022-10-18 | [17901](https://github.com/airbytehq/airbyte/pull/17901) | Fix logging to GCS                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| 0.2.11  | 2022-09-01 | [16243](https://github.com/airbytehq/airbyte/pull/16243) | Fix Json to Avro conversion when there is field name clash from combined restrictions (`anyOf`, `oneOf`, `allOf` fields)                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| 0.2.10  | 2022-08-05 | [14801](https://github.com/airbytehq/airbyte/pull/14801) | Fix multiple log bindings                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| 0.2.9   | 2022-06-24 | [14114](https://github.com/airbytehq/airbyte/pull/14114) | Remove "additionalProperties": false from specs for connectors with staging                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| 0.2.8   | 2022-06-17 | [13753](https://github.com/airbytehq/airbyte/pull/13753) | Deprecate and remove PART_SIZE_MB fields from connectors based on StreamTransferManager                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| 0.2.7   | 2022-06-14 | [13483](https://github.com/airbytehq/airbyte/pull/13483) | Added support for int, long, float data types to Avro/Parquet formats.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| 0.2.6   | 2022-05-17 | [12820](https://github.com/airbytehq/airbyte/pull/12820) | Improved 'check' operation performance                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| 0.2.5   | 2022-05-04 | [12578](https://github.com/airbytehq/airbyte/pull/12578) | In JSON to Avro conversion, log JSON field values that do not follow Avro schema for debugging.                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| 0.2.4   | 2022-04-22 | [12167](https://github.com/airbytehq/airbyte/pull/12167) | Add gzip compression option for CSV and JSONL formats.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| 0.2.3   | 2022-04-22 | [11795](https://github.com/airbytehq/airbyte/pull/11795) | Fix the connection check to verify the provided bucket path.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| 0.2.2   | 2022-04-05 | [11728](https://github.com/airbytehq/airbyte/pull/11728) | Properly clean-up bucket when running OVERWRITE sync mode                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| 0.2.1   | 2022-04-05 | [11499](https://github.com/airbytehq/airbyte/pull/11499) | Updated spec and documentation.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| 0.2.0   | 2022-04-04 | [11686](https://github.com/airbytehq/airbyte/pull/11686) | Use serialized buffering strategy to reduce memory consumption; compress CSV and JSONL formats.                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| 0.1.22  | 2022-02-12 | [10256](https://github.com/airbytehq/airbyte/pull/10256) | Add JVM flag to exist on OOME.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| 0.1.21  | 2022-02-12 | [10299](https://github.com/airbytehq/airbyte/pull/10299) | Fix connection check to require only the necessary permissions.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| 0.1.20  | 2022-01-11 | [9367](https://github.com/airbytehq/airbyte/pull/9367)   | Avro & Parquet: support array field with unknown item type; default any improperly typed field to string.                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| 0.1.19  | 2022-01-10 | [9121](https://github.com/airbytehq/airbyte/pull/9121)   | Fixed check method for GCS mode to verify if all roles assigned to user                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| 0.1.18  | 2021-12-30 | [8809](https://github.com/airbytehq/airbyte/pull/8809)   | Update connector fields title/description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| 0.1.17  | 2021-12-21 | [8574](https://github.com/airbytehq/airbyte/pull/8574)   | Added namespace to Avro and Parquet record types                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| 0.1.16  | 2021-12-20 | [8974](https://github.com/airbytehq/airbyte/pull/8974)   | Release a new version to ensure there is no excessive logging.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| 0.1.15  | 2021-12-03 | [8386](https://github.com/airbytehq/airbyte/pull/8386)   | Add new GCP regions                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| 0.1.14  | 2021-12-01 | [7732](https://github.com/airbytehq/airbyte/pull/7732)   | Support timestamp in Avro and Parquet                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| 0.1.13  | 2021-11-03 | [7288](https://github.com/airbytehq/airbyte/issues/7288) | Support Json `additionalProperties`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| 0.1.2   | 2021-09-12 | [5720](https://github.com/airbytehq/airbyte/issues/5720) | Added configurable block size for stream. Each stream is limited to 10,000 by GCS                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| 0.1.1   | 2021-08-26 | [5296](https://github.com/airbytehq/airbyte/issues/5296) | Added storing gcsCsvFileLocation property for CSV format. This is used by destination-bigquery \(GCS Staging upload type\)                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 0.1.0   | 2021-07-16 | [4329](https://github.com/airbytehq/airbyte/pull/4784)   | Initial release.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |

</details>
