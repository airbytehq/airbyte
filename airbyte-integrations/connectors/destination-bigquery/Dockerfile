FROM airbyte/integration-base-java:dev AS build

WORKDIR /airbyte

ENV APPLICATION destination-bigquery

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1 && rm -rf ${APPLICATION}.tar

FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION destination-bigquery
ENV SENTRY_DSN "https://2a3a1622a2104b8f8d36db4915c956f8@o1114644.ingest.sentry.io/6145965"

COPY --from=build /airbyte /airbyte

LABEL io.airbyte.version=0.6.2
LABEL io.airbyte.name=airbyte/destination-bigquery
