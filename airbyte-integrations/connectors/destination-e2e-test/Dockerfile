FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION destination-e2e-test

ADD build/distributions/${APPLICATION}*.tar /airbyte

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/destination-e2e-test
