ALTER SYSTEM
SET
max_connections = 150;

CREATE
    DATABASE airbyte;

\connect airbyte;

GRANT ALL ON
DATABASE airbyte TO docker;
