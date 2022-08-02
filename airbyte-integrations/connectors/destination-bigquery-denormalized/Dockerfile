FROM airbyte/integration-base-java:dev AS build

WORKDIR /airbyte

ENV APPLICATION destination-bigquery-denormalized

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1 && rm -rf ${APPLICATION}.tar

FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION destination-bigquery-denormalized
ENV ENABLE_SENTRY true

COPY --from=build /airbyte /airbyte

LABEL io.airbyte.version=1.1.12
LABEL io.airbyte.name=airbyte/destination-bigquery-denormalized
