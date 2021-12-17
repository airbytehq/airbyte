FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION source-e2e-test

ADD build/distributions/${APPLICATION}*.tar /airbyte

LABEL io.airbyte.version=0.1.1
LABEL io.airbyte.name=airbyte/source-e2e-test
