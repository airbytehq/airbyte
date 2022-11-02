FROM airbyte/integration-base-java:dev AS build

WORKDIR /airbyte

ENV APPLICATION source-postgres

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1 && rm -rf ${APPLICATION}.tar

FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION source-postgres

COPY --from=build /airbyte /airbyte

# TODO: placeholder version bump for demo. Remove this before merging.
LABEL io.airbyte.version=1.0.23
LABEL io.airbyte.name=airbyte/source-postgres
