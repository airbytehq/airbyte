FROM airbyte/integration-base-java:dev

WORKDIR /airbyte
ENV APPLICATION destination-mariadb-columnstore

ADD build/distributions/${APPLICATION}*.tar /airbyte

LABEL io.airbyte.version=0.1.1
LABEL io.airbyte.name=airbyte/destination-mariadb-columnstore
