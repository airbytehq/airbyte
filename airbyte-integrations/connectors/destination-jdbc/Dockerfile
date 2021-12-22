FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION destination-jdbc

ADD build/distributions/${APPLICATION}*.tar /airbyte

LABEL io.airbyte.version=0.3.7
LABEL io.airbyte.name=airbyte/destination-jdbc
