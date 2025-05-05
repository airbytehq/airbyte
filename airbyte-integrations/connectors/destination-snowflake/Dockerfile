# syntax=docker/dockerfile:1
# check=skip=InvalidDefaultArgInFrom

# Java connector Dockerfile for Airbyte

# Build arguments
ARG BASE_IMAGE=docker.io/airbyte/java-connector-base:2.0.1@sha256:ec89bd1a89e825514dd2fc8730ba299a3ae1544580a078df0e35c5202c2085b3

# Base image - using Amazon Corretto (Amazon's distribution of OpenJDK)
FROM ${BASE_IMAGE}
ARG CONNECTOR_NAME=destination-snowflake

# Set permissions for downloaded files
RUN chmod +x /airbyte/base.sh /airbyte/javabase.sh && \
    chown airbyte:airbyte /airbyte/base.sh /airbyte/javabase.sh /airbyte/dd-java-agent.jar

ENV AIRBYTE_ENTRYPOINT="/airbyte/base.sh"
ENV APPLICATION="${CONNECTOR_NAME}"

# Add the connector TAR file and extract it
#COPY ./build/distributions/${CONNECTOR_NAME}.tar /tmp/${CONNECTOR_NAME}.tar
COPY airbyte-app.tar /tmp/${CONNECTOR_NAME}.tar
RUN tar xf /tmp/${CONNECTOR_NAME}.tar --strip-components=1 -C /airbyte && \
    rm -rf /tmp/${CONNECTOR_NAME}.tar && \
    chown -R airbyte:airbyte /airbyte

# Set the non-root user
USER airbyte

# Set entrypoint
ENTRYPOINT ["/airbyte/base.sh"]
