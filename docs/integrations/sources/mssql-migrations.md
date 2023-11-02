# Microsoft SQL Server (MSSQL) Migration Guide

## Upgrading to 3.0.0
This change remapped date, datetime, datetime2, datetimeoffset, smalldatetime, and time data type to their correct Airbyte types. Customers whose streams have columns with the affected datatype must refresh their schema and reset their data. See chart below for the mapping change.

| Mssql type     | Current Airbyte Type | New Airbyte Type  |
|----------------|----------------------|-------------------|
| date           | string               | date              |
| datetime       | string               | timestamp         |
| datetime2      | string               | timestamp         |
| datetimeoffset | string               | timestamp with tz |
| smalldatetime  | string               | timestamp         |
| time           | string               | time              |

If your streams do not contain any column of an affected data type, your connection will be unaffected. After opting in to the new version, refresh your schema, but no stream resets are necessary.

If your streams contain at least one column of an affected data type:
1) If you want to continue writing to the same unaltered destination tables, you can opt in, refresh your schema, but ***do not reset data*** of affected streams. This will preserve the destination table schema.
2) If you want the destination to properly recognize the new data type, you can opt in, refresh your schema, and reset the data of affected streams. This will ensure a new table creation in the destination.
3) If you want the destination to properly recognize the new data type, but resetting your stream is an issue, please reach out to Airbyte Cloud support for assistance.

## Upgrading to 2.0.0
CDC syncs now has default cursor field called `_ab_cdc_cursor`. You will need to force normalization to rebuild your destination tables by manually dropping the SCD tables, refreshing the connection schema (skipping the reset), and running a sync. Alternatively, you can just run a reset.
