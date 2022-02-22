FROM airbyte/integration-base-java:dev AS build

WORKDIR /airbyte

ENV APPLICATION source-mongodb-v2

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1 && rm -rf ${APPLICATION}.tar

FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

RUN apt-get update &&\
    apt-get install -y --no-install-recommends 	curl	&&\
    rm -rf /var/lib/apt/lists/*

COPY build/resources/main/import-rds-cert.sh import-rds-cert.sh

RUN chmod +x import-rds-cert.sh

RUN ./import-rds-cert.sh

RUN rm -rf import-rds-cert.sh

ENV APPLICATION source-mongodb-v2

COPY --from=build /airbyte /airbyte

LABEL io.airbyte.version=0.1.13
LABEL io.airbyte.name=airbyte/source-mongodb-v2
