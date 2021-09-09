FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION destination-snowflake

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1

LABEL io.airbyte.version=0.3.13
LABEL io.airbyte.name=airbyte/destination-snowflake
