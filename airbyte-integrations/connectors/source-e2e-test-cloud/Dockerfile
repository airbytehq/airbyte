FROM airbyte/integration-base-java:dev AS build

WORKDIR /airbyte

ENV APPLICATION source-e2e-test-cloud

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1 && rm -rf ${APPLICATION}.tar

FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION source-e2e-test-cloud
ENV APPLICATION_VERSION 2.0.0
ENV ENABLE_SENTRY true

COPY --from=build /airbyte /airbyte

LABEL io.airbyte.version=2.0.0
LABEL io.airbyte.name=airbyte/source-e2e-test-cloud
