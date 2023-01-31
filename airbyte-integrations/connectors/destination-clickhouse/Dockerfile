FROM airbyte/integration-base-java:0.1.1 AS build

WORKDIR /airbyte

ENV APPLICATION destination-clickhouse

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1 && rm -rf ${APPLICATION}.tar

FROM airbyte/integration-base-java:0.1.1

WORKDIR /airbyte

ENV APPLICATION destination-clickhouse

COPY --from=build /airbyte /airbyte

LABEL io.airbyte.version=0.2.2
LABEL io.airbyte.name=airbyte/destination-clickhouse
