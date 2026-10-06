# Microsoft SQL Server (MSSQL) Migration Guide

## Upgrading to 5.0.0

`NUMERIC` and `DECIMAL` columns with **scale 0** (for example `DECIMAL(10,0)` or `NUMERIC(18,0)`) are now mapped to the Airbyte `integer` type instead of `number`. SQL Server stores these columns as whole numbers, and the new mapping lets downstream destinations preserve their integral semantics (for example, Snowflake materializes them as `NUMBER` rather than `FLOAT`). Columns with a non-zero scale (for example `DECIMAL(10,2)`) are unchanged and continue to map to `number`.

| MSSQL type                         | Current Airbyte Type | New Airbyte Type |
| ---------------------------------- | -------------------- | ---------------- |
| `NUMERIC` / `DECIMAL` with scale 0 | number               | integer          |

### How to tell whether you are affected

Before upgrading, you can confirm whether any of your streams contain an affected column. Version 4.4.12 (and any later 4.4.x) logs a line at discovery/schema-refresh time for every `NUMERIC`/`DECIMAL` column with scale 0:

```
Discovered DECIMAL column with scale 0 (precision=10). A future connector version will map such columns to Airbyte integer instead of number.
```

- If this line does **not** appear in your connector logs, none of your synced streams contain an affected column and the upgrade requires no action.
- If it does appear, the named column(s) will change from `number` to `integer` in 5.0.0.

### For current source-mssql users

- If your streams do not contain any `NUMERIC`/`DECIMAL` column with scale 0, your connection will be unaffected. No further action is required from you.
- If your streams contain at least one affected column, opt in and refresh your schema so the new `integer` type propagates to your destination tables. You generally do _not_ need to reset your stream data. _Note:_ in the case that your sync fails after the type change, please refresh the affected stream's data and rerun the sync. This will drop and recreate the necessary destination tables and reread the source data from the beginning.

If clearing your stream data is an issue, please reach out to Airbyte Cloud support for assistance.

## Upgrading to 4.0.0

Source MSSQL provides incremental sync that can read unlimited sized tables and can resume if the initial read has failed.
Upgrading from previous versions will be seamless and does not require any intervention.

## Upgrading to 3.0.0

This change remapped date, datetime, datetime2, datetimeoffset, smalldatetime, and time data type to their correct Airbyte types. Customers whose streams have columns with the affected datatype must refresh their schema and reset their data. See chart below for the mapping change.

| Mssql type     | Current Airbyte Type | New Airbyte Type  |
| -------------- | -------------------- | ----------------- |
| date           | string               | date              |
| datetime       | string               | timestamp         |
| datetime2      | string               | timestamp         |
| datetimeoffset | string               | timestamp with tz |
| smalldatetime  | string               | timestamp         |
| time           | string               | time              |

For current source-mssql users:

- If your streams do not contain any column of an affected data type, your connection will be unaffected. No further action is required from you.
- If your streams contain at least one column of an affected data type, you can opt in, refresh your schema, but _do not_ reset your stream data. Once the sync starts, the Airbyte platform will trigger a schema change that will propagate to the destination tables. _Note:_ In the case that your sync fails, please reset your data and rerun the sync. This will drop, recreate all the necessary tables, and reread the source data from the beginning.

If resetting your stream data is an issue, please reach out to Airbyte Cloud support for assistance.

## Upgrading to 2.0.0

CDC syncs now has default cursor field called `_ab_cdc_cursor`. You will need to force normalization to rebuild your destination tables by manually dropping the SCD tables, refreshing the connection schema (skipping the reset), and running a sync. Alternatively, you can just run a reset.
