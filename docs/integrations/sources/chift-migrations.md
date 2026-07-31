# Chift Migration Guide

## Upgrading to 0.1.0

This release adds the `executions` stream and, alongside it, stops two objects from silently
losing data on typed destinations. That second part is breaking for anyone reading those objects
as nested columns.

### What changed

Two objects carried keys defined by the integration rather than by Chift's API contract, yet the
schema enumerated a fixed subset of them:

| Object | Was declared as | Is now |
|---|---|---|
| `connections.data` | an object with a single `folder_id` property | a schemaless object |
| `syncs.mappings[].sub_mappings[].target_field.display_condition` | an object enumerating the `!` and `in` operators and one nesting shape | a schemaless object |

Airbyte's V2 destinations materialise exactly the declared stream schema. An undeclared property
inside a declared object is dropped, and the loss is not recorded in `_airbyte_meta.changes[]` —
so every key outside those subsets was disappearing with no signal at all. `display_condition` is
a JSONLogic expression tree, so its operator set is open-ended by nature and could never be
enumerated correctly.

A schemaless object is serialised to a JSON string instead, which preserves every key.

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
