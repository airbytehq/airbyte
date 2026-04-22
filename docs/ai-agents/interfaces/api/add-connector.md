---
sidebar_position: 2
---

# Add a connector

A **connector** in Airbyte Agents is a stored set of credentials for a third-party service plus everything needed to execute operations against it. You create a connector once, then reuse the returned connector ID on every subsequent call.

The `/api/v1/integrations/connectors` endpoints cover every connector operation: create, list, get, and delete.

To do the same thing from Python, see [Add a connector](../sdk/add-connector) in the SDK section.

## Create a connector

Send a `POST` to `/api/v1/integrations/connectors`. Pass the `definition_id` for the connector type and the credentials in the shape that connector expects. The response includes a connector ID. Store it somewhere you can retrieve it later.

### API token connectors

Connectors that authenticate with an API key or personal access token accept a `token` field inside `credentials`.

```bash title="Request"
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors' \
  --header 'Authorization: Bearer <application_token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "workspace_name": "default",
    "definition_id": "<github_definition_id>",
    "name": "My GitHub Connector",
    "credentials": {
      "token": "<github_personal_access_token>"
    }
  }'
```

### OAuth connectors

Connectors that use OAuth accept a `client_id`, `client_secret`, and `refresh_token` inside `credentials`. Airbyte uses the refresh token to mint and rotate access tokens automatically at execution time.

```bash title="Request"
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors' \
  --header 'Authorization: Bearer <application_token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "workspace_name": "default",
    "definition_id": "<hubspot_definition_id>",
    "name": "My HubSpot Connector",
    "credentials": {
      "client_id": "<hubspot_client_id>",
      "client_secret": "<hubspot_client_secret>",
      "refresh_token": "<hubspot_refresh_token>"
    }
  }'
```

Each connector defines its own credential shape. See the connector's page in the [Connectors](../../connectors) reference for the exact field names.

If you need to drive the OAuth consent screen yourself with your own branding, see [Build your own OAuth flow](./authentication/build-your-own). The final step of that flow calls this same endpoint with a `server_side_oauth_secret_id` in place of `credentials`.

:::note Credentials aren't validated until first execute
Airbyte doesn't validate credentials at creation time. A `200 OK` response means the request body parsed, not that the credentials work. Expect an authentication error at the first [execute](./execute) call if any credential is wrong.
:::

### Find a `definition_id`

The `definition_id` identifies the connector type. You can look it up two ways:

- Call `GET /api/v1/integrations/definitions/sources` to list every available connector type with its definition ID. See [Make your first request](./#make-your-first-request). Recommended.
- Browse the raw [Airbyte Connector Registry](https://connectors.airbyte.com/files/registries/v0/cloud_registry.json) (large file — approximately 100 MB) and copy the `sourceDefinitionId` for the entry you want.

### About `workspace_name`

The `workspace_name` field identifies which [workspace](./workspaces) the connector belongs to. Most apps use `"default"` and don't think about this again. If you need to isolate credentials across tenants or teams, pass a different value; Airbyte treats that string as the workspace name and creates the workspace on first use. See [Manage workspaces](./workspaces) for the administrative operations on top.

:::note Accepted aliases
The API also accepts `customer_name` and `external_user_id` in place of `workspace_name` for backward compatibility. Both are deprecated. Use `workspace_name` in new code.
:::

## List connectors

List the connectors in a workspace. A workspace identifier is required — pass `workspace_name` (or `workspace_id`) as a query parameter.

```bash title="Request"
curl 'https://api.airbyte.ai/api/v1/integrations/connectors?workspace_name=default' \
  --header 'Authorization: Bearer <application_token>'
```

Add `definition_id` to narrow results to a single connector type.

```bash title="Request"
curl 'https://api.airbyte.ai/api/v1/integrations/connectors?workspace_name=default&definition_id=<hubspot_definition_id>' \
  --header 'Authorization: Bearer <application_token>'
```

## Get a connector

```bash title="Request"
curl 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>' \
  --header 'Authorization: Bearer <application_token>'
```

## Delete a connector

Delete a connector when it's no longer in use. Airbyte removes the stored credentials.

```bash title="Request"
curl -X DELETE 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>' \
  --header 'Authorization: Bearer <application_token>'
```

## Next steps

Once you have a connector ID, use [Execute operations](./execute) to read data from or take actions on the connected service.
