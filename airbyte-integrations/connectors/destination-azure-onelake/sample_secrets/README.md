# Sample configuration files

Use **one** of these auth methods per destination.

| File | Auth method |
|------|-------------|
| `config.json` | **Service Principal** — set `azure_tenant_id`, `azure_client_id`, `azure_client_secret`. Leave `use_managed_identity` false or omit it. |
| `config_managed_identity.json` | **Managed Identity** — set `use_managed_identity: true`. Leave tenant/client/secret empty. Optionally set `managed_identity_client_id` for a user-assigned identity. |

Copy the file you need to `config.json` in a `secrets` folder for local runs, or paste the contents into the Airbyte UI when configuring the destination.

## Local testing with Managed Identity config

When running the connector locally (e.g. via Gradle), Azure CLI credential often isn’t available to the JVM. Use **environment variables** so DefaultAzureCredential uses EnvironmentCredential:

1. **One-off:** set the same Service Principal values in your shell, then run the check:
   ```bash
   export AZURE_TENANT_ID="your-tenant-id"
   export AZURE_CLIENT_ID="your-client-id"
   export AZURE_CLIENT_SECRET="your-client-secret"
   ./scripts/run_check_managed_identity_local.sh
   ```
2. **Or** copy `.env.managed_identity.example` to `.env.managed_identity`, fill in the three values, then run:
   ```bash
   ./scripts/run_check_managed_identity_local.sh
   ```
   (`.env.managed_identity` is gitignored.)
