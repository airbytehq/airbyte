FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION source-bigquery

ADD build/distributions/${APPLICATION}*.tar /airbyte

# Airbyte's build system uses these labels to know what to name and tag the docker images produced by this Dockerfile.
LABEL io.airbyte.version=0.1.4
LABEL io.airbyte.name=airbyte/source-bigquery
