import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# ClickHouse Migration Guide

## Upgrading to 0.3.0

Version 0.3.0 upgrades the ClickHouse JDBC driver from 0.3.2-patch10 to 0.9.5 and introduces custom type mapping for large integer types. This changes the JSON schema types produced during discovery for certain ClickHouse column types.

### What changed

The new JDBC driver maps ClickHouse large integer types differently than the previous driver:

| ClickHouse Type | Previous Schema Type | New Schema Type |
|:----------------|:---------------------|:----------------|
| UInt64 | `string` or `integer` | `number` |
| Int128 | `string` | `number` |
| Int256 | `string` | `number` |
| UInt128 | `string` | `number` |
| UInt256 | `string` | `number` |

Other ClickHouse types that previously mapped to `JDBCType.OTHER` under the new driver will now map to `string` by default.

### Who is affected

Users syncing tables that contain columns of type `UInt64`, `Int128`, `Int256`, `UInt128`, or `UInt256` will see schema changes after upgrading. If your tables do not use these column types, you are unlikely to be affected.

### Migration steps

1. Upgrade the connector to version 0.3.0.
2. Refresh the source schema to pick up the new type mappings.
3. Reset the affected streams that contain large integer columns.

## Connector upgrade guide

<MigrationGuide />
