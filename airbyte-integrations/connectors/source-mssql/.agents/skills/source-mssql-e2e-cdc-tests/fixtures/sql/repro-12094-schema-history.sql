-- Repro for airbytehq/oncall#12094
--   "[source-mssql] CDC schema history grows unbounded -- stores DDL
--    for all tables, not just captured streams"
--
-- We create N "noise" tables that are NOT CDC-enabled. Only `dbo.users`
-- is captured. After a sync configured with just `dbo.users`, Debezium
-- still loads schema for every table in the database into its
-- "list of capture schema tables", proving the bug.
--
-- Run after 00-init.sql.

USE CdcTest;
GO

DECLARE @i INT = 1;
DECLARE @sql NVARCHAR(500);
WHILE @i <= 30
BEGIN
    SET @sql = N'IF OBJECT_ID(N''dbo.noise_' + CAST(@i AS NVARCHAR(10)) +
               N''', ''U'') IS NULL CREATE TABLE dbo.noise_' +
               CAST(@i AS NVARCHAR(10)) +
               N' (id INT IDENTITY(1,1) PRIMARY KEY, payload NVARCHAR(100) NOT NULL DEFAULT '''')';
    EXEC sp_executesql @sql;
    SET @i = @i + 1;
END
GO

-- CDC-enabled tables (expect: only dbo.users from 00-init.sql,
-- and optionally dbo.[Order Items] if you also ran the 12162 repro):
SELECT capture_instance FROM CdcTest.cdc.change_tables ORDER BY 1;

-- Total user tables in this database (expect: 30 noise + dbo.users +
-- optionally dbo.[Order Items], i.e. 31 or 32):
SELECT COUNT(*) AS total_user_tables
FROM sys.tables t
WHERE t.is_ms_shipped = 0;
GO
