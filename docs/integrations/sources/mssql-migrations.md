# Microsoft SQL Server (MSSQL) Migration Guide

## Upgrading to 3.0.0
Remapped date, smalldatetime, datetime, datetime2, time, and datetimeoffset datatype to their correct Airbyte types. Customers whose streams have columns with the affected datatype must refresh their schema and reset their data.
## Upgrading to 2.0.0
CDC syncs now has default cursor field called `_ab_cdc_cursor`. You will need to force normalization to rebuild your destination tables by manually dropping the SCD tables, refreshing the connection schema (skipping the reset), and running a sync. Alternatively, you can just run a reset.
