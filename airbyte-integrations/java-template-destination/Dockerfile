FROM airbyte/base-java:dev

WORKDIR /airbyte

# todo - replace java-template with the name of directory that this file is in.
ENV APPLICATION java-template

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1
