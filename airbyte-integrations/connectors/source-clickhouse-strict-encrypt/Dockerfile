FROM airbyte/integration-base-java:dev AS build

WORKDIR /airbyte

ENV APPLICATION source-clickhouse-strict-encrypt

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1 && rm -rf ${APPLICATION}.tar

FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION source-clickhouse-strict-encrypt

COPY --from=build /airbyte /airbyte

LABEL io.airbyte.version=0.1.15
LABEL io.airbyte.name=airbyte/source-clickhouse-strict-encrypt
