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

## Operational Details

1. When configuration is updated, Airbyte increments a secret coordinate's version while preserving the prefix.
E.g. `airbyte_workspace_024eaa40-75ae-4014-941d-b9e938c3a363_secret_5675437d-ea6b-4f9a-9a0c-d76066004841_v1` -> `airbyte_workspace_024eaa40-75ae-4014-941d-b9e938c3a363_secret_5675437d-ea6b-4f9a-9a0c-d76066004841_v2`.
2. This means secret coordinates contain two useful pieces of metadata to help operators. The workspace id allows operators to understand what workspace
a secret belongs to. The stable prefix allows operators to understand how often a secret has been modified and group secrets by connections.
3. Not all secrets can be associated to a workspace e.g. Secrets created as part of a [Discover](./airbyte-protocol/#discover) or [Check](./airbyte-protocol/#check) operation. These secrets have a workspace id of
`00000000-0000-0000-0000-000000000000`. Whenever possible, Airbyte attempts to expire these secrets after 2 hours for security and cost reasons. 
4. Airbyte deletes old secrets when connector configuration is updated or deleted as of 0.63.10.
