#!/bin/bash

# Exit on error
set -e

# Function to check if Vault CLI is available and logged in
check_vault() {
  if ! command -v vault &> /dev/null; then
    echo "Error: Vault CLI is not installed or not in PATH."
    exit 1
  fi
  # Check if authenticated (simple check; assumes VAULT_TOKEN is set)
  if ! vault token lookup &> /dev/null; then
    echo "Error: You must be logged in to Vault (e.g., vault login root)."
    exit 1
  fi
}

# Enable AppRole auth method if not already enabled
enable_approle() {
  if ! vault auth list | grep -q 'approle/'; then
    echo "Enabling AppRole auth method..."
    vault auth enable approle
  else
    echo "AppRole auth method already enabled."
  fi
}

# Create the read-only policy
create_policy() {
  echo "Creating/Updating fabrix-read policy..."

  # Define the policy content (HCL format) - MINIMAL VERSION for required streams
  POLICY_CONTENT='
path "auth/approle/login" {
  capabilities = ["create", "update"]
}
# Token operations needed for authentication
path "auth/token/lookup-self" {
  capabilities = ["read"]
}
path "+/auth/token/lookup-self" {
  capabilities = ["read"]
}

# Read seal status (primary endpoint for vault_info)
path "sys/seal-status" {
  capabilities = ["read"]
}
path "+/sys/seal-status" {
  capabilities = ["read"]
}

# Read leader status (secondary endpoint for vault_info)
path "sys/leader" {
  capabilities = ["read"]
}
path "+/sys/leader" {
  capabilities = ["read"]
}

# Add root paths for namespaces
# Root namespace
path "sys/namespaces" {
  capabilities = ["list", "read"]
}
path "sys/namespaces/*" {
  capabilities = ["read"]
}

path "sys/auth" {
  capabilities = ["read", "list"]
}

path "sys/mounts" {
  capabilities = ["read", "list"]
}
path "*/sys/mounts" {
  capabilities = ["read", "list"]
}

# Add root paths for users
# Root namespace
path "identity/entity/id" {
  capabilities = ["list", "read"]
}
path "identity/entity/id/*" {
  capabilities = ["read"]
}
path "+/identity/entity/id/*" {
  capabilities = ["read"]
}
path "identity/entity" {
  capabilities = ["list", "read"]
}
path "identity/entity/*" {
  capabilities = ["read"]
}
path "identity/entity/name" {
  capabilities = ["list"]
}
path "identity/entity/name/*" {
  capabilities = ["read"]
}
path "identity/lookup/entity" {
  capabilities = ["create", "update"]
}
path "auth/*/users" {
  capabilities = ["list"]
}
path "auth/*/users/*" {
  capabilities = ["read"]
}
path "auth/*/user" {
  capabilities = ["list"]
}
path "auth/*/user/*" {
  capabilities = ["read"]
}

# Identity entity alias permissions
path "identity/entity-alias" {
  capabilities = ["list", "read"]
}
path "identity/entity-alias/*" {
  capabilities = ["read"]
}
path "identity/entity-alias/id" {
  capabilities = ["list", "read"]
}
path "identity/entity-alias/id/*" {
  capabilities = ["read"]
}
path "*/identity/entity-alias" {
  capabilities = ["list", "read"]
}
path "*/identity/entity-alias/*" {
  capabilities = ["read"]
}
path "*/identity/entity-alias/id" {
  capabilities = ["list", "read"]
}
path "*/identity/entity-alias/id/*" {
  capabilities = ["read"]
}

# Read identity groups with recursive wildcards
path "identity/group/id" {
  capabilities = ["list"]
}
path "identity/group/id/*" {
  capabilities = ["read"]
}
path "+/identity/group/id" {
  capabilities = ["list"]
}
path "+/identity/group/id/*" {
  capabilities = ["read"]
}

path "*" {
  capabilities = ["read", "list"]
}

# Read OIDC providers with recursive wildcards
path "*/identity/oidc/provider" {
  capabilities = ["list"]
}
path "*/identity/oidc/provider/*" {
  capabilities = ["read"]
}

# Add root paths for policies
# Root namespace
path "sys/policies/acl" {
  capabilities = ["list"]
}
path "sys/policies/acl/*" {
  capabilities = ["read"]
}
'

  # Write the policy to Vault
  echo "$POLICY_CONTENT" | vault policy write fabrix-read -
}

# Create the AppRole role
create_role() {
  echo "Creating fabrix-read AppRole role..."
  vault write auth/approle/role/fabrix-read \
    token_policies="fabrix-read" \
    token_ttl=12h \
    token_max_ttl=24h \
    secret_id_ttl=0
}

# Generate and output credentials
generate_credentials() {
  echo "Generating Role ID and Secret ID..."

  ROLE_ID=$(vault read -field=role_id auth/approle/role/fabrix-read/role-id)
  SECRET_ID=$(vault write -f -field=secret_id auth/approle/role/fabrix-read/secret-id)

  echo "Setup complete!"
  echo "------------------------"
  echo "Vault Address: $VAULT_ADDR"
  echo "AppRole Mount Path: auth/approle"
  echo "Role Name: fabrix-read"
  echo "Role ID: $ROLE_ID (non-sensitive)"
  echo "Secret ID: $SECRET_ID (sensitive)"
  echo "------------------------"
  echo "Use these to test authentication."
  echo "To regenerate a new Secret ID: vault write -f auth/approle/role/fabrix-read/secret-id"
}

# Main execution
check_vault
enable_approle
create_policy
create_role
generate_credentials
