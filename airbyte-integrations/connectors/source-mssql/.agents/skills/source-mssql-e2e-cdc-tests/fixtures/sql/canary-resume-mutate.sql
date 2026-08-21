-- Mutate exactly three rows so the replay read must emit update, delete,
-- and insert CDC events rather than replaying the whole table.

USE CdcTest;
GO

UPDATE dbo.resume_canary
SET email = 'updated-101@example.com'
WHERE id = 101;

DELETE FROM dbo.resume_canary
WHERE id = 102;

INSERT INTO dbo.resume_canary (id, email)
VALUES (104, 'inserted-104@example.com');
GO
