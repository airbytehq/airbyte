FROM airbyte/base-java:dev

WORKDIR /airbyte
ENV APPLICATION csv-destination

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1
