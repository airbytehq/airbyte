FROM airbyte/integration-base-java:dev AS build

WORKDIR /airbyte

ENV APPLICATION destination-cassandra

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1 && rm -rf ${APPLICATION}.tar

ARG BUILD_ID
LABEL io.airbyte.build=$BUILD_ID

FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION destination-cassandra

COPY --from=build /airbyte /airbyte

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/destination-cassandra
