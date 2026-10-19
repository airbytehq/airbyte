USE CdcTest;
GO

IF TYPE_ID(N'dbo.Fecha') IS NULL
    EXEC(N'CREATE TYPE dbo.Fecha FROM datetime NULL');
IF TYPE_ID(N'dbo.FechaD') IS NULL
    EXEC(N'CREATE TYPE dbo.FechaD FROM date NULL');
IF TYPE_ID(N'dbo.Hora') IS NULL
    EXEC(N'CREATE TYPE dbo.Hora FROM time(7) NULL');
IF TYPE_ID(N'dbo.FechaDt2') IS NULL
    EXEC(N'CREATE TYPE dbo.FechaDt2 FROM datetime2 NULL');
GO

IF OBJECT_ID(N'dbo.ausencia', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.ausencia (
        id INT PRIMARY KEY,
        au_fecha dbo.Fecha,
        au_fechad dbo.FechaD,
        au_hora dbo.Hora,
        au_fechadt2 dbo.FechaDt2
    );
END
GO

IF NOT EXISTS (SELECT 1 FROM dbo.ausencia WHERE id = 1)
BEGIN
    INSERT INTO dbo.ausencia (id, au_fecha, au_fechad, au_hora, au_fechadt2)
    VALUES (1, '2026-10-15T00:00:00', '2026-10-15', '13:00:01.1234567', '2026-10-15T12:34:56.1234567');

    INSERT INTO dbo.ausencia (id, au_fecha, au_fechad, au_hora, au_fechadt2)
    VALUES (2, '2026-10-16T00:00:00', '2026-10-16', '14:00:02.7654321', '2026-10-16T13:45:57.7654321');
END
GO

IF NOT EXISTS (
    SELECT 1
    FROM cdc.change_tables ct
    JOIN sys.tables t ON ct.source_object_id = t.object_id
    WHERE t.name = N'ausencia'
)
BEGIN
    EXEC sys.sp_cdc_enable_table
        @source_schema = N'dbo',
        @source_name = N'ausencia',
        @role_name = NULL,
        @supports_net_changes = 0;
END
GO
