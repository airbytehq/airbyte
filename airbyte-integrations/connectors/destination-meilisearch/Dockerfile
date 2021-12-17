FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION destination-meilisearch

ADD build/distributions/${APPLICATION}*.tar /airbyte

LABEL io.airbyte.version=0.2.10
LABEL io.airbyte.name=airbyte/destination-meilisearch
