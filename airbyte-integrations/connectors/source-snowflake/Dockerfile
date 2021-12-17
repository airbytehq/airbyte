FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION source-snowflake

ADD build/distributions/${APPLICATION}*.tar /airbyte

LABEL io.airbyte.version=0.1.2
LABEL io.airbyte.name=airbyte/source-snowflake
