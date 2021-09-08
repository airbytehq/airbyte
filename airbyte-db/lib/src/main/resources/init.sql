CREATE
    DATABASE airbyte;

\connect airbyte;

GRANT ALL ON
DATABASE airbyte TO docker;
