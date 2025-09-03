---
products: oss-community, oss-enterprise
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Adding Custom SSL Certificates to Airbyte Images

When deploying Airbyte in enterprise environments, you may need to add custom SSL certificates to trust internal certificate authorities or self-signed certificates. This guide shows you how to build custom Airbyte images with your SSL certificates included.

## Use Cases

Adding custom SSL certificates is necessary when:
- Your organization uses internal Certificate Authorities (CAs)
- Connectors need to communicate with services using self-signed certificates
- You're behind a corporate proxy that performs SSL inspection
- You need to connect to internal databases or APIs with custom certificates

## Prerequisites

Before you begin, ensure you have:
- Docker installed and running
- Access to a custom image registry ([see custom image registries guide](./custom-image-registries.md))
- Your SSL certificates in `.crt` format
- The specific Airbyte version you want to customize

## Step 1: Inspect Default Certificates

First, verify the current certificate configuration in the base Airbyte image:

```bash
# Pull the Airbyte image you want to customize
docker pull airbyte/workload-launcher:1.6.0

# Connect to the container
docker run -it --rm --entrypoint /bin/bash airbyte/workload-launcher:1.6.0

# Check Java home and truststore location
java -XshowSettings:properties -version 2>&1 | grep -E "java.home|trustStore"
# Output: java.home = /usr/lib/jvm/java-21-amazon-corretto

# List existing certificates
keytool -list -keystore /etc/pki/ca-trust/extracted/java/cacerts -storepass changeit | head -20
```

:::info
The default Airbyte images typically contain around 147 trusted certificates. After adding your custom certificates, this number will increase.
:::

## Step 2: Create Custom Dockerfile

Create a directory for your build context and add your certificates:

```bash
mkdir airbyte-custom-certs
cd airbyte-custom-certs

# Copy your certificates to this directory
cp /path/to/your/cert.crt .
cp /path/to/your/root.crt .
```

Create a `Dockerfile` with the following content:

<Tabs>
<TabItem value="linux" label="Linux/Windows" default>

```dockerfile title="Dockerfile"
FROM airbyte/workload-launcher:1.6.1

USER root

# Copy certificates to temporary location
COPY cert.crt root.crt /tmp/

# Import certificates into Java keystore
RUN keytool -importcert -noprompt -storepass changeit \
    -alias custom_cert_1 -file /tmp/cert.crt \
    -keystore /etc/pki/ca-trust/extracted/java/cacerts -trustcacerts && \
    keytool -importcert -noprompt -storepass changeit \
    -alias custom_root_ca -file /tmp/root.crt \
    -keystore /etc/pki/ca-trust/extracted/java/cacerts -trustcacerts && \
    # Clean up certificate files
    rm /tmp/*.crt

# Switch back to non-root user if needed
USER airbyte
```

</TabItem>
<TabItem value="mac" label="Mac Apple Silicon">

```dockerfile title="Dockerfile"
# Specify platform for Apple Silicon Macs
FROM --platform=linux/amd64 airbyte/workload-launcher:1.6.1

USER root

# Copy certificates to temporary location
COPY cert.crt root.crt /tmp/

# Import certificates into Java keystore
RUN keytool -importcert -noprompt -storepass changeit \
    -alias custom_cert_1 -file /tmp/cert.crt \
    -keystore /etc/pki/ca-trust/extracted/java/cacerts -trustcacerts && \
    keytool -importcert -noprompt -storepass changeit \
    -alias custom_root_ca -file /tmp/root.crt \
    -keystore /etc/pki/ca-trust/extracted/java/cacerts -trustcacerts && \
    # Clean up certificate files
    rm /tmp/*.crt

# Switch back to non-root user if needed
USER airbyte
```

</TabItem>
</Tabs>

:::caution
When building on Apple Silicon Macs, always specify `--platform=linux/amd64` to ensure the image is compatible with your production environment.
:::

## Step 3: Build Custom Images

Build your custom image with the certificates included:

```bash
# Verify the base image architecture
docker inspect --format='{{.Os}}/{{.Architecture}}' airbyte/workload-launcher:1.6.0

# Build the custom image
docker build -t your-registry.com/airbyte/workload-launcher:1.6.1-custom .
```

:::tip
Use a consistent naming convention for your custom images, such as appending `-custom` or including your organization name.
:::

## Step 4: Verify Certificate Installation

Confirm that your certificates were properly installed:

```bash
# Run the custom container
docker run -it --rm --entrypoint /bin/bash your-registry.com/airbyte/workload-launcher:1.6.1-custom

# Check certificate count (should be higher than before)
keytool -list -keystore /etc/pki/ca-trust/extracted/java/cacerts -storepass changeit | grep "Your keystore contains"

# Verify your specific certificates are present
keytool -list -keystore /etc/pki/ca-trust/extracted/java/cacerts -storepass changeit | grep -E "custom_cert_1|custom_root_ca"
```

## Step 5: Build All Required Images

You'll need to apply custom certificates to all Airbyte platform images. Create a script to automate this process:

```bash title="build-all-images.sh"
#!/bin/bash

# List of Airbyte images that need certificates
IMAGES=(
  "workload-launcher:1.6.1"
  "server:1.6.1"
  "worker:1.6.1"
  "webapp:1.6.1"
  "connector-builder-server:1.6.1"
)

REGISTRY="your-registry.com"

for IMAGE in "${IMAGES[@]}"; do
  echo "Building airbyte/$IMAGE with custom certificates..."
  
  # Create temporary Dockerfile
  cat > Dockerfile.tmp <<EOF
FROM airbyte/$IMAGE
USER root
COPY *.crt /tmp/
RUN for cert in /tmp/*.crt; do \
      keytool -importcert -noprompt -storepass changeit \
      -alias "\$(basename \$cert .crt)" -file "\$cert" \
      -keystore /etc/pki/ca-trust/extracted/java/cacerts -trustcacerts; \
    done && rm /tmp/*.crt
USER airbyte
EOF

  docker build -f Dockerfile.tmp -t $REGISTRY/airbyte/${IMAGE}-custom .
  docker push $REGISTRY/airbyte/${IMAGE}-custom
  
  rm Dockerfile.tmp
done
```

## Step 6: Push to Registry and Configure Airbyte

Push your custom images to your registry:

```bash
# Push individual image
docker push your-registry.com/airbyte/workload-launcher:1.6.1-custom

# Or push all images
docker images | grep your-registry.com/airbyte | awk '{print $1":"$2}' | xargs -I{} docker push {}
```

Configure Airbyte to use your custom images by updating your `values.yaml`:

```yaml title="values.yaml"
global:
  image:
    registry: your-registry.com
    tag: 1.6.1-custom  # Use your custom tag
```

## Troubleshooting

### Certificate Verification Failures

If connections still fail with certificate errors:

1. **Check certificate chain completeness**: Ensure you've added all intermediate certificates
2. **Verify certificate format**: Use PEM format (.crt or .pem files)
3. **Check certificate validity**: Ensure certificates aren't expired
4. **Review connector logs**: Check if the error is from the Java truststore or system certificates

### Building on Different Architectures

Always verify your build platform matches your target environment:

```bash
# Check current Docker default platform
docker info | grep -i platform

# Build with explicit platform
docker build --platform linux/amd64 -t your-image:tag .
```

### System Certificates vs Java Truststore

Some connectors may use system certificates instead of the Java truststore. To add certificates system-wide:

```dockerfile
# Add to both Java truststore and system certificates
RUN cp /tmp/*.crt /usr/local/share/ca-certificates/ && \
    update-ca-certificates && \
    keytool -importcert -noprompt -storepass changeit \
    -alias custom_cert -file /tmp/cert.crt \
    -keystore $JAVA_HOME/lib/security/cacerts -trustcacerts
```

## Related Documentation

- [Custom Image Registries](./custom-image-registries.md)
- [Secret Management](./secrets.md)
- [Authentication Configuration](./authentication.md)