FROM airbyte/integration-base-java:dev AS build

WORKDIR /airbyte

ENV APPLICATION source-postgres

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1 && rm -rf ${APPLICATION}.tar

FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

# Add the Datadog Java APM agent
ADD https://dtdg.co/latest-java-tracer dd-java-agent.jar

ENV APPLICATION source-postgres

ENV DD_SERVICE: "source-postgres"
ENV DD_VERSION: 1.0.36-dd
ENV DD_CONNECTOR_ENABLE_ENV_VAR: true

COPY --from=build /airbyte /airbyte

LABEL io.airbyte.version=1.0.36-dd
LABEL io.airbyte.name=airbyte/source-postgres
