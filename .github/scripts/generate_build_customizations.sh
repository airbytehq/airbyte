#!/bin/bash
# Create a build_customization.py file for a given connector. 
# With that file, the image for the connector will have proxy settings defined.

# Usage: ./generate_build_customizations.sh <connector-name>

CONNECTOR=$1
CUSTOMIZATION_FILE="airbyte-integrations/connectors/$CONNECTOR/build_customization.py"

echo "🚀 Setting up proxy configuration for $CONNECTOR..."

cat > "$CUSTOMIZATION_FILE" <<EOF
from __future__ import annotations
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dagger import Container

async def post_connector_install(base_image_container):
    HTTP_PROXY = os.environ["IMAGE_HTTP_PROXY"]
    HTTPS_PROXY = os.environ["IMAGE_HTTPS_PROXY"]
    return await base_image_container.with_env_variable("HTTP_PROXY", HTTP_PROXY).with_env_variable("HTTPS_PROXY", HTTPS_PROXY)
EOF

echo "✅ build_customization.py created at $CUSTOMIZATION_FILE"
