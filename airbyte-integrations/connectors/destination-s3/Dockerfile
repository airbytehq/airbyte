FROM airbyte/integration-base-java:dev AS build

WORKDIR /airbyte

ENV APPLICATION destination-s3

COPY bin/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1 && rm -rf ${APPLICATION}.tar

FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION destination-s3

COPY --from=build /airbyte /airbyte

LABEL io.airbyte.version=0.3.9
LABEL io.airbyte.name=airbyte/destination-s3
