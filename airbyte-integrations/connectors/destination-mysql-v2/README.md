# MySQL v2 Destination

## Overview

This is a modern, CDK-based MySQL destination connector that supports all sync modes:
- **Append**: Incremental sync without deduplication
- **Dedupe**: Incremental sync with primary key deduplication
- **Overwrite**: Full refresh that replaces all data

Built using the Airbyte Dataflow CDK v2 framework for optimal performance and maintainability.

## Features

- ✅ Full CDC support with hard/soft delete modes
- ✅ Automatic schema evolution (add/drop/modify columns)
- ✅ All sync modes (append, dedupe, overwrite)
- ✅ Batch insert optimization for high throughput
- ✅ SSL/TLS connection support
- ✅ Connection pooling with HikariCP
- ✅ MySQL 5.7+ and 8.0+ support

## Configuration

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `host` | string | yes | - | MySQL server hostname |
| `port` | integer | yes | 3306 | MySQL server port |
| `database` | string | yes | - | Target database name |
| `username` | string | yes | - | MySQL username |
| `password` | string | yes | - | MySQL password |
| `ssl` | boolean | no | false | Enable SSL connection |
| `ssl_mode` | enum | no | PREFERRED | SSL mode: DISABLED, PREFERRED, REQUIRED, VERIFY_CA, VERIFY_IDENTITY |
| `jdbc_url_params` | string | no | - | Additional JDBC parameters |
| `batch_size` | integer | no | 5000 | Records per batch |

## Requirements

- MySQL 5.7 or higher (8.0+ recommended for better upsert support)
- Database user with the following permissions:
  - `CREATE` - Create databases and tables
  - `DROP` - Drop temporary tables
  - `INSERT` - Insert data
  - `UPDATE` - Update data (for dedupe mode)
  - `DELETE` - Delete data (for dedupe mode)
  - `SELECT` - Read data for deduplication
  - `ALTER` - Modify table schema (for schema evolution)

## Supported Sync Modes

| Sync Mode | Supported | Notes |
|-----------|-----------|-------|
| Incremental \| Append | ✅ | Appends new records |
| Incremental \| Deduped | ✅ | Deduplicates by primary key |
| Full Refresh \| Overwrite | ✅ | Replaces all data |
| Full Refresh \| Append | ✅ | Appends to existing data |

## Performance

- Batch inserts using multi-value INSERT statements
- Connection pooling for concurrent streams
- Configurable batch size (default: 5000 records)
- Automatic chunking for large batches to avoid packet size limits

## Schema Evolution

The connector automatically adapts to schema changes:
- **Add Column**: Adds new columns to existing tables
- **Drop Column**: Removes columns no longer in source
- **Widen Type**: Changes column types to accommodate larger values
- **Nullable Changes**: Handles NULL to NOT NULL and vice versa

## CDC Support

When using CDC sources, the connector can:
- **Hard Delete**: Actually delete records marked as deleted
- **Soft Delete**: Keep tombstone records with deletion timestamp

## Limitations

- MySQL doesn't support time with timezone - stored as TIME without timezone
- Column names are truncated to 64 characters (MySQL limit)
- Maximum packet size is 64MB (configurable via `max_allowed_packet`)

## Development

Built with:
- Kotlin
- Airbyte CDK v2 (Dataflow)
- Micronaut for dependency injection
- HikariCP for connection pooling
- MySQL Connector/J 9.x

## License

MIT License - Copyright (c) 2025 Airbyte, Inc.
