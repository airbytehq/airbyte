#!/usr/bin/env bash

set -e

YAML_DIR=metadata_service/models/src
OUTPUT_DIR=metadata_service/models/generated
BUNDLE_OUTPUT="$OUTPUT_DIR/ConnectorMetadataDefinitionV0.json"

if ! command -v node &> /dev/null; then
  echo "❌ Error: node is not installed or not in PATH"
  echo ""
  echo "To install Node.js:"
  echo "  - On macOS: brew install node"
  echo "  - On Ubuntu/Debian: sudo apt-get install nodejs npm"
  echo "  - On other systems: https://nodejs.org/"
  echo ""
  echo "After installation, verify with: node --version"
  exit 1
fi

if ! command -v npm &> /dev/null; then
  echo "❌ Error: npm is not installed or not in PATH"
  echo ""
  echo "npm is typically installed with Node.js"
  echo "After installation, verify with: npm --version"
  exit 1
fi

# Ensure the yaml directory exists
if [ ! -d "$YAML_DIR" ]; then
  echo "❌ Error: The yaml directory does not exist: $YAML_DIR"
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

if [ ! -d "node_modules" ]; then
  echo "📦 Installing Node.js dependencies..."
  if [ -f "package-lock.json" ]; then
    npm ci --silent
  else
    npm install --silent
  fi
fi

echo "📦 Bundling JSON schemas using @apidevtools/json-schema-ref-parser..."
echo "   Entry schema: $YAML_DIR/ConnectorMetadataDefinitionV0.yaml"
echo "   Output: $BUNDLE_OUTPUT"

node bin/bundle-schemas.js

if [ $? -eq 0 ]; then
  echo "✅ Successfully bundled schema to $BUNDLE_OUTPUT"
  echo "   This bundled schema can be used for IDE validation and other tools."
else
  echo "❌ Error: Failed to bundle schemas"
  exit 1
fi
