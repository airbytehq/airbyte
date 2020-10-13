FROM airbyte/base-java:dev

WORKDIR /airbyte

ENV APPLICATION bigquery-destination

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1
