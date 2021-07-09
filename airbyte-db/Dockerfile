FROM postgres:13-alpine

COPY src/main/resources/schema.sql /docker-entrypoint-initdb.d/000_init.sql
COPY src/main/resources/config_schema.sql /docker-entrypoint-initdb.d/001_init.sql
