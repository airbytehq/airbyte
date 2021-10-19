FROM adoptopenjdk/openjdk14

ENV WORK_DIR=/airbyte

COPY . ${WORK_DIR}/

WORKDIR $WORK_DIR

# RUN ./gradlew :airbyte-integrations:connectors:destination-cassandra:build
#
# RUN ./gradlew :airbyte-integrations:connectors:destination-cassandra:integrationTest

