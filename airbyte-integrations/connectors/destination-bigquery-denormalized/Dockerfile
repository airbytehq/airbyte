FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION destination-bigquery-denormalized

ADD build/distributions/${APPLICATION}*.tar /airbyte

LABEL io.airbyte.version=0.1.11
LABEL io.airbyte.name=airbyte/destination-bigquery-denormalized
