FROM airbyte/integration-base-java:dev AS build

WORKDIR /airbyte

ENV APPLICATION destination-bigquery

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1 && rm -rf ${APPLICATION}.tar

FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION destination-bigquery
ENV ENABLE_SENTRY true
ENV JAVA_TOOL_OPTIONS -agentlib:jdwp=transport=dt_socket,server=y,suspend=y,address=*:5005
COPY --from=build /airbyte /airbyte

LABEL io.airbyte.version=1.1.0
LABEL io.airbyte.name=airbyte/destination-bigquery
