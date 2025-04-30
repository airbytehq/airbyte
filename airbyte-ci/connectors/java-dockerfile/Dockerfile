# Multi-stage Dockerfile for building Airbyte Java connectors
# This Dockerfile replicates the dagger-based build process using a multi-stage approach

# Build stage
FROM amazoncorretto:21-al2023 as builder

# Install required packages for the build
RUN yum update -y && \
    yum install -y tar gzip findutils shadow-utils && \
    yum clean all && \
    rm -rf /var/cache/yum

# Set up the build environment
WORKDIR /airbyte

# Copy the entire repository (except what's in .dockerignore)
# This is necessary because Gradle needs access to various parts of the repository
COPY . .

# Make gradlew executable
RUN chmod +x ./gradlew

# Build arguments
ARG CONNECTOR_PATH=airbyte-integrations/connectors/source-mysql

# Build the connector
RUN ./gradlew :airbyte-integrations:connectors:${CONNECTOR_NAME}:distTar

# Runtime stage
FROM amazoncorretto:21-al2023

# Install required packages for runtime
RUN set -o xtrace && \
    yum install -y shadow-utils tar openssl findutils && \
    yum update -y --security && \
    yum clean all && \
    rm -rf /var/cache/yum && \
    # Create airbyte user and group
    groupadd --gid 1000 airbyte && \
    useradd --uid 1000 --gid airbyte --shell /bin/bash --create-home airbyte && \
    # Create required directories
    mkdir -p /secrets /config /airbyte /custom_cache && \
    # Set permissions
    chown -R airbyte:airbyte /airbyte && \
    chown -R airbyte:airbyte /custom_cache && \
    chown -R airbyte:airbyte /secrets && \
    chown -R airbyte:airbyte /config && \
    chown -R airbyte:airbyte /usr/share/pki/ca-trust-source && \
    chown -R airbyte:airbyte /etc/pki/ca-trust && \
    chown -R airbyte:airbyte /tmp

# Download required scripts
WORKDIR /airbyte
ADD https://raw.githubusercontent.com/airbytehq/airbyte/master/airbyte-integrations/bases/base/base.sh /airbyte/base.sh
ADD https://raw.githubusercontent.com/airbytehq/airbyte/master/airbyte-integrations/bases/base-java/javabase.sh /airbyte/javabase.sh
ADD https://dtdg.co/latest-java-tracer /airbyte/dd-java-agent.jar

# Set permissions for downloaded files
RUN chmod +x /airbyte/base.sh /airbyte/javabase.sh && \
    chown airbyte:airbyte /airbyte/base.sh /airbyte/javabase.sh /airbyte/dd-java-agent.jar

# Build arguments for the runtime stage
ARG CONNECTOR_PATH=airbyte-integrations/connectors/source-mysql
ARG CONNECTOR_NAME=source-mysql

# Set environment variables
ENV AIRBYTE_SPEC_CMD="/airbyte/javabase.sh --spec"
ENV AIRBYTE_CHECK_CMD="/airbyte/javabase.sh --check"
ENV AIRBYTE_DISCOVER_CMD="/airbyte/javabase.sh --discover"
ENV AIRBYTE_READ_CMD="/airbyte/javabase.sh --read"
ENV AIRBYTE_WRITE_CMD="/airbyte/javabase.sh --write"
ENV AIRBYTE_ENTRYPOINT=/airbyte/base.sh
ENV APPLICATION=${CONNECTOR_NAME}

# Copy the built connector tar from the builder stage
COPY --from=builder /airbyte/${CONNECTOR_PATH}/build/distributions/*.tar /tmp/connector.tar

# Extract the connector
RUN tar xf /tmp/connector.tar --strip-components=1 -C /airbyte && \
    rm -rf /tmp/connector.tar && \
    chown -R airbyte:airbyte /airbyte

# Set the non-root user
USER airbyte

# Set entrypoint
ENTRYPOINT ["/airbyte/base.sh"]

# Add labels
LABEL io.airbyte.version="0.1.0"
LABEL io.airbyte.name="airbyte/${CONNECTOR_NAME}"
