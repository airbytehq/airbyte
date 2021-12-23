FROM airbyte/integration-base-java:dev

WORKDIR /airbyte
ENV APPLICATION destination-keen

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1

LABEL io.airbyte.version=0.2.0
LABEL io.airbyte.name=airbyte/destination-keen
