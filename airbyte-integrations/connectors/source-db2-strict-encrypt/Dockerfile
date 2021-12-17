FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION source-db2-strict-encrypt

ADD build/distributions/${APPLICATION}*.tar /airbyte

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/source-db2-strict-encrypt
