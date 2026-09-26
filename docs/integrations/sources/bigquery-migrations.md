# BigQuery Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 rebuilds the BigQuery source on Airbyte's Bulk CDK. It reads tables through the [BigQuery Storage Read API](https://cloud.google.com/bigquery/docs/reference/storage) in parallel read streams, emits state during full refresh syncs so that large tables resume after an interruption, discovers nested `STRUCT` and `ARRAY` schemas and primary key constraints, supports speed mode, and fixes the value bugs listed under [Value changes](#value-changes). Saved configurations load unchanged, and the incremental sync state written by earlier versions is understood: a stream resumes after its last cursor value instead of reading the table again.

**This version changes the schema of some streams, so it is a breaking change for connections that sync the affected columns.**

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
- `DATETIME`, `TIME` and `TIMESTAMP` values keep their microseconds. Versions 0.4.x truncated them to seconds.
- `JSON` values are emitted as JSON instead of a string containing JSON.
- Dates before 1582-10-15 and timestamps in year 1 come through unchanged. Versions 0.4.x shifted them by two days.

### Other changes

- **Service Account Key JSON** must contain a service account key. Versions 0.4.x fell back to the credentials of the environment when the field was empty.
- The connection test fails with `Discovered zero tables` when the dataset, or the whole project when **Dataset ID** is empty, contains no tables.
- Full refresh syncs emit state while they run and resume after an interruption instead of starting over.

### What to do

1. Upgrade the connector, then refresh the source schema of each connection that uses it.
2. If a connection syncs a column whose type changed, the refresh propagates the new type to the destination. If the next sync fails because of the type change, refresh the affected streams so that the destination tables are recreated.
3. If a connection uses a `BOOL`, `BYTES`, `JSON`, `STRUCT` or `ARRAY` column as its incremental cursor, choose a new cursor column and refresh the stream.
4. If a source is configured without a service account key, paste the JSON key of a service account into **Service Account Key JSON**. See [Service account](bigquery.md#service-account) for the roles it needs, including the one that enables the Storage Read API.

Nothing else is required. Incremental streams continue from their saved cursor value.
