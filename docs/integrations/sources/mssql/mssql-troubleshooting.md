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

