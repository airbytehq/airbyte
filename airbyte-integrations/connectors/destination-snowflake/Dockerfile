FROM airbyte/integration-base-java:dev

# uncomment to run Yourkit java profiling
#RUN apt-get update && apt-get install -y curl zip
#
#RUN curl -o /tmp/YourKit-JavaProfiler-2021.3-docker.zip https://www.yourkit.com/download/docker/YourKit-JavaProfiler-2021.3-docker.zip && \
#  unzip /tmp/YourKit-JavaProfiler-2021.3-docker.zip -d /usr/local && \
#  rm /tmp/YourKit-JavaProfiler-2021.3-docker.zip

WORKDIR /airbyte

ENV APPLICATION destination-snowflake

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1

LABEL io.airbyte.version=0.3.17
LABEL io.airbyte.name=airbyte/destination-snowflake
