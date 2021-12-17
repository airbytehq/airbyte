FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION destination-redshift

ADD build/distributions/${APPLICATION}*.tar /airbyte

LABEL io.airbyte.version=0.3.23
LABEL io.airbyte.name=airbyte/destination-redshift
