import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Postgres Migration Guide

## Upgrading to 4.0.0

Version 4.0.0 corrects how the connector discovers the type of two kinds of columns that use user-defined types. Both were discovered incorrectly in versions 3.8.0 to 3.8.6.

- **Non-array types whose name starts with an underscore.** Postgres names array types `_<element>`, but you can also create a non-array type with a leading underscore, for example `CREATE TYPE _status AS ENUM ('active', 'inactive')`. Versions 3.8.0 to 3.8.6 discovered such a column as an array. Full refresh syncs and initial snapshots wrote `null` for the column, and CDC syncs failed with `ClassCastException: ... TextNode cannot be cast to ... ArrayNode`. Version 4.0.0 discovers the column as a string and syncs its values.
- **Arrays of types outside the search path.** An array column whose element type is a user-defined or extension type in a schema that isn't on the connection's `search_path`, for example an enum in schema `s2` or an `hstore` installed in an `extensions` schema. Versions 3.8.0 to 3.8.6 discovered such a column as a string, with values in Postgres array text format (`{a,b}`) in full refresh syncs and as JSON arrays (`["a","b"]`) in CDC syncs. Version 4.0.0 discovers the column as an array again, as version 3.7 did.

### Who is affected

Connections that sync a stream containing one of these column types. Connections without them don't need to do anything.

To find such columns, run this query in your database:

```sql
-- Non-array types whose name starts with an underscore
SELECT c.table_schema, c.table_name, c.column_name, c.udt_schema, c.udt_name
FROM information_schema.columns c
JOIN pg_type t ON t.typname = c.udt_name
JOIN pg_namespace n ON n.oid = t.typnamespace AND n.nspname = c.udt_schema
WHERE c.udt_name LIKE '\_%' AND t.typcategory <> 'A';

-- Arrays whose element type is in a schema that isn't on the search path
SELECT c.table_schema, c.table_name, c.column_name, c.udt_schema, c.udt_name
FROM information_schema.columns c
WHERE c.data_type = 'ARRAY'
  AND c.udt_schema NOT IN ('pg_catalog')
  AND NOT c.udt_schema = ANY (current_schemas(true));
```

Run the second query as the user that the connector connects with, so that `current_schemas` reflects the connector's search path.

### Migration steps

1. Upgrade the Postgres source to version 4.0.0.
2. For each affected connection, open the connection and select the **Schema** tab.
3. Select **Refresh source schema**, review the type changes for the affected columns, and select **Save changes**.
4. If a sync then fails because the destination can't change the type of an existing column, refresh the affected streams.

If downstream models parse these columns, update them for the new type: a string instead of an array for the first kind, and an array instead of a string for the second.

## Connector upgrade guide

<MigrationGuide />
