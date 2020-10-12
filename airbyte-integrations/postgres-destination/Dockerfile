FROM airbyte/base-java:dev

WORKDIR /airbyte

# fixme - replace java-template with the name of directory that this file is in.
ENV APPLICATION postgres-destination

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1
