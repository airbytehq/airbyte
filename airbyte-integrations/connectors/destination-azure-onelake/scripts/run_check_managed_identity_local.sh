#!/usr/bin/env bash
# Run the OneLake destination check using the Managed Identity config, with credentials
# from environment variables (Option B). Use this when Azure CLI credential is not
# available to the JVM (e.g. when running via Gradle).
#
# Option 1: Set env vars then run this script:
#   export AZURE_TENANT_ID="your-tenant-id"
#   export AZURE_CLIENT_ID="your-client-id"
#   export AZURE_CLIENT_SECRET="your-client-secret"
#   ./scripts/run_check_managed_identity_local.sh
#
# Option 2: Use a secrets file (do not commit it):
#   cp sample_secrets/.env.managed_identity.example sample_secrets/.env.managed_identity
#   # Edit sample_secrets/.env.managed_identity and set the three values
#   ./scripts/run_check_managed_identity_local.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONNECTOR_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG="$CONNECTOR_DIR/sample_secrets/config_managed_identity.json"

if [[ -f "$CONNECTOR_DIR/sample_secrets/.env.managed_identity" ]]; then
  set -a
  source "$CONNECTOR_DIR/sample_secrets/.env.managed_identity"
  set +a
fi

if [[ -z "$AZURE_TENANT_ID" || -z "$AZURE_CLIENT_ID" || -z "$AZURE_CLIENT_SECRET" ]]; then
  echo "Missing required env vars for DefaultAzureCredential (EnvironmentCredential)."
  echo "Set AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, then run this script again."
  echo "Or create sample_secrets/.env.managed_identity with:"
  echo "  export AZURE_TENANT_ID=\"...\""
  echo "  export AZURE_CLIENT_ID=\"...\""
  echo "  export AZURE_CLIENT_SECRET=\"...\""
  exit 1
fi

cd "$CONNECTOR_DIR/../../.."
./gradlew :airbyte-integrations:connectors:destination-azure-onelake:run --no-daemon -q \
  --args="--check --config $CONFIG"
