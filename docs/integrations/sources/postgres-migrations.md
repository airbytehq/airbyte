import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Postgres Migration Guide

## Upgrading to 4.0.0

Version 4.0.0 discovers numeric array columns with a scale of zero as arrays of integers. Previously, the elements of every numeric array column were discovered as numbers, even when the corresponding scalar column, for example `NUMERIC(20,0)`, was discovered as an integer.

The following column types are affected:

- `NUMERIC(p)[]` and `NUMERIC(p,0)[]`
- `DECIMAL(p)[]` and `DECIMAL(p,0)[]`

Arrays of unconstrained `NUMERIC`, and of `NUMERIC(p,s)` with a non-zero scale, are still discovered as arrays of numbers.

### Who is affected

Connections that sync a stream containing one of the affected column types. Connections without them don't need to do anything.

To find such columns, run this query in your database:

```sql
SELECT n.nspname AS table_schema, c.relname AS table_name, a.attname AS column_name,
       format_type(a.atttypid, a.atttypmod) AS column_type
FROM pg_attribute a
JOIN pg_class c ON c.oid = a.attrelid
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE a.atttypid = '_numeric'::regtype
  AND a.atttypmod >= 4
  AND ((a.atttypmod - 4) & 65535) = 0
  AND a.attnum > 0
  AND NOT a.attisdropped;
```

### Migration steps

1. Upgrade the Postgres source to version 4.0.0.
2. For each affected connection, open the connection and select the **Schema** tab.
3. Select **Refresh source schema**, review the type changes for the affected columns, and select **Save changes**. Until the schema is refreshed, streams that contain an affected column are skipped.
4. If a sync then fails because the destination can't change the type of an existing column, refresh the affected streams.

If downstream models read the elements of these arrays, update them to expect integers instead of decimal numbers.

## Connector upgrade guide

<MigrationGuide />
