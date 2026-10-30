# Google Cloud Storage (GCS)

This page guides you through setting up the Google Cloud Storage (GCS) destination connector.

The GCS destination writes each stream to one or more objects in a GCS bucket. You choose the
output format (Avro, CSV, JSON Lines, or Parquet), and you can control the directory layout and the
object names with path templates. The connector authenticates with an HMAC key and uses the
[GCS XML API](https://cloud.google.com/storage/docs/xml-api/overview), which is compatible with
the Amazon S3 API.

:::info
This page covers the **Google Cloud Storage** destination, which writes plain files. If you want an
Apache Iceberg lakehouse on GCS, use the separate
[GCS Data Lake](gcs-data-lake.md) destination instead.
:::

## Prerequisites

- A GCS bucket. [Create a bucket](https://cloud.google.com/storage/docs/creating-buckets) or
  choose an existing one. Bucket retention policies and object holds must allow Airbyte to delete the
  objects it creates (see [Permissions](#permissions)).
- A Google Cloud service account with an
  [HMAC key](https://cloud.google.com/storage/docs/authentication/managing-hmackeys). If your
  organization uses the `constraints/storage.restrictAuthTypes` organization policy, it must allow
  HMAC authentication.
- Network access from the Airbyte deployment to `https://storage.googleapis.com`.

## Setup guide

### Step 1: Create a service account and HMAC key

1. In the Google Cloud console, create a dedicated service account for Airbyte.
2. [Create an HMAC key](https://cloud.google.com/storage/docs/authentication/managing-hmackeys)
   for that service account. Copy the **Access ID** and the **Secret** immediately. Google Cloud
   doesn't display the secret again.

### Step 2: Grant permissions {#permissions}

Grant the service account the **Storage Object User** role (`roles/storage.objectUser`) on the
bucket. If you prefer a custom role, it must include at least these permissions:

```text
storage.objects.create
storage.objects.get
storage.objects.list
storage.objects.delete
storage.multipartUploads.create
storage.multipartUploads.abort
```

Why each permission is needed:

| Permission | Used for |
| :--- | :--- |
| `storage.objects.create`, `storage.multipartUploads.create` | Writing output objects. Objects are uploaded as multipart uploads. |
| `storage.multipartUploads.abort` | Cleaning up a multipart upload that fails part-way. |
| `storage.objects.list`, `storage.objects.get` | Discovering existing objects and reading their generation metadata so Full Refresh - Overwrite can remove stale data. |
| `storage.objects.delete` | Deleting the connection-check probe object and stale objects in Full Refresh - Overwrite syncs. |

### Step 3: Set up the destination in Airbyte

1. In the Airbyte UI, go to **Destinations**, click **New destination**, and select
   **Google Cloud Storage (GCS)**.
2. Enter a **Destination name**.
3. Fill in the fields described in [Configuration](#configuration).
4. Click **Set up destination**. Airbyte runs a connection check that uploads a small probe object
   under the bucket path, lists it, and deletes it.

## Configuration

| Field | Required | Default | Description |
| :--- | :---: | :--- | :--- |
| **GCS Bucket Name** | Yes | | Name of the bucket that receives the data. |
| **GCS Bucket Path** | Yes | | Prefix inside the bucket under which all objects are written. A trailing `/` is optional. |
| **GCS Bucket Region** | No | `us` | Location of the bucket. See [GCS locations](https://cloud.google.com/storage/docs/locations). |
| **Authentication** → **HMAC Access ID** | Yes | | Access ID of the service account's HMAC key. |
| **Authentication** → **HMAC Secret** | Yes | | Secret of the HMAC key. |
| **Output Format** | Yes | | One of Avro, CSV, JSON Lines, or Parquet, with format-specific options. See [Output formats](#output-formats). |
| **GCS Path Format** | No | `${NAMESPACE}/${STREAM_NAME}/${YEAR}_${MONTH}_${DAY}_${EPOCH}_` | Template for the object key below the bucket path. See [GCS Path Format](#gcs-path-format). |
| **File Name Pattern** | No | `{part_number}{format_extension}` | Template for the final file name. See [File Name Pattern](#file-name-pattern). |

### Authentication

The connector supports
[HMAC key authentication](https://cloud.google.com/storage/docs/authentication/hmackeys) only.
Service account JSON keys, OAuth, and Application Default Credentials aren't supported by this
connector. Because the connector talks to the GCS XML API through an S3-compatible client, error
messages from Google Cloud are reported in S3 terminology (for example `AccessDenied` or
`SignatureDoesNotMatch`). See [Troubleshooting](#troubleshooting).

### Encryption

Both Google-managed and customer-managed encryption keys (CMEK) are supported. The connector doesn't
set an encryption key itself; it uses the bucket's default encryption, which you can review in the
**Configuration** tab of the bucket under **Encryption type**.

## Output layout

Every object key is built from the bucket path, the resolved **GCS Path Format**, and the resolved
**File Name Pattern**:

```text
<bucket-name>/<bucket-path>/<resolved GCS Path Format><resolved File Name Pattern>
```

Note that the path format and the file name are concatenated directly. If the path format doesn't end
with `/`, its last segment becomes a prefix of the file name. With the default settings, a sync of
the `users` stream in the `public` namespace produces objects such as:

```text
my-bucket/landing/public/users/2026_10_30_1761820800000_0.csv.gz
↑         ↑       ↑      ↑     ↑          ↑             ↑ ↑
|         |       |      |     |          |             | format extension
|         |       |      |     |          |             part number
|         |       |      |     |          epoch milliseconds of the sync
|         |       |      |     sync date (YYYY_MM_DD)
|         |       |      stream name
|         |       namespace (omitted when the stream has none)
|         bucket path
bucket name
```

A sync writes one or more part files per stream. Files roll over at roughly 200 MB compressed,
so large streams produce several part numbers from the same sync.

### GCS Path Format

**GCS Path Format** is a template for the directory structure under the bucket path. Variables use
the `${VARIABLE}` syntax and are substituted at the start of the sync. Consecutive `/` characters are
collapsed, so an empty `${NAMESPACE}` doesn't create an empty directory.

| Variable | Description | Example |
| :--- | :--- | :--- |
| `${NAMESPACE}` | Namespace of the stream (empty if none) | `public` |
| `${STREAM_NAME}` | Name of the stream | `users` |
| `${YEAR}` | Year of the sync (UTC, four digits) | `2026` |
| `${MONTH}` | Month of the sync (UTC, zero-padded) | `10` |
| `${DAY}` | Day of the sync (UTC, zero-padded) | `30` |
| `${HOUR}` | Hour of the sync (UTC, zero-padded) | `09` |
| `${MINUTE}` | Minute of the sync (UTC, zero-padded) | `30` |
| `${SECOND}` | Second of the sync (UTC, zero-padded) | `45` |
| `${MILLISECOND}` | Millisecond of the sync (UTC) | `0123` |
| `${EPOCH}` | Milliseconds since the Unix epoch at the start of the sync | `1761820800000` |
| `${UUID}` | Random UUID | `a1b2c3d4-e5f6-...` |
| `${SYNC_ID}` | Unique ID of the sync | `101` |

If you leave the field empty, the default template is used. Multiple syncs of the same stream never
overwrite each other's files because `${EPOCH}` (default template) or the part number differs.

#### Example: Hive-style partitions

To lay out each stream as a partitioned table that Hive, Spark, BigQuery external tables, and
similar engines can read, end the template with `/` so that each sync lands in its own partition
directory:

```text
${STREAM_NAME}/dt=${YEAR}-${MONTH}-${DAY}/
```

With the default **File Name Pattern**, this produces:

```text
my-bucket/landing/users/dt=2026-10-30/0.parquet
my-bucket/landing/users/dt=2026-10-30/1.parquet
```

Because the file name no longer includes a timestamp, add `{timestamp}` or `{sync_id}` to the
**File Name Pattern** if you run the stream more than once a day in an append mode:

```text
{sync_id}_{part_number}{format_extension}
```

#### Example: flat layout without the stream name

To write all files for a stream directly under the bucket path, use a template that contains no
directory separators, for example `${YEAR}_${MONTH}_${DAY}_`. You need one connection (or one bucket
path) per stream in this layout; otherwise streams share the same directory.

### File Name Pattern

**File Name Pattern** is a template for the file name. Variables use the `{variable}` syntax.

| Variable | Description | Example |
| :--- | :--- | :--- |
| `{date}` | Date of the sync in `yyyy_MM_dd` format | `2026_10_30` |
| `{date:yyyy_MM}` | Date of the sync in `yyyy_MM` format | `2026_10` |
| `{timestamp}` | Wall-clock time in milliseconds when the file is created | `1761820845123` |
| `{part_number}` | Part number of the file within the sync (0, 1, 2, ...) | `0` |
| `{sync_id}` | Unique ID of the sync | `101` |
| `{format_extension}` | File extension including the compression suffix | `.csv.gz` |

Always include `{part_number}` so that part files from the same sync get distinct names, and
`{format_extension}` so that the extension matches the configured format. If you leave the field
empty, the default pattern is used.

:::note
Path format variables use `${VARIABLE}`; file name variables use `{variable}`.
:::

## Sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | Yes |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | No |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | No |

Each stream's directory holds the complete data set for that stream. Think of the directory as the
equivalent of a table.

- **Append modes** add new files containing only the new data.
- **Full Refresh - Overwrite** writes the new files first and, after the sync completes successfully,
  deletes the stream's objects from earlier generations. Objects are matched by the resolved path
  template (including any `${...}` variables) and by the Airbyte generation ID stored in object
  metadata, so stale files are removed even when the path contains date variables.

:::warning
Full Refresh - Overwrite deletes objects that match the stream's path template under the bucket
path. Use a dedicated bucket or bucket path for Airbyte and double-check your path configuration to
avoid deleting unrelated data.
:::

Objects written by connector versions before 1.0.0 carry no generation metadata and are never
deleted by Full Refresh - Overwrite. Remove them manually after upgrading. See the
[migration guide](gcs-migrations.md).

## Output formats

All formats include these Airbyte metadata fields in every record:

| Field | Description |
| :--- | :--- |
| `_airbyte_raw_id` | UUID assigned by Airbyte to the record. |
| `_airbyte_extracted_at` | Time the record was extracted from the source, in Unix epoch milliseconds. |
| `_airbyte_meta` | Record metadata: `sync_id` and a `changes` array describing any modifications Airbyte made to the record (for example a field set to `NULLED` because it didn't match the declared type). |
| `_airbyte_generation_id` | Generation of the stream the record belongs to. Full Refresh - Overwrite starts a new generation. |

### Avro

[Apache Avro](https://avro.apache.org/) is a compact binary format with an embedded schema. The
connector writes
[binary-encoded](https://avro.apache.org/docs/1.12.0/specification/#binary-encoding) Avro object
container files and derives the Avro schema from the stream's JSON schema. Learn how Airbyte maps
JSON types to Avro, and the current limitations, in
[JSON to Avro conversion](https://docs.airbyte.com/understanding-airbyte/json-avro-conversion).

Available compression codecs:

| Codec | Options |
| :--- | :--- |
| No compression | |
| `deflate` | Compression level `0`–`9` (default `0`). `0` is fastest with no compression, `9` is smallest and slowest. |
| `bzip2` | |
| `xz` | Compression level `0`–`9` (default `6`). `0`–`3` are fast with medium compression; `4`–`6` are slower with high compression; `7`–`9` use larger dictionaries and more memory and only help for files above 8, 16, or 32 MiB respectively. |
| `zstandard` | Compression level `-5`–`22` (default `3`). Negative levels are fast modes similar to `lz4`/`snappy`; levels above `9` are for archival use and levels above `18` use a lot of memory. Optionally include a checksum in each data block. |
| `snappy` | |

### CSV

CSV output supports two flattening modes:

- **No flattening**: the source record is serialized as a JSON string in the `_airbyte_data` column.
- **Root level flattening**: each top-level field of the source record becomes its own column.
  Nested objects and arrays are serialized as JSON strings.

| Column | Present when | Description |
| :--- | :--- | :--- |
| `_airbyte_raw_id` | Always | See [Output formats](#output-formats). |
| `_airbyte_extracted_at` | Always | |
| `_airbyte_meta` | Always | Serialized as a JSON string. |
| `_airbyte_generation_id` | Always | |
| `_airbyte_data` | No flattening | Source record serialized as a JSON string. |
| Source fields | Root level flattening | One column per top-level source field. |

For example, this source record:

```json
{
  "user_id": 123,
  "name": {
    "first": "John",
    "last": "Doe"
  }
}
```

With no flattening:

| `_airbyte_raw_id` | `_airbyte_extracted_at` | `_airbyte_meta` | `_airbyte_generation_id` | `_airbyte_data` |
| :--- | :--- | :--- | :--- | :--- |
| `26d73cde-7eb1-4e1e-b7db-a4c03b4cf206` | 1622135805000 | `{"sync_id":10111,"changes":[]}` | 11 | `{"user_id":123,"name":{"first":"John","last":"Doe"}}` |

With root level flattening:

| `_airbyte_raw_id` | `_airbyte_extracted_at` | `_airbyte_meta` | `_airbyte_generation_id` | `user_id` | `name` |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `26d73cde-7eb1-4e1e-b7db-a4c03b4cf206` | 1622135805000 | `{"sync_id":10111,"changes":[]}` | 11 | 123 | `{"first":"John","last":"Doe"}` |

CSV files are **GZIP-compressed by default** (`.csv.gz`). Choose **No Compression** in the format
options to write plain `.csv` files.

### JSON Lines (JSONL)

[JSON Lines](https://jsonlines.org/) writes one JSON object per line. It supports the same
**No flattening** and **Root level flattening** options as CSV. With no flattening, the source
record is nested under `_airbyte_data`; with root level flattening, the source fields appear next to
the Airbyte metadata fields.

Example output with no flattening for two source records:

```json
{"_airbyte_raw_id":"26d73cde-7eb1-4e1e-b7db-a4c03b4cf206","_airbyte_extracted_at":1622135805000,"_airbyte_meta":{"sync_id":10111,"changes":[]},"_airbyte_generation_id":11,"_airbyte_data":{"user_id":123,"name":{"first":"John","last":"Doe"}}}
{"_airbyte_raw_id":"0a61de1b-9cdd-4455-a739-93572c9a5f20","_airbyte_extracted_at":1631948170000,"_airbyte_meta":{"sync_id":10112,"changes":[]},"_airbyte_generation_id":12,"_airbyte_data":{"user_id":456,"name":{"first":"Jane","last":"Roe"}}}
```

JSONL files are **GZIP-compressed by default** (`.jsonl.gz`). Choose **No Compression** to write
plain `.jsonl` files.

Fields that are absent from a source record are absent from the output record as well; the
connector doesn't backfill them with `null`.

### Parquet

[Apache Parquet](https://parquet.apache.org/) is a columnar format. Records are first converted
to Avro using the same mapping as the [Avro](#avro) format, then written as Parquet.

| Option | Type | Default | Description |
| :--- | :---: | :---: | :--- |
| **Compression Codec** | enum | `UNCOMPRESSED` | One of `UNCOMPRESSED`, `SNAPPY`, `GZIP`, `LZO`, `BROTLI`, `LZ4`, `ZSTD`. |
| **Block Size (Row Group Size)** | integer (MB) | `128` | Size of a row group buffered in memory. Larger values improve read performance but use more memory while writing. |
| **Max Padding Size** | integer (MB) | `8` | Maximum padding used to align row groups; also the minimum row group size. |
| **Page Size** | integer (KB) | `1024` | Size of a data page, the smallest unit that must be read to access a record. Very small pages reduce compression efficiency. |
| **Dictionary Page Size** | integer (KB) | `1024` | Size of the dictionary page per column per row group when dictionary encoding is on. |
| **Dictionary Encoding** | boolean | `true` | Whether to use dictionary encoding. |

These options map to Parquet's
[`ParquetOutputFormat`](https://www.javadoc.io/doc/org.apache.parquet/parquet-hadoop/1.12.0/org/apache/parquet/hadoop/ParquetOutputFormat.html)
settings. See the
[Parquet configuration guide](https://parquet.apache.org/docs/file-format/configurations) for
recommended values.

## Namespace support

This destination uses [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces)
through the `${NAMESPACE}` variable in **GCS Path Format**. If a stream has no namespace, the
variable resolves to an empty string and the directory segment is omitted. Stream and namespace
names are sanitized to characters that are safe in object keys.

## Troubleshooting

### Connection check fails with `AccessDenied`

The connector reports Google Cloud errors in S3 terminology because it uses the S3-compatible XML
API. `AccessDenied` means the HMAC key's service account is missing one of the
[required permissions](#permissions) on the bucket, most often `storage.multipartUploads.create` or
`storage.objects.delete`. Grant **Storage Object User** on the bucket or add the missing permissions
to your custom role.

### Connection check fails with `SignatureDoesNotMatch` or `InvalidAccessKeyId`

The HMAC access ID or secret is incorrect, or the key belongs to a different project. Make sure you
copied the secret exactly and that the key is active. If your organization restricts authentication
types, confirm that HMAC keys are allowed by the `constraints/storage.restrictAuthTypes` policy.

### Output objects are written directly under the bucket path with no directory

The **GCS Path Format** doesn't end with `/` and contains no `/` at all, so its resolved value is
used as a file name prefix. Add `/` where you want a directory boundary, or clear the field to use the
default template. In connector versions before 1.0.2, clearing the field could also produce this
layout; upgrade to 1.0.2 or later.

### Old files remain after a Full Refresh - Overwrite sync

Only objects that match the stream's current path template and carry generation metadata are
deleted. Files written by connector versions before 1.0.0, or written under a different
**GCS Path Format**, are left in place. Remove them manually.

## Upgrading to 1.0.0

Version 1.0.0 is a rewrite on the Bulk Load CDK and changes the default compression and output
layout. See the [GCS migration guide](gcs-migrations.md) before upgrading.

## Performance

The connector uses tuned object-storage pipeline defaults and exposes no performance-tuning
settings, matching the other Bulk CDK object-storage destinations. Throughput scales with the
destination pod's CPU and memory and, for socket-mode syncs, with the source's read concurrency and
the number of streams synced in parallel. In socket mode the CDK sizes the socket count, part size,
and upload parallelism from the negotiated CPU limits automatically.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|:--------|:-----------|:---------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1.0.2   | 2026-10-30 | [90272](https://github.com/airbytehq/airbyte/pull/90272) | Promote to certified (GA). Treat blank `gcs_path_format` / `file_name_pattern` as the default patterns; declare `allowedHosts` in metadata. |
| 1.0.1   | 2026-10-22 | [89650](https://github.com/airbytehq/airbyte/pull/89650) | Upgrade to Bulk CDK 1.1.9: fix critical CVEs in Apache MINA (mina-core 2.0.31), MINA SSHD 2.20.0 and BouncyCastle 1.86; netty 4.1.139, Hadoop 3.4.3, Parquet 1.18.1. |
| 1.0.0   | 2026-07-15 | [81376](https://github.com/airbytehq/airbyte/pull/81376) | Migrate to the Bulk Load CDK for significantly higher throughput on large syncs through parallel, back-pressured multipart uploads and SOCKET/PROTOBUF data transfer with compatible sources. Streams larger than approximately 200 MB may produce multiple objects, CSV and JSONL output is GZIP-compressed by default, and Airbyte metadata field names change. See [Upgrading to 1.0.0](gcs-migrations.md#upgrading-to-100).                                                                                                                           |
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
