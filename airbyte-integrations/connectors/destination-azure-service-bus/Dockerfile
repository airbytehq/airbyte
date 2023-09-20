FROM airbyte/integration-base-java:dev AS build

WORKDIR /airbyte
ENV APPLICATION destination-azure-service-bus

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1 && rm -rf ${APPLICATION}.tar

FROM airbyte/integration-base-java:dev

WORKDIR /airbyte
ENV APPLICATION destination-azure-service-bus

COPY --from=build /airbyte /airbyte

# 0.8.0 tested against airbyte v0.50.30
LABEL io.airbyte.version=0.8.0
LABEL io.airbyte.name=airbyte/destination-azure-service-bus
