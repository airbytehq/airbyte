# Troubleshooting Microsoft SQL Server (MSSQL) Sources

## Connector Limitations

### Adding columns to existing tables with CDC

When working with source SQL Server (MSSQL) in CDC mode, Making alteration to a table such as `ALTER TABLE <table> ADD <column>` will not automatically be reflected in the CDC stream.
The easiest way of making CDC match the new structure of a table. You can disable and re-enable CDC on the table. This will create a new capture instance for the table with the new structure:
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

You can validate which columns are being captured by running the following query:
```sql
EXEC sys.sp_cdc_get_captured_columns 
    @capture_instance = N'<capture instance (typically schema_table)>';
```

