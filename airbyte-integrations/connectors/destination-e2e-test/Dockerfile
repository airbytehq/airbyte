FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION destination-e2e-test

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1

LABEL io.airbyte.version=dev
LABEL io.airbyte.name=airbyte/destination-e2e-test
