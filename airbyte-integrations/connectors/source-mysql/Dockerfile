FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION source-mysql

ADD build/distributions/${APPLICATION}*.tar /airbyte

LABEL io.airbyte.version=0.4.12

LABEL io.airbyte.name=airbyte/source-mysql
