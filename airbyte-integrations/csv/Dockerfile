FROM airbyte/base-java:dev

WORKDIR /airbyte
# todo (cgardens) - naming.
ENV INTEGRATION_NAME csv

COPY build/libs/${INTEGRATION_NAME}*.jar lib/${INTEGRATION_NAME}.jar

ENV DESTINATION_CLASS CsvDestination
ENV DESTINATION_JAR_PATH lib/${INTEGRATION_NAME}.jar
