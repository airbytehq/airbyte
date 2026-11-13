-- Bootstrap a CDC-ready DB on a fresh `mcr.microsoft.com/mssql/server:2022-latest`
-- container. Idempotent: safe to re-run.
--
-- Prereq: the container must have been started with -e MSSQL_AGENT_ENABLED=true
-- so SQL Server Agent is running (CDC capture jobs are Agent jobs).

USE master;
GO

-- Drop any prior CdcTest database to guarantee a clean slate. Earlier
-- worked examples (repro-12094, repro-12162) add tables on top of this
-- one, so dropping here ensures every run starts from the same baseline
-- regardless of which fixtures were applied previously.
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

INSERT INTO dbo.users (email) VALUES
    ('alice@example.com'),
    ('bob@example.com'),
    ('carol@example.com');
GO

SELECT name, is_cdc_enabled FROM sys.databases WHERE name = 'CdcTest';
SELECT capture_instance, source_object_id FROM CdcTest.cdc.change_tables;
GO
