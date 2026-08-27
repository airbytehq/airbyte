# Troubleshooting Microsoft SQL Server (MSSQL) Sources

## Connector Limitations

### Adding columns to existing tables with CDC

When using SQL Server (MSSQL) in CDC mode, adding new columns to existing tables using `ALTER TABLE <table> ADD <column>` 
will **not** automatically be captured by the CDC stream. As a result, the column will be excluded from CDC tracking 
(while it might appear in the Schema section, it will return zero records). To ensure the column is tracked, 
we recommend disabling and re-enabling CDC on the table. This will create a new capture instance that reflects 
the updated structure and includes the new column:

1. Disabling CDC on the table:
```sql
EXEC sys.sp_cdc_disable_table
    @source_schema = N'<schema>',
    @source_name   = N'<table>',
    @capture_instance = N'<capture instance (typically schema_table)>'
```
2. Enabling CDC on the table:
```sql
EXEC sys.sp_cdc_enable_table
    @source_schema = N'<schema>',
    @source_name   = N'<table>',
    @role_name     = NULL
```
Note: You may want to set a `@role_name` or any other arguments similarly to how they were set when CDC was enabled in the first place.

3. (Optional) Validate that all columns are being captured:
```sql
EXEC sys.sp_cdc_get_captured_columns 
    @capture_instance = N'<capture instance (typically schema_table)>';
```

### SSH tunnel limitation (Azure SQL Managed Instance)

:::info
This limitation applies only to Azure SQL **Managed Instance**. Azure SQL Database can connect through an SSH tunnel normally.
:::

#### Error

Connections to an Azure SQL Managed Instance through an SSH tunnel may fail the source's connection check with one of the
following errors:

- `Error code: 40532; Cannot open server "localhost" requested by the login. The login failed.`
- `Login failed for user '<user>@<instance-name>'.` (when the username includes an `@instance-name` suffix)

#### Cause

Azure SQL Managed Instance requires the instance hostname to route connections correctly. When Airbyte connects through
an SSH tunnel, the connection uses `localhost` instead of the Managed Instance hostname, causing the login to fail.

The `<user>@<instance-name>` workaround supported by Azure SQL Database **does not apply to Azure SQL Managed Instance**.

#### Workaround

Connect without a tunnel, using the Managed Instance [public endpoint](https://learn.microsoft.com/en-us/azure/azure-sql/managed-instance/public-endpoint-configure?view=azuresql&tabs=azure-portal):

1. In the Azure portal, enable the public endpoint on your Managed Instance (Security > Networking). The hostname should look like this: `<instance-name>.public.<dns-zone>.database.windows.net`.
2. In the network security group attached to the Managed Instance subnet, add an inbound rule allowing TCP port 3342 from [Airbyte's IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) only.
3. In the Airbyte source configuration, use the following settings:
   - **Port:** 3342 (the public endpoint does not use 1433)
   - **SSH Tunnel Method:** No Tunnel
   - **Username:** A plain SQL username without an @instance suffix
