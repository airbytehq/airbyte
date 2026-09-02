-- airbytehq/airbyte#85286 — variant of 00-init-cdc.sql that seeds dbo.users
-- BEFORE enabling CDC on the table. The seed rows therefore exist only in
-- the base table and never in cdc.dbo_users_CT, so they can only ever be
-- emitted by the initial snapshot, never by the Debezium change stream.
-- That makes "snapshot skipped" observable as "seed rows missing".
-- Idempotent: drops and recreates CdcTest like 00-init-cdc.sql does.

USE master;
GO

IF DB_ID('CdcTest') IS NOT NULL
BEGIN
    ALTER DATABASE CdcTest SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE CdcTest;
END
GO

CREATE DATABASE CdcTest;
GO

USE CdcTest;
GO

IF NOT EXISTS (SELECT 1 FROM sys.databases WHERE name = 'CdcTest' AND is_cdc_enabled = 1)
BEGIN
    EXEC sys.sp_cdc_enable_db;
END
GO

IF OBJECT_ID('dbo.users', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.users (
        id INT IDENTITY(1,1) PRIMARY KEY,
        email NVARCHAR(200) NOT NULL,
        created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
    );
END
GO

INSERT INTO dbo.users (email) VALUES
    ('alice@example.com'),
    ('bob@example.com'),
    ('carol@example.com');
GO

IF NOT EXISTS (
    SELECT 1 FROM cdc.change_tables ct
    JOIN sys.tables t ON ct.source_object_id = t.object_id
    WHERE t.name = 'users'
)
BEGIN
    EXEC sys.sp_cdc_enable_table
        @source_schema = N'dbo',
        @source_name   = N'users',
        @role_name     = NULL,
        @supports_net_changes = 0;
END
GO

SELECT name, is_cdc_enabled FROM sys.databases WHERE name = 'CdcTest';
SELECT capture_instance, source_object_id FROM CdcTest.cdc.change_tables;
GO
