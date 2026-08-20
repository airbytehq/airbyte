-- Seed the table used by canary-resume.sh.
-- Idempotent when applied after 00-init-cdc.sql.

USE CdcTest;
GO

IF OBJECT_ID('dbo.resume_canary', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.resume_canary (
        id INT NOT NULL PRIMARY KEY,
        email NVARCHAR(200) NOT NULL
    );
END
GO

IF OBJECT_ID('dbo.resume_canary_noise', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.resume_canary_noise (
        id INT NOT NULL PRIMARY KEY
    );
END
GO

IF NOT EXISTS (
    SELECT 1
    FROM cdc.change_tables ct
    JOIN sys.tables t ON ct.source_object_id = t.object_id
    WHERE t.name = 'resume_canary'
)
BEGIN
    EXEC sys.sp_cdc_enable_table
        @source_schema = N'dbo',
        @source_name = N'resume_canary',
        @role_name = NULL,
        @supports_net_changes = 0;
END
GO

IF NOT EXISTS (
    SELECT 1
    FROM cdc.change_tables ct
    JOIN sys.tables t ON ct.source_object_id = t.object_id
    WHERE t.name = 'resume_canary_noise'
)
BEGIN
    EXEC sys.sp_cdc_enable_table
        @source_schema = N'dbo',
        @source_name = N'resume_canary_noise',
        @role_name = NULL,
        @supports_net_changes = 0;
END
GO

IF NOT EXISTS (SELECT 1 FROM dbo.resume_canary WHERE id = 101)
    INSERT INTO dbo.resume_canary (id, email) VALUES (101, 'seed-101@example.com');
IF NOT EXISTS (SELECT 1 FROM dbo.resume_canary WHERE id = 102)
    INSERT INTO dbo.resume_canary (id, email) VALUES (102, 'seed-102@example.com');
IF NOT EXISTS (SELECT 1 FROM dbo.resume_canary WHERE id = 103)
    INSERT INTO dbo.resume_canary (id, email) VALUES (103, 'seed-103@example.com');
GO

IF NOT EXISTS (SELECT 1 FROM dbo.resume_canary_noise WHERE id = 1)
    INSERT INTO dbo.resume_canary_noise (id) VALUES (1);
GO
