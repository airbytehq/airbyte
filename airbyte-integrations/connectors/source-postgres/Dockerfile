FROM airbyte/integration-base-java:dev AS build

WORKDIR /airbyte

ENV APPLICATION source-postgres

// optionally install procps to enable the ps command in the connector container
RUN apt-get update && apt-get install -y procps && rm -rf /var/lib/apt/lists/*

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

// expose the same JMX port specified in the previous step
EXPOSE 6000

RUN tar xf ${APPLICATION}.tar --strip-components=1 && rm -rf ${APPLICATION}.tar

FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION source-postgres

COPY --from=build /airbyte /airbyte

LABEL io.airbyte.version=1.0.39
LABEL io.airbyte.name=airbyte/source-postgres
