FROM airbyte/integration-base-java:dev AS build

WORKDIR /airbyte

ENV APPLICATION source-dynamodb

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1 && rm -rf ${APPLICATION}.tar

FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION source-dynamodb

COPY --from=build /airbyte /airbyte

# Airbyte's build system uses these labels to know what to name and tag the docker images produced by this Dockerfile.
LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/source-dynamodb
