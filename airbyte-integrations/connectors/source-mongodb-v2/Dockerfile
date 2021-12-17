FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION source-mongodb-v2

ADD build/distributions/${APPLICATION}*.tar /airbyte

LABEL io.airbyte.version=0.1.9
LABEL io.airbyte.name=airbyte/source-mongodb-v2
