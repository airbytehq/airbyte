FROM airbyte/integration-base-java:dev AS build

WORKDIR /airbyte

ENV APPLICATION destination-bigquery-denormalized

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1 && rm -rf ${APPLICATION}.tar

FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION destination-bigquery-denormalized
ENV SENTRY_DSN="https://981e729cf92840628b29121e96e958f7@o1009025.ingest.sentry.io/6173659"

COPY --from=build /airbyte /airbyte

LABEL io.airbyte.version=0.2.5
LABEL io.airbyte.name=airbyte/destination-bigquery-denormalized
