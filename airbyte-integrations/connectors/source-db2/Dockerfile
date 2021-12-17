FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION source-db2

ADD build/distributions/${APPLICATION}*.tar /airbyte

LABEL io.airbyte.version=0.1.3
LABEL io.airbyte.name=airbyte/source-db2
