ARG BASE_IMAGE

FROM ${BASE_IMAGE}
ARG CONNECTOR_NAME

# Set permissions for downloaded files
RUN chmod +x /airbyte/base.sh /airbyte/javabase.sh && \
    chown airbyte:airbyte /airbyte/base.sh /airbyte/javabase.sh /airbyte/dd-java-agent.jar

ENV AIRBYTE_ENTRYPOINT="/airbyte/base.sh"
ENV APPLICATION="${CONNECTOR_NAME}"

# Add the connector TAR file and extract it
COPY airbyte-app.tar /tmp/${CONNECTOR_NAME}.tar
RUN tar xf /tmp/${CONNECTOR_NAME}.tar --strip-components=1 -C /airbyte && \
    rm -rf /tmp/${CONNECTOR_NAME}.tar && \
    chown -R airbyte:airbyte /airbyte

# Install S3-specific dependencies as root.
USER root
RUN yum install -y lzop lzo lzo-devel && yum clean all

# Critically important to switch back to Airbyte later.
USER airbyte

# Set entrypoint
ENTRYPOINT ["/airbyte/base.sh"]
