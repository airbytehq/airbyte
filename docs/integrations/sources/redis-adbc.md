# Redis (ADBC)

<HideInUI>

This page contains the setup guide and reference information for the
[Redis ADBC driver](https://github.com/redis/redis-adbc-driver) source connector.

</HideInUI>

This community connector is proposed for alpha review. It is not enabled in
the Airbyte Cloud or OSS registries while packaging and integration review is pending.

## Prerequisites

- A Redis Software or Redis Cloud database with Redis Search enabled.
- A connection `uri` using `redis://` or `rediss://`, with URL-encoded credentials.
- Tables or views already exposed through the Redis ADBC driver's metadata.
- Permissions required by the Redis ADBC driver, including Search and its own
  metadata initialization/migration. Connections always use autocommit.

## Setup guide

### Set up Redis (ADBC)

Prepare driver-managed SQL tables or explicitly prepare external indexed data
using the Redis ADBC driver's documented tools. The connector does not adopt
arbitrary Redis application HASHes. Configure exact database schema names;
the default is `public`.

### Set up the Redis (ADBC) connector in Airbyte

#### For Airbyte Cloud:

This proposed connector is not enabled in Airbyte Cloud.

#### For Airbyte Open Source:

1. Build the proposed connector image following its developer README.
2. Navigate to the Airbyte Open Source dashboard and register the image as a custom source.
3. Set `uri`; use `rediss://` for TLS. Set `schemas`, optional `catalog`, and `batch_size` as needed.
4. Run Check and Discover, select streams and top-level fields, and configure Full Refresh.

An optional `flight_sql` connection type uses an ADBC Flight SQL gateway.
The gateway must implement catalog/schema metadata, autocommit and SQL reads.
Use `schemas: [""]` when it has no database schema namespace. The reference
SQLite Flight SQL server is tested; a production Redis-backed gateway and its
TLS/authentication must be validated for that deployment.

## Supported sync modes

The Redis (ADBC) source connector supports Full Refresh with Overwrite or Append
at the destination. Incremental syncs and CDC are not supported.

## Supported Streams

Each table or view exposed through ADBC metadata is a stream. Database schemas
become Airbyte namespaces. Only configured schemas, selected streams and selected
top-level fields are read. An exact `catalog` resolves ambiguous names across catalogs.

## Data type map

| Arrow type | Airbyte representation |
| --- | --- |
| NULL | JSON null |
| Boolean, integer up to 32 bits | Boolean, JSON integer |
| Signed/unsigned 64-bit integer | String preserving the complete integer |
| Decimal | Fixed-point string preserving precision and scale |
| Floating point | JSON number; non-finite values fail the sync |
| UTF-8, dictionary | String, decoded value |
| Binary | Base64 string |
| Date/time/timestamp | ISO string retaining stored precision |
| List/struct | Recursively converted array/object |
| Map, union, interval, duration, extension | Rejected explicitly |

## Limitations & Troubleshooting

There is no shared snapshot, incremental checkpoint or durable query cursor.
Concurrent writes and TTL expiry can affect the extracted data. Failed jobs
restart a full read; Append can duplicate already delivered records. Overwrite
behavior is controlled by the destination and platform generation metadata.

The source reads Arrow batches internally and emits Airbyte JSON/stdio records.
It does not add native Arrow transport or claim a performance improvement.
Reader/cursor/connection cleanup and SIGTERM cancellation are tested. Raw native
driver diagnostics are withheld because they may contain connection credentials.
Configure Redis URI read/write timeouts to bound blocking operations.

Schema drift or unsupported types fail the sync and require rediscovery. The
published driver wheel is pinned in Poetry and bundles the native library.
AMD64 builds and a full Airbyte platform deployment require separate validation.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| --- | --- | --- | --- |
| 0.1.0 | 2026-11-01 | Pending | Initial full-refresh Redis ADBC source proposal |

</details>
