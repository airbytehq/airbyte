# Chift Migration Guide

## Upgrading to 0.1.0

This release adds the `executions` stream and, alongside it, stops two objects from silently
losing data on schematizing destinations (S3 and GCS in Avro or Parquet format). That second
part is breaking for anyone reading those objects as nested columns.

### What changed

Two objects carried keys defined by the integration rather than by Chift's API contract, yet the
schema enumerated a fixed subset of them:

| Object | Was declared as | Is now |
|---|---|---|
| `connections.data` | an object with a single `folder_id` property | a schemaless object |
| `syncs.mappings[].sub_mappings[].target_field.display_condition` | an object enumerating the `!` and `in` operators and one nesting shape | a schemaless object |

Chift's own OpenAPI contract declares both objects free-form (`additionalProperties: true`, no
fixed properties), so enumerating a key subset misrepresented the contract. On destinations that
materialize declared nested shapes - S3 and GCS in Avro or Parquet format - the object column was
built strictly from the enumerated keys: every other key was dropped silently, and the loss was
not recorded in `_airbyte_meta.changes[]`. `display_condition` is a condition expression tree
whose operator set is open-ended by nature, so it could never be enumerated correctly.

A schemaless object is serialised to a JSON string instead, which preserves every key.
Destinations that already store whole objects as JSON or VARIANT columns (BigQuery, Snowflake,
Iceberg-based) keep the same column contents as before; for them this release only changes the
declared catalog shape.

### What you need to do

1. **Refresh the source schema** for the connection.
2. **Reset the `connections` and `syncs` streams** so the new column shape is applied.
3. **Update any query** that reads `data.folder_id` or the `display_condition` sub-fields as
   columns: they are now keys inside a JSON string.

Streams other than `connections` and `syncs` are unaffected, and no field is lost — the two
objects now carry strictly more than before.

### Extracting the values afterwards

Replace a direct column reference such as `data.folder_id` with a JSON extraction:

```sql
-- BigQuery
SELECT JSON_VALUE(data, '$.folder_id') AS folder_id FROM connections;

-- Snowflake
SELECT PARSE_JSON(data):folder_id::string AS folder_id FROM connections;

-- Postgres
SELECT data::json ->> 'folder_id' AS folder_id FROM connections;
```

The same pattern applies to `display_condition`, whose contents are now reachable with the JSON
path of the operator you care about, for example `$."in"` or `$."!"`.
