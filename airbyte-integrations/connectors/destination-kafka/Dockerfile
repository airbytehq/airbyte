FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION destination-kafka

ADD build/distributions/${APPLICATION}*.tar /airbyte

LABEL io.airbyte.version=0.1.2
LABEL io.airbyte.name=airbyte/destination-kafka
