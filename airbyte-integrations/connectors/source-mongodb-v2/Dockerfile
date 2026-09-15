FROM amazoncorretto:21-al2023

WORKDIR /airbyte

# Install required packages
RUN yum update -y --security && \
    yum install -y --allowerasing tar openssl findutils curl && \
    yum clean all

# Copy base entrypoint scripts
COPY airbyte-integrations/bases/base/base.sh /airbyte/base.sh
COPY airbyte-integrations/bases/base-java/javabase.sh /airbyte/javabase.sh
RUN chmod +x /airbyte/base.sh /airbyte/javabase.sh

# Set Airbyte entrypoint env variables
ENV AIRBYTE_ENTRYPOINT="/airbyte/base.sh"
ENV AIRBYTE_SPEC_CMD="/airbyte/javabase.sh --spec"
ENV AIRBYTE_CHECK_CMD="/airbyte/javabase.sh --check"
ENV AIRBYTE_DISCOVER_CMD="/airbyte/javabase.sh --discover"
ENV AIRBYTE_READ_CMD="/airbyte/javabase.sh --read"
ENV APPLICATION="source-mongodb-v2"

# Copy and extract connector distribution
COPY airbyte-integrations/connectors/source-mongodb-v2/source-mongodb-v2.tar /airbyte/source-mongodb-v2.tar
RUN tar xf source-mongodb-v2.tar --strip-components=1 && rm -f source-mongodb-v2.tar

# Import AWS RDS global CA bundle into JVM truststore for DocumentDB TLS support
# See: https://github.com/airbytehq/airbyte/issues/10388
RUN curl -fsSL https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem -o /tmp/global-bundle.pem && \
    STORE=$(find /usr/lib/jvm -name cacerts | head -1) && \
    STOREPASS="changeit" && \
    IDX=0 && \
    BUNDLE=/tmp/global-bundle.pem && \
    while openssl x509 -noout -in "$BUNDLE" 2>/dev/null; do \
        CERT=$(openssl x509 -in "$BUNDLE" 2>/dev/null); \
        ALIAS="aws-rds-ca-$IDX"; \
        echo "$CERT" | keytool -import -noprompt -alias "$ALIAS" -keystore "$STORE" -storepass "$STOREPASS" 2>/dev/null || true; \
        BUNDLE_REST=$(awk '/-----END CERTIFICATE-----/{found=1; next} found{print}' "$BUNDLE"); \
        echo "$BUNDLE_REST" > /tmp/bundle_rest.pem; \
        BUNDLE=/tmp/bundle_rest.pem; \
        IDX=$((IDX + 1)); \
        [ -s "$BUNDLE" ] || break; \
    done && \
    rm -f /tmp/global-bundle.pem /tmp/bundle_rest.pem && \
    echo "Imported $IDX AWS CA certificates into JVM truststore."

LABEL io.airbyte.version="1.3.4"
LABEL io.airbyte.name="airbyte/source-mongodb-v2"

ENTRYPOINT ["/airbyte/base.sh"]
