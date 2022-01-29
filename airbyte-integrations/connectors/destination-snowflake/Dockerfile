FROM airbyte/integration-base-java:dev

# uncomment to run Yourkit java profiling
#RUN apt-get update && apt-get install -y curl zip
#
#RUN curl -o /tmp/YourKit-JavaProfiler-2021.3-docker.zip https://www.yourkit.com/download/docker/YourKit-JavaProfiler-2021.3-docker.zip && \
#  unzip /tmp/YourKit-JavaProfiler-2021.3-docker.zip -d /usr/local && \
#  rm /tmp/YourKit-JavaProfiler-2021.3-docker.zip

WORKDIR /airbyte

ENV APPLICATION destination-snowflake

# Needed for JDK17 (in turn, needed on M1 macs) - see https://github.com/snowflakedb/snowflake-jdbc/issues/589#issuecomment-983944767
ENV DESTINATION_SNOWFLAKE_OPTS "--add-opens java.base/java.nio=ALL-UNNAMED"

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1

ENV SENTRY_DSN="https://981e729cf92840628b29121e96e958f7@o1009025.ingest.sentry.io/6173659"

LABEL io.airbyte.version=0.4.5

LABEL io.airbyte.name=airbyte/destination-snowflake
