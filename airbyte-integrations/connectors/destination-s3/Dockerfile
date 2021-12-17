FROM airbyte/integration-base-java:dev

WORKDIR /airbyte
ENV APPLICATION destination-s3

ADD build/distributions/${APPLICATION}*.tar /airbyte

LABEL io.airbyte.version=0.2.0
LABEL io.airbyte.name=airbyte/destination-s3
