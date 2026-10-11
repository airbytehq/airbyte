-- Idempotent CDC fixture for source-mysql e2e tests.

DROP DATABASE IF EXISTS cdc_test;
CREATE DATABASE cdc_test;
USE cdc_test;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(200) NOT NULL,
  created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
);

INSERT INTO users (email) VALUES
  ('alice@example.com'),
  ('bob@example.com'),
  ('carol@example.com');
