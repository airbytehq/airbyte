import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Chift Migration Guide

## Upgrading to 0.1.0

:::note
This change only alters the data you receive if your destination is S3 or GCS in **Avro or Parquet** format and you read fields inside `connections.data` or `syncs.mappings[].sub_mappings[].target_field.display_condition`. Destinations that store objects as JSON, VARIANT, or JSONB columns (BigQuery, Snowflake, Postgres, Iceberg-based destinations such as S3 Data Lake) keep the same column contents. For them, refreshing the source schema is the only step.
:::

This release adds the `executions` stream and changes how two objects in the `connections` and `syncs` streams are declared. That second part is breaking for anyone reading those objects as nested columns.

If you don't upgrade by 2026-10-31, Airbyte disables connections that still use 0.0.x until you upgrade them manually.

### What changed

Two objects carry keys defined by the third-party integration rather than by Chift's API contract, but the schema enumerated a fixed subset of them:

| Object | Was declared as | Is now |
| --- | --- | --- |
| `connections.data` | an object with a single `folder_id` property | a schemaless object |
| `syncs.mappings[].sub_mappings[].target_field.display_condition` | an object enumerating the `!` and `in` operators and one nesting shape | a schemaless object |

Chift's OpenAPI contract declares both objects free-form (`additionalProperties: true`, no fixed properties). On destinations that build typed records from the declared schema (S3 and GCS in Avro or Parquet format), the object column contained only the enumerated keys. Every other key was dropped silently, and the loss wasn't recorded in `_airbyte_meta.changes[]`. `display_condition` is a condition expression tree whose operator set is open-ended, so it could never be enumerated correctly.

A schemaless object is serialized to a JSON string on those destinations, which preserves every key. No data is lost: the full object is kept. On Avro and Parquet, the nested `data.folder_id` record field is replaced by the `data` string. Streams other than `connections` and `syncs` are unaffected.

### What you need to do

Which steps apply depends on your destination.

**S3 or GCS in Avro or Parquet format.** The `connections.data` and `syncs.mappings[].sub_mappings[].target_field.display_condition` columns change from a record with a fixed set of fields to a string containing the full JSON object.

1. Refresh the source schema for the connection.
2. If the connection replicates `connections` or `syncs` in **Full refresh | Append** mode, clear both streams so the prefix does not mix record-typed and string-typed files. Both streams are full refresh, so the next sync re-supplies every record. **Full refresh | Overwrite** connections are rebuilt on the next sync and need no clear.
3. Update any reader that accessed `data.folder_id` or the `display_condition` sub-fields as nested record fields to parse the JSON string instead. For example, in Athena or Trino, `json_extract_scalar(data, '$.folder_id')`; in Spark, `get_json_object(data, '$.folder_id')`. For `display_condition`, use the JSON path of the operator you care about, such as `$."in"` or `$."!"`.

**BigQuery, Snowflake, Postgres, and Iceberg-based destinations (including S3 Data Lake).** These destinations already store the whole object in a JSON, VARIANT, or JSONB column, so the column contents don't change. Refresh the source schema so the connection's catalog matches the new declared shape. You don't need to clear the streams or change your queries; JSON extraction such as `JSON_VALUE(data, '$.folder_id')` (BigQuery), `data:folder_id::string` (Snowflake), or `data ->> 'folder_id'` (Postgres) keeps working as before.

## Connector upgrade guide

<MigrationGuide />
