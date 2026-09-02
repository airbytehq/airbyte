-- airbytehq/airbyte#85286 — between-phase mutation. Inserts one row into
-- dbo.users after the baseline snapshot so that a replay can distinguish
-- "restarted the snapshot" (all 4 rows) from "resumed CDC" (only this row)
-- from "skipped the stream" (0 rows). Idempotent.
USE CdcTest;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.users WHERE email = 'dave@example.com')
BEGIN
    INSERT INTO dbo.users (email) VALUES ('dave@example.com');
END
GO

SELECT id, email FROM dbo.users ORDER BY id;
GO
