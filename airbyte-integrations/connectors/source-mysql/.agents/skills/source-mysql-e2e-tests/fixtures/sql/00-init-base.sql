-- Idempotent base init for source-mysql e2e tests (non-CDC).
-- The test_db database is created by the container (MYSQL_DATABASE); this
-- fixture just (re)creates a small sample table with three rows.

DROP TABLE IF EXISTS sample;

CREATE TABLE sample (
  id    INT          NOT NULL PRIMARY KEY,
  label VARCHAR(64)  NOT NULL
);

INSERT INTO sample (id, label) VALUES
  (1, 'alpha'),
  (2, 'beta'),
  (3, 'gamma');
