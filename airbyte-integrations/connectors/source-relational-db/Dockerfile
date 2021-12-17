FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION source-relational-db

ADD build/distributions/${APPLICATION}*.tar /airbyte

LABEL io.airbyte.version=0.3.0
LABEL io.airbyte.name=airbyte/source-relational-db
