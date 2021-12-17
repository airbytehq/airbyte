FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION destination-postgres

ADD build/distributions/${APPLICATION}*.tar /airbyte

LABEL io.airbyte.version=0.3.13
LABEL io.airbyte.name=airbyte/destination-postgres
