-- Repro for airbytehq/oncall#12162
--   "source-mssql CDC mode fails for tables with spaces in names
--    (message.key.columns regex rejection)"
--
-- Pattern matters: Dynamics 365 Business Central tables look like
-- "[Company Name$TableName$GUID]". Any space in the table or schema
-- name triggers a Debezium config-validation failure at engine startup
-- because the connector emits an unescaped `schema.table:pkcol` entry
-- into Debezium's `message.key.columns`, and Debezium validates each
-- entry against `^\s*([^\s:]+):([^:\s]+)\s*$`.
--
-- Run after 00-init.sql.

USE CdcTest;
GO

IF OBJECT_ID('dbo.[Order Items]', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.[Order Items] (
        id INT IDENTITY(1,1) PRIMARY KEY,
        sku NVARCHAR(50) NOT NULL,
        qty INT NOT NULL
    );
END
GO

IF NOT EXISTS (
    SELECT 1 FROM cdc.change_tables ct
    JOIN sys.tables t ON ct.source_object_id = t.object_id
    WHERE t.name = 'Order Items'
)
BEGIN
    EXEC sys.sp_cdc_enable_table
        @source_schema = N'dbo',
        @source_name   = N'Order Items',
        @role_name     = NULL,
        @supports_net_changes = 0;
END
GO

INSERT INTO dbo.[Order Items] (sku, qty) VALUES
    ('SKU-1', 10),
    ('SKU-2', 5);
GO

SELECT capture_instance FROM CdcTest.cdc.change_tables ORDER BY 1;
GO
