# MS SQL Server Migration Guide

## Upgrading to 1.0.0

This version removes the option to use "normalization" with Microsoft SQL Server. It also changes
the schema and database of Airbyte's "raw" tables to be compatible with the new
[Destinations V2](https://docs.airbyte.com/release_notes/upgrading_to_destinations_v2/#what-is-destinations-v2)
format. These changes will likely require updates to downstream dbt / SQL models. After this update,
Airbyte will only produce the "raw" v2 tables, which store all content in JSON. These changes remove
the ability to do deduplicated syncs with Microsoft SQL Server.
If you are interested in the Microsoft SQL Server destination gaining the full features
of Destinations V2 (including final tables), click [[https://github.com/airbytehq/airbyte/discussions/37010]]
to register your interest.

This upgrade will ignore any existing raw tables and will not migrate any data to the new schema.
For each stream, you should perform the following query to migrate the data from the old raw table
to the new raw table:

```sql
-- assumes your schema was 'default'
-- replace `{{stream_name}}` with replace your stream name

CREATE TABLE airbyte_internal.default_raw__stream_{{stream_name}} (
 _airbyte_raw_id VARCHAR(64) PRIMARY KEY,
 _airbyte_data NVARCHAR(MAX),
 _airbyte_extracted_at DATETIMEOFFSET(7) DEFAULT SYSDATETIMEOFFSET(),
 _airbyte_loaded_at DATETIMEOFFSET(7),
 _airbyte_meta NVARCHAR(MAX)
);

INSERT INTO airbyte_internal.default_raw__stream_{{stream_name}}
SELECT
    _airbyte_ab_id AS _airbyte_raw_id,
    _airbyte_data as _airbyte_data,
    _airbyte_emitted_at as _airbyte_extracted_at,
    NULL as _airbyte_loaded_at,
    NULL as _airbyte_meta
FROM airbyte._airbyte_raw_{{stream_name}}
```

**Airbyte will not delete any of your v1 data.**

### Schema and the Internal Schema

We have split the raw and final tables into their own schemas. For the Microsoft SQL Server destination, this means that
we will only write into the raw table which will live in the `airbyte_internal` schema.
The tables written into this schema will be prefixed with either the default database provided in
the `DB Name` field when configuring Microsoft SQL Server (but can also be overridden in the connection). You can
change the "raw" database from the default `airbyte_internal` by supplying a value for
`Raw Table Schema Name`.

For Example:

- Schema: `default`
- Stream Name: `my_stream`

Writes to `airbyte_intneral.default_raw__stream_my_stream`

Where as:

- Schema: `default`
- Stream Name: `my_stream`
- Raw Table Schema Name: `raw_data`

Writes to `raw_data.default_raw__stream_my_stream`
