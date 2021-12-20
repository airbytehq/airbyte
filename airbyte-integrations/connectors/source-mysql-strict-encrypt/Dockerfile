FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION source-mysql-strict-encrypt

ADD build/distributions/${APPLICATION}*.tar /airbyte

LABEL io.airbyte.version=0.1.5
LABEL io.airbyte.name=airbyte/source-mysql-strict-encrypt
