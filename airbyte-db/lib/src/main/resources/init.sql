ALTER SYSTEM
SET
max_connections = 200;

CREATE
    DATABASE airbyte;

\connect airbyte;

GRANT ALL ON
DATABASE airbyte TO docker;
