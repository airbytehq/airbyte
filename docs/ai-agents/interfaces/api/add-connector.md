---
sidebar_position: 2
---

# Add a connector

A **connector** in Airbyte Agents is a per-end-user instance that stores one set of credentials for a third-party service and executes operations against it. You create a connector the first time an end user connects their account, then reuse the returned connector ID on every subsequent call.

The `/api/v1/integrations/connectors` endpoints cover every connector operation: create, list, get, and delete.

To do the same thing from Python, see [Add a connector](../sdk/add-connector) in the SDK section.

## Create a connector

Send a `POST` to `/api/v1/integrations/connectors`. Pass the `definition_id` for the connector type and the end user's credentials in the shape that connector expects. The response includes a connector ID. Store it in your app database, keyed by your end user.

Most apps call this endpoint from their backend with an application token and identify the end user with `customer_name`. Airbyte uses that value as the workspace identifier, so the same string you pass here is the one that appears everywhere else in the API. If you prefer, use a [scoped token](./authentication#scoped-token) minted for that end user's workspace and omit `customer_name`; the token already carries the workspace scope.

### API token connectors

Connectors that authenticate with an API key or personal access token accept a `token` field inside `credentials`.

```bash title="Request"
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors' \
  --header 'Authorization: Bearer <application_token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "customer_name": "user_12345",
    "definition_id": "<github_definition_id>",
    "name": "My GitHub Connector",
    "credentials": {
      "token": "<user_github_personal_access_token>"
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
    "customer_name": "user_12345",
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

### Find a `definition_id`

The `definition_id` identifies the connector type. You can look it up two ways:

- Browse the [Airbyte Connector Registry](https://connectors.airbyte.com/files/registries/v0/cloud_registry.json) and copy the `sourceDefinitionId` for your connector.
- Call `GET /api/v1/integrations/definitions/sources` to list every available connector type with its definition ID. See [Make your first request](./#make-your-first-request).

## List connectors

Filter by `customer_name` to list one end user's connectors, or by `definition_id` to find every connector of a given type.

```bash title="Request"
curl 'https://api.airbyte.ai/api/v1/integrations/connectors?customer_name=user_12345' \
  --header 'Authorization: Bearer <application_token>'
```

## Get a connector

```bash title="Request"
curl 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>' \
  --header 'Authorization: Bearer <application_token>'
```

## Delete a connector

Delete a connector when an end user disconnects their account. Airbyte removes the stored credentials.

```bash title="Request"
curl -X DELETE 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>' \
  --header 'Authorization: Bearer <application_token>'
```

## Next steps

Once you have a connector ID, use [Execute operations](./execute) to read or act on the end user's data.
