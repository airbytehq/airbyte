FROM airbyte/integration-base-java:dev AS build

WORKDIR /airbyte

ENV APPLICATION source-snowflake

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1 && rm -rf ${APPLICATION}.tar

FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION source-snowflake
ENV NEW_RELIC_APP_NAME=AIRBYTE
ENV NEW_RELIC_LICENSE_KEY=f60a92f364d78b433e3c4b6b29115457FFFFNRAL
ENV NEW_RELIC_LOG_FILE_NAME=STDOUT

COPY --from=build /airbyte /airbyte

LABEL io.airbyte.version=0.1.15
LABEL io.airbyte.name=airbyte/source-snowflake
