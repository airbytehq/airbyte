FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION destination-bigquery-denormalized

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1

LABEL io.airbyte.version=0.1.4
LABEL io.airbyte.name=airbyte/destination-bigquery-denormalized
