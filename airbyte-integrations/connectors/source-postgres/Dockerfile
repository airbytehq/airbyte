FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION source-postgres

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1

LABEL io.airbyte.version=0.3.9
LABEL io.airbyte.name=airbyte/source-postgres
