FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION destination-pulsar

ADD build/distributions/${APPLICATION}*.tar /airbyte

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/destination-pulsar
