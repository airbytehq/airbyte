USE CdcTest;
GO

UPDATE dbo.ausencia
SET au_fecha = '2026-10-17T00:00:00',
    au_fechad = '2026-10-17',
    au_hora = '15:00:03.9876543',
    au_fechadt2 = '2026-10-17T14:56:58.9876543'
WHERE id = 1;

IF NOT EXISTS (SELECT 1 FROM dbo.ausencia WHERE id = 3)
BEGIN
    INSERT INTO dbo.ausencia (id, au_fecha, au_fechad, au_hora, au_fechadt2)
    VALUES (3, '2026-10-18T00:00:00', '2026-10-18', '16:00:04.1234567', '2026-10-18T15:57:59.1234567');
END
GO
