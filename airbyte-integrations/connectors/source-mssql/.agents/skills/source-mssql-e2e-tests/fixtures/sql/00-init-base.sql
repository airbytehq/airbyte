-- Idempotent base init for source-mssql e2e tests (non-CDC).
-- Creates a TestDb database and a small dbo.sample table with three rows.

IF DB_ID('TestDb') IS NULL
BEGIN
  CREATE DATABASE TestDb;
END
GO

USE TestDb;
GO

IF OBJECT_ID('dbo.sample', 'U') IS NULL
BEGIN
  CREATE TABLE dbo.sample (
    id    INT          NOT NULL PRIMARY KEY,
    label NVARCHAR(64) NOT NULL
  );

  INSERT INTO dbo.sample (id, label) VALUES (1, 'alpha'), (2, 'beta'), (3, 'gamma');
END
GO
