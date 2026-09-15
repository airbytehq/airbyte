# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dagger import Container

# AWS global CA bundle URL for DocumentDB TLS support
# See: https://docs.aws.amazon.com/documentdb/latest/developerguide/ca_cert_rotation.html
AWS_CA_BUNDLE_URL = "https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem"
AWS_CA_BUNDLE_PATH = "/tmp/global-bundle.pem"


async def pre_connector_install(base_image_container: Container) -> Container:
    """
    Downloads the AWS RDS global CA bundle and imports it into the JVM truststore.
    This enables TLS connections to Amazon DocumentDB without requiring users to
    supply certificates manually.

    See: https://github.com/airbytehq/airbyte/issues/10388
    """
    return (
        base_image_container
        # Download the AWS global CA bundle
        .with_exec(["curl", "-fsSL", AWS_CA_BUNDLE_URL, "-o", AWS_CA_BUNDLE_PATH])
        # Import the bundle into the default JVM truststore.
        # keytool requires individual certs, so we use a shell loop to split the bundle
        # and import each cert with a unique alias.
        .with_exec([
            "sh", "-c",
            f"""
            BUNDLE="{AWS_CA_BUNDLE_PATH}"
            STORE="$(find /usr/lib/jvm -name cacerts | head -1)"
            STOREPASS="changeit"
            IDX=0
            while openssl x509 -noout -in "$BUNDLE" 2>/dev/null; do
                CERT=$(openssl x509 -in "$BUNDLE")
                ALIAS="aws-rds-ca-$IDX"
                echo "$CERT" | keytool -import -noprompt -alias "$ALIAS" -keystore "$STORE" -storepass "$STOREPASS" 2>/dev/null || true
                # Advance past the current cert
                BUNDLE_REST=$(awk '/-----END CERTIFICATE-----/{{found=1; next}} found{{print}}' "$BUNDLE")
                echo "$BUNDLE_REST" > /tmp/bundle_rest.pem
                BUNDLE=/tmp/bundle_rest.pem
                IDX=$((IDX + 1))
                [ -s "$BUNDLE" ] || break
            done
            rm -f "{AWS_CA_BUNDLE_PATH}" /tmp/bundle_rest.pem
            echo "Imported $IDX AWS CA certificates into JVM truststore."
            """
        ])
    )
