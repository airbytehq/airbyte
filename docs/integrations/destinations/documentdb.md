# DocumentDB

The DocumentDB destination writes Airbyte records to the open-source [DocumentDB](https://github.com/documentdb/documentdb) MongoDB-compatible database.

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| Full Refresh - Append | Yes |
| Full Refresh - Overwrite | Yes |
| Incremental - Append | Yes |
| Append + Deduped | No |

## Prerequisites

- A reachable DocumentDB gateway
- A user with permission to create collections, insert documents, and drop or rename collections for overwrite syncs
- Network access from the Airbyte worker to the DocumentDB host and port
- The CA certificate trusted by the Airbyte worker when TLS uses a private certificate authority

## Configuration

Configure either `host` and `port`, or a `mongodb://` connection string. The default port is `10260` and TLS is enabled by default. Airbyte always applies `retryWrites=false` because DocumentDB does not provide MongoDB retryable-write semantics.

```json
{
  "host": "documentdb.example.com",
  "port": 10260,
  "database": "airbyte",
  "username": "airbyte_writer",
  "password": "your-password",
  "auth_source": "admin",
  "tls": true,
  "direct_connection": true,
  "read_preference": "primaryPreferred"
}
```

Set `direct_connection` to `false` and provide `replica_set` when connecting through multiple replica-set members. For local development, either import the `documentdb-local` CA certificate into the connector JVM trust store or disable TLS only on a trusted local network.

## Output format

Each Airbyte stream is written to a separate collection using the MongoDB destination's BSON conversion, batching, duplicate detection, and temporary-collection overwrite flow. Airbyte stores the source record in `_airbyte_data` with its emitted timestamp and generated identifier.

## Limitations

- Upsert and append-deduped modes are not supported.
- MongoDB features outside DocumentDB's implemented compatibility surface may fail.
- The connector does not accept `mongodb+srv://` URIs in its initial alpha release.

## Changelog

| Version | Date | Subject |
| :--- | :--- | :--- |
| 0.1.0 | 2026-08-17 | Initial alpha release with append and overwrite support |