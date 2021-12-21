FROM airbyte/integration-base-java:dev

WORKDIR /airbyte
ENV APPLICATION destination-csv

ADD build/distributions/${APPLICATION}*.tar /airbyte

LABEL io.airbyte.version=0.2.8
LABEL io.airbyte.name=airbyte/destination-csv
