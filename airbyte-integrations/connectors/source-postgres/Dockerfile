FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION source-postgres

ADD build/distributions/${APPLICATION}*.tar /airbyte

LABEL io.airbyte.version=0.3.18
LABEL io.airbyte.name=airbyte/source-postgres
