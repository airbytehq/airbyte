# Direct-Load Tables

Direct-load is an improvement to [Typing and Deduping](typing-deduping). Airbyte intends to eventually replace typing and deduping with direct-load. Under direct-load, the final tables in your destination are identical to their typed and deduped version, but without the need to store the raw tables in your destination.

## Why direct-loading is superior to typing and deduping

Under Typing and Deduping, during a sync, a destination connector only writes JSON data into a "raw table." At the end of each sync, the connector then executes a SQL query (the "T+D" query) to load new records from that raw table into the true (fully-typed) "final table."

This has two main downsides:

* Unbounded growth in the raw tables (because they're never deduped)
* High warehouse compute spend (because the T+D query does some nontrivial `cast` operations)

Direct-load addresses both of those problems, by offloading the type-casting to the destination connector itself. This allows the connector to load typed data directly into the warehouse (hence the name "direct-load"), and avoids the need to store persistent, non-deduped raw tables in the warehouse.

## What will change?

If you never query the raw tables, you will notice very little difference, other than a reduced warehouse bill. The format and structure of your tables will remain the same. If you query _only_ the raw tables, see the [compatibility support](#raw-tables-compatibility-support) section.

Connectors will continue to populate the `_airbyte_meta` column with any type validation errors. Note that the `reason` field in each change will change (under T+D it was `DESTINATION_TYPECAST_ERROR`; under direct-load it is `DESTINATION_SERIALIZATION_ERROR`). However, if you are using our recommended query style (e.g. `WHERE json_array_length(_airbyte_meta ->> changes) = 0`), this will not impact you.

### Schema evolution

Direct-load connectors may require user intervention in certain schema evolution situations. This is a change from T+D destinations, where schema evolution was handled by triggering a soft reset (which always succeeds, but requires a slow/expensive table rebuild). Direct-load connectors instead execute `alter table` statements (or some equivalent), which may not succeed in all cases.

Specifically, if a column's type is changed, and any historical records contain a value which cannot be cast to the new type, the schema change will fail in direct-load destinations.

If you see such a failure, you have two options:

* Run a refresh, and choose to remove existing records
* Manually update historical records to be valid under the new type

### Record visibility

`Append` syncs will now insert records directly to the target table. This is different from T+D, where new records are first written to the raw table, and not populated to the final table until the end of the sync.

Depending on the destination, `dedup` syncs may periodically upsert records to the target table. `Dedup` syncs will (for most destinations) still write to a separate table during the sync. However, that table only exists for the duration of the sync; after a successful sync, it will be deleted.

`Overwrite` syncs (including any "refresh and remove records" operation) will also continue to use a temporary table, to support Airbyte's no-data-downtime feature.

### Raw tables compatibility support

If you were previously querying the raw tables directly, you may choose to enable the `Legacy raw tables` option on the connector. This is equivalent to the T+D `Disable Final Tables` option: the connector will _only_ write the raw tables, and will _not_ create the final tables at all. Connectors with the `Disable Final Tables` option enabled will automatically have the `Legacy raw tables` option enabled.

The connector no longer supports writing both the raw and final tables in a single connection. If you need to do this, you should configure two destinations, and run connections to them in parallel.
