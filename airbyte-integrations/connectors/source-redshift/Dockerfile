FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION source-redshift

ADD build/distributions/${APPLICATION}*.tar /airbyte

LABEL io.airbyte.version=0.3.4
LABEL io.airbyte.name=airbyte/source-redshift
