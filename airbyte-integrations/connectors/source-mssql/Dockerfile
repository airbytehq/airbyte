FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION source-mssql

ADD build/distributions/${APPLICATION}*.tar /airbyte

LABEL io.airbyte.version=0.3.10
LABEL io.airbyte.name=airbyte/source-mssql
