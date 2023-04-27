FROM airbyte/integration-base-java:dev AS build

WORKDIR /airbyte

ENV APPLICATION source-alloydb-strict-encrypt

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1 && rm -rf ${APPLICATION}.tar

FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION source-alloydb-strict-encrypt

COPY --from=build /airbyte /airbyte

LABEL io.airbyte.version=2.0.28
LABEL io.airbyte.name=airbyte/source-alloydb-strict-encrypt
