#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Usage: $0 <output_directory>"
    echo "Example: $0 build/releases/1.0.0"
    exit 1
fi

OUTPUT_DIR="$1"
METADATA_FILE="$OUTPUT_DIR/metadata.yaml"

if [ ! -f "$METADATA_FILE" ]; then
    echo "Error: metadata.yaml not found in $OUTPUT_DIR"
    exit 1
fi

CONNECTOR_TYPE=$(yq eval '.data.connectorType' "$METADATA_FILE")
DOCKER_REPOSITORY=$(yq eval '.data.dockerRepository' "$METADATA_FILE")
DOCKER_IMAGE_TAG=$(yq eval '.data.dockerImageTag' "$METADATA_FILE")
DEFINITION_ID=$(yq eval '.data.definitionId' "$METADATA_FILE")
NAME=$(yq eval '.data.name' "$METADATA_FILE")
CONNECTOR_SUBTYPE=$(yq eval '.data.connectorSubtype // "api"' "$METADATA_FILE")
RELEASE_STAGE=$(yq eval '.data.releaseStage // "alpha"' "$METADATA_FILE")
RELEASE_DATE=$(yq eval '.data.releases[0].date // ""' "$METADATA_FILE")
NORMALIZATION_REPOSITORY=$(yq eval '.data.normalizationConfig.normalizationRepository // ""' "$METADATA_FILE")
NORMALIZATION_TAG=$(yq eval '.data.normalizationConfig.normalizationTag // ""' "$METADATA_FILE")
SUPPORTS_DBT=$(yq eval '.data.supportsDbt // false' "$METADATA_FILE")
SUPPORTS_NORMALIZATION=$(yq eval '.data.supportsNormalization // false' "$METADATA_FILE")
DOCUMENTATION_URL=$(yq eval '.data.documentationUrl // ""' "$METADATA_FILE")
ICON_URL=$(yq eval '.data.iconUrl // ""' "$METADATA_FILE")

SPEC_JSON='{
  "documentationUrl": "'$DOCUMENTATION_URL'",
  "connectionSpecification": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "'$NAME' Spec",
    "type": "object",
    "properties": {}
  }
}'

create_registry_entry() {
    local registry_type="$1"
    
    local override_key=""
    if [ "$registry_type" = "cloud" ]; then
        override_key=".data.registryOverrides.cloud"
    else
        override_key=".data.registryOverrides.oss"
    fi
    
    local has_overrides=$(yq eval "has($override_key)" "$METADATA_FILE")
    
    if [ "$CONNECTOR_TYPE" = "source" ]; then
        cat << EOF
{
  "sourceDefinitionId": "$DEFINITION_ID",
  "name": "$NAME",
  "dockerRepository": "$DOCKER_REPOSITORY",
  "dockerImageTag": "$DOCKER_IMAGE_TAG",
  "documentationUrl": "$DOCUMENTATION_URL",
  "icon": "$ICON_URL",
  "sourceType": "$CONNECTOR_SUBTYPE",
  "spec": $SPEC_JSON,
  "tombstone": false,
  "public": true,
  "custom": false,
  "releaseStage": "$RELEASE_STAGE",
  "releaseDate": "$RELEASE_DATE",
  "resourceRequirements": null,
  "protocolVersion": "0.2.0",
  "allowedHosts": {
    "hosts": []
  },
  "maxSecondsBetweenMessages": 86400,
  "suggestedStreams": {
    "streams": []
  }
}
EOF
    else
        local normalization_config=""
        if [ "$SUPPORTS_NORMALIZATION" = "true" ] && [ -n "$NORMALIZATION_REPOSITORY" ]; then
            normalization_config='"normalizationConfig": {
    "normalizationRepository": "'$NORMALIZATION_REPOSITORY'",
    "normalizationTag": "'$NORMALIZATION_TAG'",
    "normalizationIntegrationType": "dbt"
  },'
        fi
        
        cat << EOF
{
  "destinationDefinitionId": "$DEFINITION_ID",
  "name": "$NAME",
  "dockerRepository": "$DOCKER_REPOSITORY",
  "dockerImageTag": "$DOCKER_IMAGE_TAG",
  "documentationUrl": "$DOCUMENTATION_URL",
  "icon": "$ICON_URL",
  "spec": $SPEC_JSON,
  "tombstone": false,
  "public": true,
  "custom": false,
  "releaseStage": "$RELEASE_STAGE",
  "releaseDate": "$RELEASE_DATE",
  "resourceRequirements": null,
  "protocolVersion": "0.2.0",
  $normalization_config
  "supportsDbt": $SUPPORTS_DBT,
  "supportsNormalization": $SUPPORTS_NORMALIZATION
}
EOF
    fi
}

echo "Generating oss.json..."
create_registry_entry "oss" > "$OUTPUT_DIR/oss.json"

echo "Generating cloud.json..."
create_registry_entry "cloud" > "$OUTPUT_DIR/cloud.json"

if [ -f "$OUTPUT_DIR/components.py" ]; then
    echo "Creating components.zip for manifest-only connector..."
    cd "$OUTPUT_DIR"
    zip -q components.zip components.py
    sha256sum components.zip | cut -d' ' -f1 > components.zip.sha256
    cd - > /dev/null
fi

echo "Registry artifacts generated successfully in $OUTPUT_DIR"
echo "Files created:"
ls -la "$OUTPUT_DIR"
