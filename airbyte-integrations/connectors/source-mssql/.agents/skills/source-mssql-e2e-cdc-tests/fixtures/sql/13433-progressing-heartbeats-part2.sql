USE CdcTest;
GO

DECLARE @i INT = 1;
DECLARE @tableName NVARCHAR(128);
DECLARE @sql NVARCHAR(MAX);
DECLARE @row INT = 1;
WHILE @row <= 20000
BEGIN
    SET @i = ((@row - 1) % 50) + 1;
    SET @tableName = N'noise_13433_' + RIGHT('000' + CAST(@i AS VARCHAR(3)), 3);
    SET @sql = N'INSERT INTO dbo.' + QUOTENAME(@tableName) +
        N' (id, v) VALUES (' + CAST(@row AS NVARCHAR(20)) + N', ' +
        CAST(@row AS NVARCHAR(20)) + N');';
    EXEC sp_executesql @sql;
    SET @row += 1;
END;
GO

DECLARE @lastCount BIGINT = -1;
DECLARE @stable INT = 0;
DECLARE @count BIGINT;
WHILE @stable < 3
BEGIN
    SELECT @count = COUNT_BIG(*) FROM cdc.lsn_time_mapping;
    IF @count = @lastCount
        SET @stable += 1;
    ELSE
        SET @stable = 0;
    SET @lastCount = @count;
    IF @stable < 3
        WAITFOR DELAY '00:00:05';
END;
SELECT sys.fn_cdc_get_max_lsn() AS max_lsn, COUNT_BIG(*) AS lsn_time_mapping_count
FROM cdc.lsn_time_mapping;
GO
