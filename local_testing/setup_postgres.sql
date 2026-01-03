CREATE TABLE test_table (id serial PRIMARY KEY, value varchar(256), ts_tz timestamptz);
INSERT INTO test_table (value, ts_tz) VALUES ('some-value', '2025-06-18 05:06:07');
