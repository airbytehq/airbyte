USE CdcTest;
GO

IF OBJECT_ID('dbo.repro_13433', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.repro_13433 (
        id INT NOT NULL PRIMARY KEY,
        v INT NOT NULL
    );
END
GO

IF NOT EXISTS (
    SELECT 1
    FROM cdc.change_tables ct
    JOIN sys.tables t ON t.object_id = ct.source_object_id
    WHERE t.name = 'repro_13433'
)
BEGIN
    EXEC sys.sp_cdc_enable_table
        @source_schema = N'dbo',
        @source_name = N'repro_13433',
        @role_name = NULL,
        @supports_net_changes = 0;
END
GO

IF NOT EXISTS (SELECT 1 FROM dbo.repro_13433 WHERE id = 1)
    INSERT INTO dbo.repro_13433 (id, v) VALUES (1, 1);
IF NOT EXISTS (SELECT 1 FROM dbo.repro_13433 WHERE id = 2)
    INSERT INTO dbo.repro_13433 (id, v) VALUES (2, 2);
GO

DECLARE @i INT = 1;
DECLARE @tableName NVARCHAR(128);
DECLARE @sql NVARCHAR(MAX);
WHILE @i <= 350
BEGIN
    SET @tableName = N'catalog_static_13433_' + RIGHT('000' + CAST(@i AS VARCHAR(3)), 3);
    IF OBJECT_ID(N'dbo.' + @tableName, 'U') IS NULL
    BEGIN
        SET @sql = N'CREATE TABLE dbo.' + QUOTENAME(@tableName) +
            N' (id INT NOT NULL PRIMARY KEY, v INT NOT NULL);';
        EXEC sp_executesql @sql;
    END;
    IF NOT EXISTS (
        SELECT 1
        FROM cdc.change_tables ct
        JOIN sys.tables t ON t.object_id = ct.source_object_id
        WHERE t.name = @tableName
    )
    BEGIN
        EXEC sys.sp_cdc_enable_table
            @source_schema = N'dbo',
            @source_name = @tableName,
            @role_name = NULL,
            @supports_net_changes = 0;
    END;
    SET @i += 1;
END;
GO

DECLARE @i INT = 1;
DECLARE @tableName NVARCHAR(128);
DECLARE @sql NVARCHAR(MAX);
WHILE @i <= 50
BEGIN
    SET @tableName = N'noise_13433_' + RIGHT('000' + CAST(@i AS VARCHAR(3)), 3);
    IF OBJECT_ID(N'dbo.' + @tableName, 'U') IS NULL
    BEGIN
        SET @sql = N'CREATE TABLE dbo.' + QUOTENAME(@tableName) +
            N' (id INT NOT NULL PRIMARY KEY, v INT NOT NULL);';
        EXEC sp_executesql @sql;
    END;
    IF NOT EXISTS (
        SELECT 1
        FROM cdc.change_tables ct
        JOIN sys.tables t ON t.object_id = ct.source_object_id
        WHERE t.name = @tableName
    )
    BEGIN
        EXEC sys.sp_cdc_enable_table
            @source_schema = N'dbo',
            @source_name = @tableName,
            @role_name = NULL,
            @supports_net_changes = 0;
    END;
    SET @i += 1;
END;
GO
