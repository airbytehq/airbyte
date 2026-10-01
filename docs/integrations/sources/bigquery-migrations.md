import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# BigQuery Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 rebuilds the BigQuery source on Airbyte's Bulk CDK. It changes the discovered schema of most streams and the format of some values, so it is a breaking change for every connection that uses the connector: **each connection must refresh its source schema before its first sync on 1.0.0.** Saved configurations and incremental cursor state carry over, except for sources that relied on the credentials of the environment (see [Other changes](#other-changes)).

What else is new: on Airbyte Cloud the connector reads tables through the [BigQuery Storage Read API](https://cloud.google.com/bigquery/docs/reference/storage) in parallel read streams, full refresh syncs emit state while they run so that large tables resume after an interruption, nested `STRUCT` and `ARRAY` schemas and primary key constraints are discovered, speed mode is supported, and the value bugs listed under [Value changes](#value-changes) are fixed.

### Schema changes

The catalog the connector discovers differs from versions 0.4.x in the following ways.

| BigQuery type | Airbyte type up to 0.4.5                                            | Airbyte type in 1.0.0                      |
| :------------ | :------------------------------------------------------------------ | :----------------------------------------- |
| `DATE`        | string                                                              | date                                       |
| `DATETIME`    | string                                                              | timestamp without timezone                 |
| `TIME`        | string                                                              | time without timezone                      |
| `TIMESTAMP`   | string                                                              | timestamp with timezone                    |
| `JSON`        | string                                                              | json                                       |
| `BYTES`       | string                                                              | string with `contentEncoding: base64`      |
| `STRUCT`      | object without a schema                                             | object with the nested fields and types    |
| `ARRAY<T>`    | array without a schema, or the scalar type for a `REPEATED` scalar  | array whose items have the type of `T`     |

- Tables with a `PRIMARY KEY` constraint report it as the source-defined primary key.
- Incremental sync is offered only for streams that have a column of a supported cursor type (`INT64`, `NUMERIC`, `BIGNUMERIC`, `FLOAT64`, `STRING`, `DATE`, `DATETIME`, `TIME`, `TIMESTAMP`), and only those columns can be chosen as the cursor. Versions 0.4.x accepted any column.
- BigQuery ML models are no longer discovered as streams.

### Value changes

- `DATE` values are emitted as `2023-07-12` instead of `2023-07-12T00:00:00Z`.
- `DATETIME` values are emitted without a `Z` suffix, for example `2023-07-12T10:00:00.123456` instead of `2023-07-12T10:00:00Z`. Versions 0.4.x labelled these zone-less values as UTC.
- `DATETIME` and `TIMESTAMP` values keep their microseconds. Versions 0.4.x truncated them to seconds. `TIME` values already kept their microseconds.
- `JSON` values are emitted as JSON instead of a string containing JSON.
- Dates before 1582-10-15 and timestamps in year 1 come through unchanged. Versions 0.4.x shifted them by two days.

### Other changes

- **Service Account Key JSON** must contain a service account key. Versions 0.4.x fell back to the credentials of the environment when the field was empty.
- The connection test fails with `Discovered zero tables` when the dataset, or the whole project when **Dataset ID** is empty, contains no tables.
- Full refresh syncs emit state while they run and resume after an interruption instead of starting over.

### What to do

Every connection needs step 1. Steps 2 to 4 apply only in the cases they describe.

:::caution
Like every database source, this connector reads the rows that BigQuery holds at sync time and has no start date. If a stream syncs in **Incremental | Append** or **Incremental | Append + Deduped** and BigQuery no longer holds some rows that were synced earlier, because they were deleted or removed by table or partition expiration, a **Refresh and remove records** or a **Clear** drops those rows from the destination for good. Use **Refresh and retain records** when you refresh such a stream, and snapshot the destination table first if you are unsure. See [Refreshes](/platform/operator-guides/refreshes).
:::

1. Upgrade the connector, then refresh the source schema of each connection that uses it and save the connection without clearing data. Until a connection has refreshed its schema, every stream with a column whose type changed fails with an error that asks for the refresh.
2. Run a sync. The destination applies the new column types during that sync, and Full Refresh | Overwrite streams need nothing beyond the schema refresh. If the sync fails because of the type change, refresh the failing streams with **Refresh and retain records**, which keeps the records already in the destination and reads the stream again from the start.
3. If a connection uses a `BOOL`, `BYTES`, `JSON`, `STRUCT` or `ARRAY` column as its incremental cursor, choose a new cursor column. The saved cursor value belongs to the old column, so the stream is read again in full on its next sync. The same happens when a saved cursor value cannot be interpreted as the column's type.
4. If a source is configured without a service account key, paste the JSON key of a service account into **Service Account Key JSON**. See [Service account](bigquery.md#service-account) for the roles it needs, including the one that enables the Storage Read API (Airbyte Cloud only).

Incremental streams whose cursor column keeps its type continue from their saved cursor value.

### Downstream impact

- Column types change in the destination: `DATE`, `DATETIME`, `TIME` and `TIMESTAMP` columns become date and time types, `JSON` columns become a native JSON column, and `BYTES` columns declare their base64 encoding. SQL, `dbt` models and dashboards that parse these columns as strings, for example with `PARSE_DATE` or `JSON_EXTRACT` on a string column, need to be updated.
- `DATETIME` values lose the `Z` suffix and `DATE` values lose the midnight time part, so string comparisons against the old format stop matching.
- Destinations that append, and file or object storage destinations, hold rows in both formats: rows synced before the upgrade keep the old string values and rows synced after it have the new ones, for example `"2023-07-12T00:00:00Z"` next to `"2023-07-12"`, or a JSON string next to a JSON object. How a typed destination converts the rows it already holds when a column changes type depends on the destination, so check a sample of pre-upgrade rows after the first sync.
- Tables with a `PRIMARY KEY` constraint now report it as the source-defined primary key. BigQuery declares these constraints but does not enforce them, so a table with duplicate key values has its duplicates merged by the **Incremental | Append + Deduped** sync mode. Check the primary key of the streams that use that mode after the schema refresh.

### Rolling back

Pinning the connector back to 0.4.5 after a sync on 1.0.0 does not undo the upgrade. Version 0.4.5 does not understand the state that 1.0.0 writes, so incremental streams start over from the beginning on their next sync, and the destination columns keep the types that 1.0.0 gave them until the schema is refreshed again.

## Connector upgrade guide

<MigrationGuide />
