FROM scratch

## TODO Add your dockerfile instructions here

FROM airbyte/source-first-connector:dev

WORKDIR /airbyte

ENV APPLICATION source-first-connector



# Airbyte's build system uses these labels to know what to name and tag the docker images produced by this Dockerfile.
LABEL io.airbyte.name=airbyte/source-first-connector
LABEL io.airbyte.version=0.1.0