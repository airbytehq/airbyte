# DocumentDB

The DocumentDB source reads collections from the open-source [DocumentDB](https://github.com/documentdb/documentdb) MongoDB-compatible database.

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| Full Refresh | Yes |
| Incremental / CDC | No |

The current public `documentdb-local` image returns MongoDB error `115 CommandNotSupported` for both cluster-level and collection-level `$changeStream` requests. Without compatible change streams and resume tokens, Airbyte cannot reliably capture inserts, updates, and deletes. The connector therefore exposes full refresh only.

## Prerequisites

- A reachable DocumentDB gateway
- A user with permission to list and read the configured databases and collections
- Network access from the Airbyte worker to the DocumentDB host and port
- The CA certificate trusted by the Airbyte worker when TLS uses a private certificate authority

## Configuration

Configure either `host` and `port`, or a `mongodb://` connection string. The default port is `10260` and TLS is enabled by default. Airbyte always applies `retryWrites=false` for DocumentDB compatibility.

```json
{
  "host": "documentdb.example.com",
  "port": 10260,
  "databases": ["inventory"],
  "username": "airbyte_reader",
  "password": "your-password",
  "auth_source": "admin",
  "tls": true,
  "direct_connection": true,
  "read_preference": "primaryPreferred"
}
```

Set `direct_connection` to `false` and provide `replica_set` when connecting through multiple replica-set members. For local development, either import the `documentdb-local` CA certificate into the connector JVM trust store or disable TLS only on a trusted local network.

## Data types and discovery

The connector reuses Airbyte's MongoDB BSON conversion and schema discovery. Documents are sampled during discovery, so fields absent from the configured sample may not appear in an enforced schema. Disable `schema_enforced` to use schemaless records when collections contain highly variable documents.

## Limitations

- Incremental and CDC syncs are not supported.
- MongoDB features outside DocumentDB's implemented compatibility surface may fail.
- The connector does not accept `mongodb+srv://` URIs in its initial alpha release.

## Changelog

| Version | Date | Subject |
| :--- | :--- | :--- |
| 0.1.0 | 2026-08-17 | Initial alpha release with full refresh support |