---
sidebar_position: 2
---

# Add a connector

A **connector** in Airbyte Agents is a stored set of credentials for a third-party service plus everything needed to execute operations against it. You create a connector once, then reuse the returned connector ID on every subsequent call.

The `/api/v1/integrations/connectors` endpoints cover every connector operation: create, list, get, and delete.

To do the same thing from Python, see [Add a connector](../sdk/add-connector) in the SDK section.

## Create a connector

Send a `POST` to `/api/v1/integrations/connectors`. Pass an identifier for the connector type and the credentials in the shape that connector expects. The response includes a connector ID. Store it somewhere you can retrieve it later.

The request body accepts one of three connector-type identifiers:

- `definition_id`: the connector definition UUID (returned as `sourceDefinitionId` from the definitions endpoint). Recommended.
- `connector_type`: a human-readable slug such as `"linear"` or `"hubspot"`.
- `source_template_id`: a template UUID. Useful when your organization has published custom source templates. See [Source templates](#source-templates) below.

Exactly one of the three is required. If none is provided, the server responds with `422 "One of connector_type, definition_id, or source_template_id must be provided"`.

### API token connectors

Connectors that authenticate with a single API key or personal access token take one credential field. The exact field name is connector-specific — GitHub uses `personal_access_token`, Linear uses `api_key`, Notion uses `token`, and so on. See the connector's page in the [Connectors](../../connectors) reference for the field name the connector expects.

```bash title="Request"
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors' \
  --header 'Authorization: Bearer <application_token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "workspace_name": "default",
    "definition_id": "<github_definition_id>",
    "name": "My GitHub Connector",
    "credentials": {
      "option_title": "PAT Credentials",
      "personal_access_token": "<github_pat>"
    },
    "replication_config": {
      "repositories": ["airbytehq/airbyte"]
    }
  }'
```

Some connectors also need non-credential configuration. Pass those fields under `replication_config` on the request body — not at the top level. GitHub's `replication_config.repositories` above is one example. Without it the call fails with `422 "required property 'repositories' not found"`; the same error applies if you place `repositories` at the top level instead. See the connector's page in the [Connectors](../../connectors) reference for any extra required fields and where they belong.

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

Each connector defines its own credential shape. See the connector's page in the [Connectors](../../connectors) reference for the exact field names. Airbyte validates credentials on the first [execute](./execute) call; a `200 OK` here means the request body parsed.

<!--
AGENTIC-1141: credentials aren't validated at create-time; any typo in the
client_id/secret/refresh_token surfaces as an auth error on the first
execute. Don't highlight this in the public narrative — the single line
above covers it neutrally. Remove the note once create-time validation
lands.
-->

### Find a `definition_id`

The `definition_id` identifies the connector type. You can look it up two ways:

- Call `GET /api/v1/integrations/definitions/sources` to list every available connector type. See [Make your first request](./#make-your-first-request). Recommended.
- Filter by name to get a single connector in one call — for example, to grab the GitHub `definition_id`:

```bash
curl -s 'https://api.airbyte.ai/api/v1/integrations/definitions/sources?name=github' \
  -H 'Authorization: Bearer <application_token>' \
  | jq -r '.definitions[0].sourceDefinitionId'
```

:::note Naming
The definitions endpoint returns the ID as `sourceDefinitionId`. The connector creation endpoint accepts it as `definition_id`. Both names refer to the same UUID.
:::

### Source templates

A **source template** is the organization-level catalog entry a connector is provisioned from: a connector definition plus the default configuration, stream selection, and customizations your organization has agreed on for that connector. Every connector instance belongs to exactly one source template.

That's why [list](#list-connectors) and [get](#get-a-connector) responses carry a nested `summarized_source_template` alongside the underlying `source_definition_id`. The template's UUID also appears as the `source_template_id` field when you [create](#create-a-connector) a connector from a specific template.

Most apps won't set `source_template_id` explicitly — passing `definition_id` or `connector_type` picks the default template for that connector type. Use `source_template_id` when your organization has more than one template for the same connector type and you need to pin a specific one.

### About `workspace_name`

The `workspace_name` field identifies which [workspace](./workspaces) the connector belongs to. Most apps use `"default"` and don't think about this again. If you need to isolate credentials across tenants or teams, pass a different value. See [Manage workspaces](./workspaces) for the administrative operations on top.

<!--
AGENTIC-1140: create-connector doesn't autocreate workspaces (404s when
the workspace_name is new), while scoped-token mint does autocreate.
Readers following the default narrative on this page stay on "default",
so they never encounter this. Revisit when autocreate is consistent
across endpoints.
-->

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

```json title="Response"
{
  "data": [
    {
      "id": "<connector_id>",
      "name": "My Linear Connector",
      "summarized_source_template": {
        "id": "<source_template_id>",
        "name": "Linear",
        "actor_definition_id": "<definition_id>",
        "icon": "https://connectors.airbyte.com/files/metadata/airbyte/source-linear/latest/icon.svg",
        "mode": "REPLICATION"
      },
      "created_at": "2026-04-20T21:57:20.991787Z",
      "updated_at": "2026-04-20T21:57:20.991787Z"
    }
  ]
}
```

Each entry's `id` is the connector ID you pass to [Execute operations](./execute) and [Get a connector](#get-a-connector). The nested `summarized_source_template.actor_definition_id` is the connector's definition ID.

## Get a connector

```bash title="Request"
curl 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>' \
  --header 'Authorization: Bearer <application_token>'
```

The response mirrors the `create` response: the connector `id` plus its full `source_template` (including the user config spec), any configured `entities`, and timestamps.

## Delete a connector

Delete a connector when it's no longer in use. Airbyte removes the stored credentials.

```bash title="Request"
curl -X DELETE 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>' \
  --header 'Authorization: Bearer <application_token>'
```

```json title="Response (202)"
{
  "job_id": "<deletion_job_id>"
}
```

Deletion is asynchronous: the server returns `202 Accepted` with a `job_id` and removes the connector in the background. If the same connector ID disappears from subsequent [List connectors](#list-connectors) responses, the deletion has completed.

## Errors

Errors from the connector endpoints use the same envelope across the API. The HTTP status code tells you the error family; the body carries a human message plus a machine-readable `errors` list.

```json title="Example 422"
{
  "message": "Value error, One of connector_type, definition_id, or source_template_id must be provided",
  "errors": [
    {
      "field": "body",
      "message": "Value error, One of connector_type, definition_id, or source_template_id must be provided",
      "error_code": "value_error"
    }
  ]
}
```

Common codes:

- `400`: the credentials block doesn't match the connector's auth scheme. The `message` typically includes `"Credentials do not match any auth scheme. Provided keys: [...]. Available schemes: ..."`.
- `401` / `403`: missing or invalid bearer token.
- `404`: the `workspace_name` doesn't exist, or the connector ID in the URL isn't found.
- `422`: the request body parsed but failed schema validation — missing required field on the connector spec, unknown property, and so on.

## Next steps

Once you have a connector ID, use [Execute operations](./execute) to read data from or take actions on the connected service.
