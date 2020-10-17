FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

# fixme - replace java-template with the name of directory that this file is in.
ENV APPLICATION java-template-destination

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/airbyte-java-template-destination
