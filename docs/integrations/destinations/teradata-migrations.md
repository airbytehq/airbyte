# Teradata Vantage Migration Guide

## Upgrading to 1.0.0

This version introduces [Destinations V2](/release_notes/upgrading_to_destinations_v2/#what-is-destinations-v2), which provides better error handling, incremental delivery of data for large syncs, and final table generation. To review the breaking changes, and how to upgrade, see [here](/release_notes/upgrading_to_destinations_v2/#quick-start-to-upgrading). These changes will likely require updates to downstream dbt / SQL models, which we walk through [here](/release_notes/upgrading_to_destinations_v2/#updating-downstream-transformations). Selecting `Upgrade` will upgrade **all** connections using this destination at their next sync. You can manually sync existing connections prior to the next scheduled sync to start the upgrade early.

Worthy of specific mention, this version includes:

- Final table generation
- Per-record error handling

Learn more about what's new in Destinations V2 [here](/platform/using-airbyte/core-concepts/typing-deduping).



### Changes to RAW table structure

OLD Raw Table Columns

- `_airbyte_ab_id`: The column type in Teradata is `VARCHAR(256)`.
- `_airbyte_emitted_at`: The column type in Teradata is `TIMESTAMP(6)`.
- `_airbyte_data`: The column type in Teradata is `JSON`.

V2 Raw Table Columns

- `_airbyte_raw_id`: a unique uuid assigned by Airbyte to each event that is processed. This is the primary index column. The column type in Teradata is `VARCHAR(256)`.
- `_airbyte_extracted_at`: a timestamp representing when the event was pulled from the data source. The column type in Teradata is `TIMESTAMP WITH TIME ZONE`.
- `_airbyte_loaded_at`: a timestamp representing when the row was processed into final table. The column type in Teradata is `TIMESTAMP WITH TIME ZONE`.
- `_airbyte_data`: a json blob representing with the event data. The column type in Teradata is `JSON`.
- `_airbyte_meta`: a json blob representing per-row error/change handling. The column type in Teradata is `JSON`.
- `_airbyte_generation_id`: This is one of metadata field and incremented each time you execute a [refresh](https://docs.airbyte.com/operator-guides/refreshes). The column type in Teradata is `BIGINT`.

[Refer to this guide for more details](https://docs.airbyte.com/understanding-airbyte/airbyte-metadata-fields)



The migration process will take care of Raw table update from OLD format to V2 format. Following the successful migration of v1 raw tables to v2, the v1 raw tables will be dropped. 



