FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION source-stock-ticker-api
ENV TZ UTC

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1

LABEL io.airbyte.version=dev
LABEL io.airbyte.name=airbyte/source-stock-ticker-api

