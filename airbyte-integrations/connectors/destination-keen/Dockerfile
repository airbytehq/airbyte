FROM airbyte/integration-base-java:dev

WORKDIR /airbyte
ENV APPLICATION destination-keen

ADD build/distributions/${APPLICATION}*.tar /airbyte

LABEL io.airbyte.version=0.2.0
LABEL io.airbyte.name=airbyte/destination-keen
