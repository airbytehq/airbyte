# Google Cloud Storage (GCS)

## Overview

This destination writes data to GCS bucket.

The Airbyte GCS destination allows you to sync data to cloud storage buckets. Each stream is written to its own directory under the bucket.

### Sync overview

#### Features

| Feature                       | Support | Notes                                                                                        |
| :---------------------------- | :-----: | :------------------------------------------------------------------------------------------- |
| Full Refresh Sync             |   ✅    | Warning: this mode deletes all previously synced data in the configured bucket path.         |
| Incremental - Append Sync     |   ✅    |                                                                                              |
| Incremental - Deduped History |   ❌    | As this connector does not support dbt, we don't support this sync mode on this destination. |
| Namespaces                    |   ❌    | Setting a specific bucket path is equivalent to having separate namespaces.                  |

## Configuration

| Parameter          |  Type   | Notes                                                                                                                                                                                                                                                                       |
| :----------------- | :-----: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GCS Bucket Name    | string  | Name of the bucket to sync data into.                                                                                                                                                                                                                                       |
| GCS Bucket Path    | string  | Subdirectory under the above bucket to sync the data into.                                                                                                                                                                                                                  |
| GCS Region         | string  | See [here](https://cloud.google.com/storage/docs/locations) for all region codes.                                                                                                                                                                                           |
| HMAC Key Access ID | string  | HMAC key access ID . The access ID for the GCS bucket. When linked to a service account, this ID is 61 characters long; when linked to a user account, it is 24 characters long. See [HMAC key](https://cloud.google.com/storage/docs/authentication/hmackeys) for details. |
| HMAC Key Secret    | string  | The corresponding secret for the access ID. It is a 40-character base-64 encoded string.                                                                                                                                                                                    |
| Format             | object  | Format specific configuration. See below [for details](https://docs.airbyte.com/integrations/destinations/gcs#output-schema).                                                                                                                                               |
| Part Size          | integer | Arg to configure a block size. Max allowed blocks by GCS = 10,000, i.e. max stream size = blockSize \* 10,000 blocks.                                                                                                                                                       |

Currently, only the [HMAC key](https://cloud.google.com/storage/docs/authentication/hmackeys) is supported. More credential types will be added in the future, please [submit an issue](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=type%2Fenhancement%2C+needs-triage&template=feature-request.md&title=) with your request.

Additionally, your bucket must be encrypted using a Google-managed encryption key (this is the default setting when creating a new bucket). We currently do not support buckets using customer-managed encryption keys (CMEK). You can view this setting under the "Configuration" tab of your GCS bucket, in the `Encryption type` row.

⚠️ Please note that under "Full Refresh Sync" mode, data in the configured bucket and path will be wiped out before each sync. We recommend you to provision a dedicated S3 resource for this sync to prevent unexpected data deletion from misconfiguration. ⚠️

The full path of the output data is:

```text
<bucket-name>/<sorce-namespace-if-exists>/<stream-name>/<upload-date>-<upload-mills>-<partition-id>.<format-extension>
```

For example:

```text
testing_bucket/data_output_path/public/users/2021_01_01_1609541171643_0.csv.gz
↑              ↑                ↑      ↑     ↑          ↑             ↑ ↑
|              |                |      |     |          |             | format extension
|              |                |      |     |          |             partition id
|              |                |      |     |          upload time in millis
|              |                |      |     upload date in YYYY-MM-DD
|              |                |      stream name
|              |                source namespace (if it exists)
|              bucket path
bucket name
```

Please note that the stream name may contain a prefix, if it is configured on the connection.

The rationales behind this naming pattern are: 1. Each stream has its own directory. 2. The data output files can be sorted by upload time. 3. The upload time composes of a date part and millis part so that it is both readable and unique.

A data sync may create multiple files as the output files can be partitioned by size (targeting a size of 200MB compressed or lower) .

## Output Schema

Each stream will be outputted to its dedicated directory according to the configuration. The complete datastore of each stream includes all the output files under that directory. You can think of the directory as equivalent of a Table in the database world.

- Under Full Refresh Sync mode, old output files will be purged before new files are created.
- Under Incremental - Append Sync mode, new output files will be added that only contain the new data.

### Avro

[Apache Avro](https://avro.apache.org/) serializes data in a compact binary format. Currently, the Airbyte S3 Avro connector always uses the [binary encoding](http://avro.apache.org/docs/current/spec.html#binary_encoding), and assumes that all data records follow the same schema.

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

Like most of the other Airbyte destination connectors, usually the output has three columns: a UUID, an emission timestamp, and the data blob. With the CSV output, it is possible to normalize \(flatten\) the data blob to multiple columns.

| Column                | Condition                                                                                         | Description                                                              |
| :-------------------- | :------------------------------------------------------------------------------------------------ | :----------------------------------------------------------------------- |
| `_airbyte_ab_id`      | Always exists                                                                                     | A uuid assigned by Airbyte to each processed record.                     |
| `_airbyte_emitted_at` | Always exists.                                                                                    | A timestamp representing when the event was pulled from the data source. |
| `_airbyte_data`       | When no normalization \(flattening\) is needed, all data reside under this column as a json blob. |                                                                          |
| root level fields     | When root level normalization \(flattening\) is selected, the root level fields are expanded.     |                                                                          |

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

| `_airbyte_ab_id`                       | `_airbyte_emitted_at` | `_airbyte_data`                                                |
| :------------------------------------- | :-------------------- | :------------------------------------------------------------- |
| `26d73cde-7eb1-4e1e-b7db-a4c03b4cf206` | 1622135805000         | `{ "user_id": 123, name: { "first": "John", "last": "Doe" } }` |

With root level normalization, the output CSV is:

| `_airbyte_ab_id`                       | `_airbyte_emitted_at` | `user_id` | `name`                               |
| :------------------------------------- | :-------------------- | :-------- | :----------------------------------- |
| `26d73cde-7eb1-4e1e-b7db-a4c03b4cf206` | 1622135805000         | 123       | `{ "first": "John", "last": "Doe" }` |

Output files can be compressed. The default option is GZIP compression. If compression is selected, the output filename will have an extra extension (GZIP: `.csv.gz`).

### JSON Lines \(JSONL\)

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

```text
{ "_airbyte_ab_id": "26d73cde-7eb1-4e1e-b7db-a4c03b4cf206", "_airbyte_emitted_at": "1622135805000", "_airbyte_data": { "user_id": 123, "name": { "first": "John", "last": "Doe" } } }
{ "_airbyte_ab_id": "0a61de1b-9cdd-4455-a739-93572c9a5f20", "_airbyte_emitted_at": "1631948170000", "_airbyte_data": { "user_id": 456, "name": { "first": "Jane", "last": "Roe" } } }
```

Output files can be compressed. The default option is GZIP compression. If compression is selected, the output filename will have an extra extension (GZIP: `.jsonl.gz`).

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

## Getting started

### Requirements

1. Allow connections from Airbyte server to your GCS cluster \(if they exist in separate VPCs\).
2. An GCP bucket with credentials \(for the COPY strategy\).

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

## CHANGELOG

| Version | Date       | Pull Request                                               | Subject                                                                                                                    |
| :------ | :--------- | :--------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------- |
| 0.4.4   | 2023-07-14 | [#28345](https://github.com/airbytehq/airbyte/pull/28345) | Increment patch to trigger a rebuild                                                                                       |
| 0.4.3   | 2023-07-05 | [#27936](https://github.com/airbytehq/airbyte/pull/27936)  | Internal code update                                                                                                       |
| 0.4.2   | 2023-06-30 | [#27891](https://github.com/airbytehq/airbyte/pull/27891)  | Internal code update                                                                                                       |
| 0.4.1   | 2023-06-28 | [#27268](https://github.com/airbytehq/airbyte/pull/27268)  | Internal code update                                                                                                       |
| 0.4.0   | 2023-06-26 | [#27725](https://github.com/airbytehq/airbyte/pull/27725)  | License Update: Elv2                                                                                                       |
| 0.3.0   | 2023-04-28 | [#25570](https://github.com/airbytehq/airbyte/pull/25570)  | Fix: all integer schemas should be converted to Avro longs                                                                 |
| 0.2.17  | 2023-04-27 | [#25346](https://github.com/airbytehq/airbyte/pull/25346)  | Internal code cleanup                                                                                                      |
| 0.2.16  | 2023-03-17 | [#23788](https://github.com/airbytehq/airbyte/pull/23788)  | S3-Parquet: added handler to process null values in arrays                                                                 |
| 0.2.15  | 2023-03-10 | [#23466](https://github.com/airbytehq/airbyte/pull/23466)  | Changed S3 Avro type from Int to Long                                                                                      |
| 0.2.14  | 2023-11-23 | [\#21682](https://github.com/airbytehq/airbyte/pull/21682) | Add support for buckets with Customer-Managed Encryption Key                                                               |
| 0.2.13  | 2023-01-18 | [#21087](https://github.com/airbytehq/airbyte/pull/21087)  | Wrap Authentication Errors as Config Exceptions                                                                            |
| 0.2.12  | 2022-10-18 | [\#17901](https://github.com/airbytehq/airbyte/pull/17901) | Fix logging to GCS                                                                                                         |
| 0.2.11  | 2022-09-01 | [\#16243](https://github.com/airbytehq/airbyte/pull/16243) | Fix Json to Avro conversion when there is field name clash from combined restrictions (`anyOf`, `oneOf`, `allOf` fields)   |
| 0.2.10  | 2022-08-05 | [\#14801](https://github.com/airbytehq/airbyte/pull/14801) | Fix multiple log bindings                                                                                                  |
| 0.2.9   | 2022-06-24 | [\#14114](https://github.com/airbytehq/airbyte/pull/14114) | Remove "additionalProperties": false from specs for connectors with staging                                                |
| 0.2.8   | 2022-06-17 | [\#13753](https://github.com/airbytehq/airbyte/pull/13753) | Deprecate and remove PART_SIZE_MB fields from connectors based on StreamTransferManager                                    |
| 0.2.7   | 2022-06-14 | [\#13483](https://github.com/airbytehq/airbyte/pull/13483) | Added support for int, long, float data types to Avro/Parquet formats.                                                     |
| 0.2.6   | 2022-05-17 | [12820](https://github.com/airbytehq/airbyte/pull/12820)   | Improved 'check' operation performance                                                                                     |
| 0.2.5   | 2022-05-04 | [\#12578](https://github.com/airbytehq/airbyte/pull/12578) | In JSON to Avro conversion, log JSON field values that do not follow Avro schema for debugging.                            |
| 0.2.4   | 2022-04-22 | [\#12167](https://github.com/airbytehq/airbyte/pull/12167) | Add gzip compression option for CSV and JSONL formats.                                                                     |
| 0.2.3   | 2022-04-22 | [\#11795](https://github.com/airbytehq/airbyte/pull/11795) | Fix the connection check to verify the provided bucket path.                                                               |
| 0.2.2   | 2022-04-05 | [\#11728](https://github.com/airbytehq/airbyte/pull/11728) | Properly clean-up bucket when running OVERWRITE sync mode                                                                  |
| 0.2.1   | 2022-04-05 | [\#11499](https://github.com/airbytehq/airbyte/pull/11499) | Updated spec and documentation.                                                                                            |
| 0.2.0   | 2022-04-04 | [\#11686](https://github.com/airbytehq/airbyte/pull/11686) | Use serialized buffering strategy to reduce memory consumption; compress CSV and JSONL formats.                            |
| 0.1.22  | 2022-02-12 | [\#10256](https://github.com/airbytehq/airbyte/pull/10256) | Add JVM flag to exist on OOME.                                                                                             |
| 0.1.21  | 2022-02-12 | [\#10299](https://github.com/airbytehq/airbyte/pull/10299) | Fix connection check to require only the necessary permissions.                                                            |
| 0.1.20  | 2022-01-11 | [\#9367](https://github.com/airbytehq/airbyte/pull/9367)   | Avro & Parquet: support array field with unknown item type; default any improperly typed field to string.                  |
| 0.1.19  | 2022-01-10 | [\#9121](https://github.com/airbytehq/airbyte/pull/9121)   | Fixed check method for GCS mode to verify if all roles assigned to user                                                    |
| 0.1.18  | 2021-12-30 | [\#8809](https://github.com/airbytehq/airbyte/pull/8809)   | Update connector fields title/description                                                                                  |
| 0.1.17  | 2021-12-21 | [\#8574](https://github.com/airbytehq/airbyte/pull/8574)   | Added namespace to Avro and Parquet record types                                                                           |
| 0.1.16  | 2021-12-20 | [\#8974](https://github.com/airbytehq/airbyte/pull/8974)   | Release a new version to ensure there is no excessive logging.                                                             |
| 0.1.15  | 2021-12-03 | [\#8386](https://github.com/airbytehq/airbyte/pull/8386)   | Add new GCP regions                                                                                                        |
| 0.1.14  | 2021-12-01 | [\#7732](https://github.com/airbytehq/airbyte/pull/7732)   | Support timestamp in Avro and Parquet                                                                                      |
| 0.1.13  | 2021-11-03 | [\#7288](https://github.com/airbytehq/airbyte/issues/7288) | Support Json `additionalProperties`.                                                                                       |
| 0.1.2   | 2021-09-12 | [\#5720](https://github.com/airbytehq/airbyte/issues/5720) | Added configurable block size for stream. Each stream is limited to 10,000 by GCS                                          |
| 0.1.1   | 2021-08-26 | [\#5296](https://github.com/airbytehq/airbyte/issues/5296) | Added storing gcsCsvFileLocation property for CSV format. This is used by destination-bigquery \(GCS Staging upload type\) |
| 0.1.0   | 2021-07-16 | [\#4329](https://github.com/airbytehq/airbyte/pull/4784)   | Initial release.                                                                                                           |
