FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION source-jdbc

ADD build/distributions/${APPLICATION}*.tar /airbyte

LABEL io.airbyte.version=0.3.1
LABEL io.airbyte.name=airbyte/source-jdbc
