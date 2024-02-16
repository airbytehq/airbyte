# Clickhouse Migration Guide

## Upgrading to 1.0.0

This version removes the option to use "normalization" with clickhouse. It also changes
the schema and database of Airbyte's "raw" tables to be compatible with the new
[Destinations V2](https://docs.airbyte.com/release_notes/upgrading_to_destinations_v2/#what-is-destinations-v2)
format. These changes will likely require updates to downstream dbt / SQL models. After this update, 
Airbyte will only produce the ‘raw’ v2 tables, which store all content in JSON. These changes remove 
the ability to do deduplicated syncs with Clickhouse.  (Clickhouse has an overview)[[https://clickhouse.com/docs/en/integrations/dbt]]
for integrating with dbt If you are interested in the Clickhouse destination gaining the full features
of Destinations V2 (including final tables), click [[https://github.com/airbytehq/airbyte/discussions/35339]] 
to register your interest.

### Database/Schema and the Internal Schema
We have split the raw and final tables into their own schemas,
which in clickhouse is analogous to a `database`. For the Clickhouse destination, this means that
we will only write into the raw table which will live in the `airbyte_internal` database.
The tables written into this schema will be prefixed with either the default database provided in 
the `DB Name` field when configuring clickhouse (but can also be overridden in the connection). You can
change the "raw" database from the default `airbyte_internal` by supplying a value for 
`Raw Table Schema Name`.

For Example:

 - DB Name: `default`
 - Stream Name: `my_stream`

Writes to `airbyte_intneral.default_raw__stream_my_stream`

where as:

 - DB Name: `default`
 - Stream Name: `my_stream`
 - Raw Table Schema Name: `raw_data`

Writes to: `raw_data.default_raw__stream_my_stream`
