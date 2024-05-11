# Microsoft SQL Server (MSSQL) Migration Guide

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
