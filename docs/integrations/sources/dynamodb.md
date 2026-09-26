---
description: >-
  Amazon DynamoDB is a fully managed NoSQL key-value database offered by
  Amazon Web Services.
---

# DynamoDB

The DynamoDB source connector reads the tables of an Amazon DynamoDB account and region. It supports full refresh and incremental syncs, infers each table's schema by sampling its items, reads a table page by page with the `Scan` API, and saves its position after every round of pages so that a large table resumes after an interruption instead of starting over.

Version 1.0.0 rebuilds the connector on Airbyte's Bulk CDK. It accepts the configuration and the saved state of versions 0.3.x, so existing connections keep syncing without a reset. See [Changes in 1.0.0](#changes-in-100) for what changed and the [migration guide](dynamodb-migrations.md) for what to do.

## Features

| Feature                   | Supported | Notes                                                                                       |
| :------------------------ | :-------- | :------------------------------------------------------------------------------------------ |
| Full refresh sync         | Yes       | Resumable, see [State and resuming](#state-and-resuming)                                    |
| Incremental sync - append | Yes       | Cursor based, see [Incremental sync](#incremental-sync)                                     |
| Replicate deletes         | No        | The connector doesn't read DynamoDB Streams                                                 |
| Change data capture (CDC) | No        |                                                                                             |
| Namespaces                | No        | A region has a flat list of tables                                                          |
| Primary keys              | Yes       | The table's partition key                                                                   |
| Checkpoints               | Yes       | A state message after every round of scan pages, per scan segment                           |
| Speed mode                | Yes       | The connector supports the socket data channel with JSONL and protocol buffer serialization |

The connector is read-only. It calls `ListTables`, `DescribeTable` and `Scan` and never writes to your tables.

## Getting started

### Requirements

- An AWS account with the DynamoDB tables to sync.
- An IAM identity with the permissions listed below, and its access key. Credentials always come from the source configuration: the connector can't use an AWS profile, an instance role or environment variables of the machine it runs on.

### IAM permissions

Create a dedicated IAM user or role for Airbyte and grant it the following permissions. Restrict `DescribeTable` and `Scan` to the tables you sync when you don't want Airbyte to see the others.

| Permission               | Resource                                   | Why                                                                     |
| :----------------------- | :----------------------------------------- | :---------------------------------------------------------------------- |
| `dynamodb:ListTables`    | `*`                                        | Lists the tables of the region during the connection test and discovery |
| `dynamodb:DescribeTable` | Each table to sync                         | Reads the table's key schema, which becomes the stream's primary key    |
| `dynamodb:Scan`          | Each table to sync                         | Samples items during discovery and reads the data during a sync         |
| `sts:AssumeRole`         | The role, with **Access Key and IAM Role** | Lets the access key's identity assume the role that reads the tables    |

### Authentication

The connector offers two authentication methods. Both start from an access key.

- **Access Key**: the access key ID and secret access key of an IAM user, or temporary credentials issued by AWS STS. For temporary credentials also fill in the **Session Token**. The connector signs every request with this key.
- **Access Key and IAM Role**: an access key that is allowed to call `sts:AssumeRole` on an IAM role, plus the role's ARN and, when the role's trust policy requires one, the external ID. The connector assumes the role and reads the tables with the role's temporary credentials. Use this method for cross-account access or to keep the reading identity to a least-privilege role.

The role based authentication of versions 0.3.x, which took credentials from the environment the connector runs in, is not available. A saved configuration that uses it fails the connection test with a message that says so.

### Set up the DynamoDB source in Airbyte

1. In the Airbyte UI, click **Sources** and then **+ New source**.
2. Select **DynamoDB** from the source type list.
3. Fill in the connection fields:

| Field                                          | Required | Description                                                                                                                                                                                                 |
| :--------------------------------------------- | :------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Credentials**                                | Yes      | **Access Key** or **Access Key and IAM Role**, see [Authentication](#authentication).                                                                                                                       |
| **AWS Region**                                 | Yes      | The region of the tables, for example `us-east-1`. The region is required even with an endpoint override.                                                                                                   |
| **DynamoDB Endpoint**                          | No       | An `http` or `https` URL that replaces the public endpoint of the region: a VPC endpoint, a FIPS endpoint, or a DynamoDB Local instance.                                                                    |
| **Reserved attribute names**                   | No       | Kept so that configurations of versions 0.3.x still load. The connector ignores it: every attribute is aliased in its scan expressions, so reserved words and special characters need no configuration.     |
| **Ignore missing read permissions tables**     | No       | When on, discovery skips a table whose `Scan` is denied instead of failing. Off by default.                                                                                                                 |
| **Discovery sample size (Advanced)**           | No       | How many items discovery reads from each table to infer its attributes and their types. Defaults to 1000, the range is 1 to 100000. A larger sample finds rarer attributes and consumes more read capacity. |
| **Checkpoint Target Time Interval (Advanced)** | No       | How often, in seconds, a stream saves its position. A table is scanned in rounds of about this duration and a state message follows every round. Defaults to 300, the minimum is 1.                         |
| **Concurrency**                                | No       | How many scans the connector runs at the same time, across the segments of a table and across tables. Defaults to 1. See [Concurrency](#concurrency).                                                       |

4. Click **Set up source**. The connection test lists the tables of the region. It fails with `Discovered zero tables.` when the identity can't see any table there.

## Replication

### Discovered streams

Every table of the region is a stream. DynamoDB tables have no schema, only their key attributes are typed, so the connector infers a schema the way versions 0.3.x did: it scans up to **Discovery sample size** items of the table, merges the top-level attributes of every sampled item, and maps each attribute to a JSON schema from the type of its value. When an attribute has values of different types in different items, the last sampled item decides its type. Nested maps and lists keep the structure of the sampled values. An attribute that appears only in items outside the sample is missing from the schema, and a table without items isn't discovered at all.

The stream's primary key is the table's partition key. A table with a composite key reports only its partition key, as versions 0.3.x did, so more than one item can share a primary key value. Global and local secondary indexes are never read.

### Full refresh

A full refresh scans the whole table with the `Scan` API, one page of up to 1 MB at a time, projecting exactly the attributes of the stream's schema. Every attribute is referenced through a placeholder in the expression, so attribute names that are DynamoDB reserved words, or that contain spaces, dots, dashes, or a leading underscore, work without configuration.

`Scan` is eventually consistent and has no snapshot isolation. An item written while its table is being scanned may appear in either version, and an item inserted or deleted during the scan may or may not be part of the result.

### Incremental sync

Incremental sync uses a cursor attribute that you choose for each stream. The cursor must be a top-level attribute of type string (`S`), for example an ISO 8601 timestamp, or number (`N`), for example an epoch value. The connector takes the cursor's type from the stream's schema: a `string` attribute is compared as a string and an `integer` or `number` attribute as a number with full DynamoDB precision. Nested attributes and other types can't be cursors.

The first sync reads the whole table. Every later sync scans the whole table again with a filter that keeps the items whose cursor is greater than the saved cursor value, or greater than or equal to it when the saved value is a plain date such as `2016-02-15`, so that the items of the day of the last sync aren't skipped. DynamoDB applies the filter after reading the items, so an incremental sync consumes as much read capacity as a full refresh and takes about as long; the filter only reduces the records sent to the destination. The highest cursor value read becomes the saved cursor once the scan is complete. Items without the cursor attribute are replicated but don't move the cursor, and changing the cursor attribute of a stream starts it over.

Choose an attribute whose values only grow and that every new or updated item carries, such as an update timestamp. Because the cursor is compared as text for string attributes, use a fixed-width format that sorts chronologically, such as `2024-05-01T10:00:00Z`. Cursor values should never be empty.

### State and resuming

The connector emits state while it reads, not only at the end of a sync. After every round of scan pages, about **Checkpoint Target Time Interval** long, the state records, for every segment of the table, the key of the last page read or that the segment is complete; for an incremental stream it also carries the highest cursor value seen so far in each segment. A retried attempt resumes every unfinished segment at its saved key, so at most one page per segment is read twice and no item is skipped. The number of segments is saved with the state and kept until the table is complete, whatever the **Concurrency** setting of the retry. A completed incremental stream saves its cursor value in the same shape versions 0.3.x used, and a completed full refresh saves a marker so that a retried attempt doesn't read the table again. Resetting the connection's data makes the next sync start from the beginning.

The connector also reads the state saved by versions 0.3.x. A stream with such state resumes after its saved cursor value instead of reading the table from the start.

### Concurrency

The connector reads a large table with a [parallel scan](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Scan.html), where DynamoDB divides the table into segments by hashing each item's partition key and the connector scans each segment on its own. The segments cost nothing to compute and consume the same read capacity as one sequential scan. The number of segments comes from the table size that `DescribeTable` reports, one segment per 64 MB, up to 128 segments per table, so a table under 64 MB is still read by a single scan. DynamoDB refreshes that size about every six hours, so a table loaded since the last refresh reports zero bytes; the connector then uses as many segments as **Concurrency**.

**Concurrency** sets how many scans run at the same time across all tables. With the default of 1 the segments of a table are read one after another and tables one after another, which is as fast as a single sequential scan. Raise it to read segments and tables in parallel; the speed-up is close to linear until the table's read capacity or the network is saturated. Each running scan holds one page of up to 1 MB in memory.

Segments can be uneven. All items with the same partition key land in the same segment, so a table with few partition keys, or a few large item collections, has segments of different sizes; the larger ones just finish later.

### Read throughput

Measured on 2026-09-24 against a 1 GB table in `us-east-2` (1,000,000 items of about 1 KB) from a laptop on a residential connection, where one 1 MB scan page takes about 0.4 s to arrive; inside AWS the absolute numbers are higher, the ratios are what matter. Every run read the same 1,000,000 records and consumed the same 124,274 read units (about $0.03 on-demand).

| Concurrency | Segments read in parallel | Wall time  | Throughput |
| :---------- | :------------------------ | :--------- | :--------- |
| 1           | 1                         | 7 min 47 s | 2.1 MB/s   |
| 4           | 4                         | 1 min 57 s | 8.5 MB/s   |
| 8           | 8                         | 1 min 12 s | 14 MB/s    |
| 16          | 16                        | 45 s       | 23 MB/s    |

A sync interrupted at concurrency 8 and resumed from its last state returned every one of the 1,000,000 keys exactly once, apart from the records read in the 10 seconds after the last checkpoint. Sixteen concurrent segments completed inside a 384 MB Java heap.

### Read capacity

Every sync scans each configured table in full, and so does discovery for up to **Discovery sample size** items per table. `Scan` consumes read capacity for every item it reads, whatever the projection or filter: an eventually consistent read of up to 4 KB costs half a read request unit, see [Read/write capacity mode](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/read-write-capacity-mode.html). On a table with provisioned capacity a sync competes with your own workload for read capacity units; DynamoDB throttles the connector when the table's capacity is exceeded, and the connector retries and, when the throttling persists, reports a transient error that Airbyte retries. Raise the table's read capacity or switch it to on-demand mode when syncs are throttled.

## Data type mapping

Each top-level attribute of a table becomes a field whose JSON schema and value follow the type of the attribute's value in the sampled items. The schemas use the same shapes as Airbyte's other database connectors: `{"type": "string"}` rather than a `["null", "string"]` type list, and whole numbers as `{"type": "number", "airbyte_type": "integer"}`. Every field can hold null, as in all Airbyte sources.

| DynamoDB type     | Airbyte type | Notes                                                                                                                                                                                                   |
| :---------------- | :----------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `S` (string)      | `string`     |                                                                                                                                                                                                         |
| `N` (number)      | `integer`    | When the sampled value is an integer that fits in 64 bits. Values are read as integers when they fit in 64 bits, otherwise as exact decimals with the full 38 digits of precision that DynamoDB stores. |
| `N` (number)      | `number`     | When the sampled value has a fraction or an exponent, or doesn't fit in 64 bits.                                                                                                                        |
| `B` (binary)      | `string`     | Base64 encoded, with `contentEncoding: base64` in the schema.                                                                                                                                           |
| `BOOL`            | `boolean`    |                                                                                                                                                                                                         |
| `NULL`            | `null`       |                                                                                                                                                                                                         |
| `M` (map)         | `object`     | The schema lists the nested attributes of the sampled value with their own types.                                                                                                                       |
| `L` (list)        | `array`      | The schema lists one item schema per element of the sampled value.                                                                                                                                      |
| `SS` (string set) | `array`      | Items are strings.                                                                                                                                                                                      |
| `NS` (number set) | `array`      | Items are numbers, read exactly.                                                                                                                                                                        |
| `BS` (binary set) | `array`      | Items are base64 encoded strings.                                                                                                                                                                       |

An attribute that a record's item doesn't have is `null` in the record.

## Changes in 1.0.0

Version 1.0.0 loads the configuration and the state of versions 0.3.x, and its `discover` output lists the same streams, fields, and types for the same tables, with these differences. The [migration guide](dynamodb-migrations.md) says what to do about them.

- **Schemas use Airbyte's standard shapes.** Versions 0.3.x wrote `{"type": ["null", "string"]}` and `{"type": ["null", "integer"]}`; this connector writes `{"type": "string"}` and `{"type": "number", "airbyte_type": "integer"}`, like every other Airbyte database connector. A connection upgraded from 0.3.x keeps syncing with its saved catalog and shows a schema change on every column at its next schema refresh; the column types in the destination don't change.

- **Credentials come from the configuration only.** Role based authentication, which used the credentials of the environment the connector ran in, is gone. Temporary credentials with a session token and role assumption with `sts:AssumeRole` are new, **AWS Region** is required and **DynamoDB Endpoint** must be an `http` or `https` URL.
- **Reserved attribute names need no configuration.** Every attribute is aliased in the scan expressions, so the **Reserved attribute names** field is ignored. Versions 0.3.x failed on any unlisted reserved word or special character and could never read a table that had both `field.name` and `field-name`.
- **Large numbers are exact.** An `N` value that doesn't fit in 64 bits is read as an exact decimal; versions 0.3.x converted it to a floating point number and lost precision.
- **Absent attributes are `null`.** An attribute that an item doesn't have is present in the record as `null`; versions 0.3.x left it out.
- **Integer cursors work.** Versions 0.3.x failed before the first record on any cursor attribute discovered as `integer`, which is every whole number.
- **Syncs resume.** Full refresh and incremental streams save their position after every round of scan pages and resume there; versions 0.3.x saved one state at the end of an incremental stream and nothing for a full refresh.
- **Failures carry a message.** The connection test reports why it failed; versions 0.3.x reported a failure without a message. A configured table that no longer exists, or whose stream has no fields, fails only its own stream; the other streams of the sync are read.
- **Empty tables aren't discovered**, and the connection test fails when the region has no tables. Versions 0.3.x listed an empty table as a stream without fields and couldn't read it.
- **Large tables are read with parallel scans.** A table over 64 MB is split into scan segments that **Concurrency** reads in parallel; versions 0.3.x read every table with one sequential scan.
- **Discovery sample size and Concurrency** are new settings; versions 0.3.x always sampled 1000 items and read one table at a time.

## Limitations and troubleshooting

- **No change data capture.** Deleted items aren't detected and updated items are only picked up when the cursor attribute changes. The connector doesn't read DynamoDB Streams.
- **Every sync scans every configured table in full**, incremental syncs included, and consumes read capacity for every item of the table. See [Read capacity](#read-capacity).
- **The schema comes from a sample.** Raise **Discovery sample size** and refresh the source schema when an attribute is missing from a stream or has the wrong type, and pin the type of an attribute that varies between items by storing one type only.
- **Composite keys report only the partition key** as the primary key. Destinations that remove duplicates by primary key collapse the items that share a partition key value; use append modes for such tables.
- **`The access key id or the session token is invalid`** or **`The secret access key is invalid`** mean the configured access key is wrong; **`The temporary credentials (session token) have expired`** means new temporary credentials are needed.
- **`... is not authorized to perform: sts:AssumeRole ...`** names the identity and the role: the role's trust policy doesn't allow the access key's identity to assume it, or the external ID is wrong. **`... is not authorized to perform: dynamodb:... `** names a missing permission from the [IAM permissions](#iam-permissions) table.
- **`Could not reach the DynamoDB endpoint`** means the configured endpoint doesn't resolve or accept connections; check **DynamoDB Endpoint** and **AWS Region**.
- **`A configured table does not exist (any more)`** appears when a table was deleted or renamed after the source schema was set up; refresh the source schema. **`The saved state of a stream does not match its table's key schema`** appears when a table was recreated with other key attributes, and **`... does not match its table's scan segments`** when a saved segment key no longer fits the table; reset the stream's data in both cases.
- **Throttling errors** (`ProvisionedThroughputExceededException`, `ThrottlingException`) are transient. Airbyte retries the sync; raise the table's read capacity if they persist.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                                              |
| :------ | :--------- | :-------------------------------------------------------- | :------------------------------------------------------------------- |
| 1.0.0 | 2026-09-25 | [86997](https://github.com/airbytehq/airbyte/pull/86997) | Rebuild on the Bulk CDK: parallel scan segments, resumable full refresh and incremental syncs, speed mode, exact numbers, integer cursors, temporary credentials and IAM role assumption. See the migration guide |
| 0.3.11 | 2025-07-10 | [62916](https://github.com/airbytehq/airbyte/pull/62916) | Add gradle docker plugins |
| 0.3.10 | 2025-06-14 | [61601](https://github.com/airbytehq/airbyte/pull/61601) | fix(source-dynamodb): Replace ListNode with Iterator for lazyness #61600 |
| 0.3.9 | 2025-02-12 | [53202](https://github.com/airbytehq/airbyte/pull/53202) | fixed IRSA by adding STS to classpath of connector. |
| 0.3.8 | 2025-01-10 | [51489](https://github.com/airbytehq/airbyte/pull/51489) | Use a non root base image |
| 0.3.7 | 2024-12-18 | [49881](https://github.com/airbytehq/airbyte/pull/49881) | Use a base image: airbyte/java-connector-base:1.0.0 |
| 0.3.6 | 2024-07-19 | [41936](https://github.com/airbytehq/airbyte/pull/41936) | Fix incorrect type check for incremental read |
| 0.3.5 | 2024-07-23 | [42433](https://github.com/airbytehq/airbyte/pull/42433) | add PR number |
| 0.3.4 | 2024-07-23 | [49881](https://github.com/airbytehq/airbyte/pull/49881) | fix primary key fetching |
| 0.3.3 | 2024-07-22 | [49881](https://github.com/airbytehq/airbyte/pull/49881) | fix primary key fetching |
| 0.3.2 | 2024-05-01 | [27045](https://github.com/airbytehq/airbyte/pull/27045) | Fix missing scan permissions |
| 0.3.1 | 2024-05-01 | [31935](https://github.com/airbytehq/airbyte/pull/31935) | Fix list more than 100 tables |
| 0.3.0 | 2024-04-24 | [37530](https://github.com/airbytehq/airbyte/pull/37530) | Allow role based access |
| 0.2.3 | 2024-02-13 | [35232](https://github.com/airbytehq/airbyte/pull/35232) | Adopt CDK 0.20.4 |
| 0.2.2 | 2024-01-24 | [34453](https://github.com/airbytehq/airbyte/pull/34453) | bump CDK version |
| 0.2.1   | 2024-01-03 | [#33924](https://github.com/airbytehq/airbyte/pull/33924) | Add new ap-southeast-3 AWS region                                    |
| 0.2.0   | 18-12-2023 | https://github.com/airbytehq/airbyte/pull/33485           | Remove LEGACY state                                                  |
| 0.1.2   | 01-19-2023 | https://github.com/airbytehq/airbyte/pull/20172           | Fix reserved words in projection expression & make them configurable |
| 0.1.1   | 02-09-2023 | https://github.com/airbytehq/airbyte/pull/22682           | Fix build                                                            |
| 0.1.0   | 11-14-2022 | https://github.com/airbytehq/airbyte/pull/18750           | Initial version                                                      |

</details>
