FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION destination-oracle

ADD build/distributions/${APPLICATION}*.tar /airbyte

LABEL io.airbyte.version=0.1.12
LABEL io.airbyte.name=airbyte/destination-oracle
