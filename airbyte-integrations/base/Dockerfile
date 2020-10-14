FROM debian:10.5-slim

WORKDIR /airbyte

COPY entrypoint.sh .

ENTRYPOINT ["/airbyte/entrypoint.sh"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/integration-base
