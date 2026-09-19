-- Keep the resume read's upper bound beyond Erin while side-table changes
-- remain outside the configured users stream.
USE CdcTest;
GO

INSERT INTO dbo.users (email, nickname)
VALUES ('erin@example.com', 'erin');
GO

DECLARE @i INT = 1;
WHILE @i <= 5
BEGIN
    BEGIN TRANSACTION;
    INSERT INTO dbo.side_13544 (payload)
    VALUES (CONCAT('resume-side-', @i));
    COMMIT TRANSACTION;
    SET @i += 1;
END
GO

WAITFOR DELAY '00:00:15';
GO
