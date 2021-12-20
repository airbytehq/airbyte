FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION source-clickhouse-strict-encrypt

ADD build/distributions/${APPLICATION}*.tar /airbyte

LABEL io.airbyte.version=0.1.2
LABEL io.airbyte.name=airbyte/source-clickhouse-strict-encrypt
