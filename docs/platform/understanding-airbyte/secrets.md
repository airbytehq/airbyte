# Secrets

Airbyte store secrets in the configured secret persistence layer as Source and Destinations are created.

This page focuses on understanding how Airbyte uses secrets. Please refer to the [Secret Management](../deploying-airbyte/integrations/secrets.md)
for more information on how to configure various secret persistence layers.

## Handling Secrets
Airbyte stores configuration for various internal models as JSON blobs in the database. By declaring `airbyte_secret` = `true`, models mark sensitive fields
when defining their spec. Airbyte uses this property to understand which fields should be treated as secrets.

While this is most often seen in Connector configuration, this hold true for all models, including Platform models such as webhook configuration.

A secret field:
* must not be returned by the api.
* must not be printed in logs.
* **must be obfuscated in the stored json blob and the UI**.

The last point is particularly important as a security best practice - it's possible to deploy Airbyte so users with deployment access do not have
secret access. This increases Airbyte's deployment flexibility.

## Obfuscation

Airbyte obfuscates secrets within a spec by:
1) Generating a deterministic coordinate of the form `<airbyte-workspace>_<workspace-id>_secret_<uuid>_<version>`. e.g. `airbyte_workspace_024eaa40-75ae-4014-941d-b9e938c3a363_secret_5675437d-ea6b-4f9a-9a0c-d76066004841_v1`.
2) Writing the original secret payload to the coordinate.
3) Replacing the secret field within the JSON payload an object with the embedded secret coordinate.
For example, given a spec of:
```
{
   "email": { "type": "string" }
   "api_token": { "type": "string" , "airbyte_secret": true}
}

```
and a corresponding raw json of:
```
{
   "email":"itpartners@noodle.com",
   "api_token": "fake-token"
}
```

Airbyte saves the following JSON blob:
```
{
    "email":"itpartners@noodle.com",
    "api_token":{
        "_secret":"airbyte_workspace_4e7d7911-0307-40fe-9b79-f00c0dfbb082_secret_d66baab6-3c8d-4ae5-91a6-ca8d904c4780_v1"
    }
}
```

Upon any operation, Airbyte reads the obfuscated JSON spec, extracts the secret coordinate and hydrates the correct secret value before passing it to consumers.

## External Secret References

If your organization has a [custom secret storage configured](../enterprise-flex/external-secrets.md) (for example, AWS Secrets Manager, Google Secret Manager, or Azure Key Vault), you can point connector configuration fields at secrets that already exist in your secret manager. Instead of passing the raw secret value, you pass a reference using the `secret_coordinate::` prefix.

This is useful when:

- You manage secrets externally (e.g. via Terraform, CI/CD pipelines, or a secrets team) and want Airbyte connectors to reference them without Airbyte ever seeing the plaintext value.
- You want to rotate secrets in your secret manager without updating Airbyte connector configurations.
- Compliance requirements prevent you from sending secret values through the Airbyte API.

### Prerequisites

Your Airbyte organization or workspace must have a custom secret storage configured. On Airbyte Cloud, contact your Airbyte representative to set this up. For Enterprise Flex, see [External Secret Management](../enterprise-flex/external-secrets.md).

### How It Works

Any field in a connector spec marked `airbyte_secret: true` can accept a value prefixed with `secret_coordinate::`. When Airbyte sees this prefix, it stores an external reference to the secret in your configured secret manager rather than writing the value to Airbyte's own secret persistence.

For example, if you have a secret named `my-pg-password` in your configured secret manager (e.g. Google Secret Manager, AWS Secrets Manager), you can reference it as:

```
secret_coordinate::my-pg-password
```

At runtime, Airbyte resolves the reference by reading the secret value from your configured secret manager.

### Supported APIs

External secret references work with all source and destination create and update endpoints:

- **Create Source** (`POST /v1/sources`)
- **Update Source** (`PUT /v1/sources/{sourceId}`)
- **Create Destination** (`POST /v1/destinations`)
- **Update Destination** (`PUT /v1/destinations/{destinationId}`)

### API Example

```bash
curl --request POST \
  --url https://api.airbyte.com/v1/sources \
  --header 'Authorization: Bearer <YOUR_ACCESS_TOKEN>' \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "My Postgres Source",
    "workspaceId": "<YOUR_WORKSPACE_ID>",
    "definitionId": "<POSTGRES_SOURCE_DEFINITION_ID>",
    "configuration": {
      "host": "db.example.com",
      "port": 5432,
      "database": "mydb",
      "username": "airbyte_user",
      "password": "secret_coordinate::my-pg-password"
    }
  }'
```

In this example, `password` is an `airbyte_secret` field. Instead of providing the actual password, you pass `secret_coordinate::my-pg-password`, and Airbyte resolves it from your configured secret manager.

### Terraform Example

The same approach works with the [Airbyte Terraform Provider](https://registry.terraform.io/providers/airbytehq/airbyte/latest):

```hcl
resource "airbyte_source_postgres" "example" {
  name         = "My Postgres Source"
  workspace_id = var.workspace_id

  configuration = {
    host     = "db.example.com"
    port     = 5432
    database = "mydb"
    username = "airbyte_user"
    password = "secret_coordinate::my-pg-password"
  }
}
```

:::tip
You can also read back the stored secret coordinates (rather than `***` placeholders) by setting `include_secret_coordinates = true` on the `airbyte_source` or `airbyte_destination` data sources.
:::

### Limitations

- The secret name you pass after the `secret_coordinate::` prefix must match the name of a secret that exists (or will exist) in the secret manager configured for your workspace or organization.
- If no custom secret storage is configured for your workspace/organization, the `secret_coordinate::` prefix will not resolve correctly at runtime.

## Operational Details

1. When configuration is updated, Airbyte increments a secret coordinate's version while preserving the prefix.
E.g. `airbyte_workspace_024eaa40-75ae-4014-941d-b9e938c3a363_secret_5675437d-ea6b-4f9a-9a0c-d76066004841_v1` -> `airbyte_workspace_024eaa40-75ae-4014-941d-b9e938c3a363_secret_5675437d-ea6b-4f9a-9a0c-d76066004841_v2`.
2. This means secret coordinates contain two useful pieces of metadata to help operators. The workspace id allows operators to understand what workspace
a secret belongs to. The stable prefix allows operators to understand how often a secret has been modified and group secrets by connections.
3. Not all secrets can be associated to a workspace e.g. Secrets created as part of a [Discover](./airbyte-protocol/#discover) or [Check](./airbyte-protocol/#check) operation. These secrets have a workspace id of
`00000000-0000-0000-0000-000000000000`. Whenever possible, Airbyte attempts to expire these secrets after 2 hours for security and cost reasons. 
4. Airbyte deletes old secrets when connector configuration is updated or deleted as of 0.63.10.
