-- The side table is CDC-enabled but excluded from the catalog. Its changes
-- advance sys.fn_cdc_get_max_lsn() without producing users records, forcing
-- the alter read to finish on a heartbeat at the CDC upper bound.
USE CdcTest;
GO

ALTER TABLE dbo.users ADD nickname NVARCHAR(50) NULL;
GO

EXEC sys.sp_cdc_enable_table
    @source_schema = N'dbo',
    @source_name = N'users',
    @role_name = NULL,
    @supports_net_changes = 0,
    @capture_instance = N'dbo_users_v2';
GO

INSERT INTO dbo.users (email, nickname)
VALUES ('dave@example.com', 'dave');
GO

WAITFOR DELAY '00:00:10';
GO

IF OBJECT_ID('dbo.side_13544', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.side_13544 (
        id INT IDENTITY(1, 1) PRIMARY KEY,
        payload NVARCHAR(100) NOT NULL
    );
END
GO

IF NOT EXISTS (
    SELECT 1
    FROM cdc.change_tables ct
    JOIN sys.tables t ON ct.source_object_id = t.object_id
    WHERE t.name = 'side_13544'
)
BEGIN
    EXEC sys.sp_cdc_enable_table
        @source_schema = N'dbo',
        @source_name = N'side_13544',
        @role_name = NULL,
        @supports_net_changes = 0;
END
GO

DECLARE @i INT = 1;
WHILE @i <= 20
BEGIN
    BEGIN TRANSACTION;
    INSERT INTO dbo.side_13544 (payload)
    VALUES (CONCAT('side-', @i));
    COMMIT TRANSACTION;
    SET @i += 1;
END
GO

WAITFOR DELAY '00:00:15';
GO
