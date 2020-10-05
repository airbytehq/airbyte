FROM airbyte/base-java:dev
COPY --from=openjdk:14.0.2-slim / /

WORKDIR /airbyte
# todo (cgardens) - naming.
ENV INTEGRATION_NAME csv

COPY build/libs/${INTEGRATION_NAME}*.jar lib/${INTEGRATION_NAME}.jar

ENV DESTINATION_CLASS io.airbyte.integrations.csv.CsvDestination
ENV DESTINATION_JAR_PATH lib/${INTEGRATION_NAME}.jar
