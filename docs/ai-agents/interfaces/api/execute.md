---
sidebar_position: 3
---

# Execute operations

You can execute operations directly through the Airbyte Agent API. This approach is useful when you're not using Python, when building custom integrations, or when you need to execute operations from a backend service.

To execute operations from Python code instead, see [Execute operations](../sdk/execute) in the SDK section.

## Authentication

Before making API calls, you need an application token. For details on obtaining tokens, see [Token types](./authentication#token-types).

## Find the connector ID

Every execute call targets a specific connector by its `connector_id` in the URL. If you didn't store the ID from the [create response](./add-connector), look it up by workspace and connector type. Call `GET /api/v1/integrations/connectors` and filter by `workspace_name` and `definition_id`:

```bash title="Request"
curl 'https://api.airbyte.ai/api/v1/integrations/connectors?workspace_name=default&definition_id=<hubspot_definition_id>' \
  --header 'Authorization: Bearer <your_application_token>'
```

`definition_id` is the connector type (HubSpot, GitHub, and so on). See [Find a `definition_id`](./add-connector#find-a-definition_id) for how to look one up. The response includes each matching connector's `id` — use it in the execute URL below.

The Airbyte Agent Python SDK can resolve a connector by its slug (for example, `"hubspot"`) without any IDs. Consider using the [SDK](../sdk/execute) if you want to avoid managing connector IDs in application code.

## Execute an operation

To execute an operation against a connector, send a POST request to the execute endpoint with the entity, action, and any required parameters.

```bash title="Request"
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>/execute' \
  --header 'Authorization: Bearer <your_application_token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "entity": "<entity_name>",
    "action": "<action_name>",
    "params": {}
  }'
```

The request body contains three fields:

| Field | Type | Description |
|-------|------|-------------|
| `entity` | `string` | The entity to operate on, such as `users`, `calls`, or `issues`. |
| `action` | `string` | The action to perform, such as `list`, `get`, or `search`. |
| `params` | `object` | Parameters for the action. The required parameters depend on the entity and action. |

### Example: List issues

This example lists issues from a Linear connector.

```bash title="Request"
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>/execute' \
  --header 'Authorization: Bearer <your_application_token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "entity": "issues",
    "action": "list"
  }'
```

### Example: Get a specific record

This example retrieves a specific issue by ID.

```bash title="Request"
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>/execute' \
  --header 'Authorization: Bearer <your_application_token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "entity": "issues",
    "action": "get",
    "params": {
      "id": "<issue_id>"
    }
  }'
```

### Example: Search with filters

This example searches for records using filter conditions.

:::note `search` reads from the [context store](../../concepts/context-store)
The `search` action reads from Airbyte's pre-indexed context store, not the live third-party API. The store is enabled by default in new organizations, and Airbyte populates it per connector after the connector is created. If you call `search` while the connector's context store still shows `Loading` or `Building Preview` on the Credentials page, the call returns an error at runtime. Wait for the status to reach `Preview` or `Ready`, or use `list`/`get` against the live API until it does.
:::

```bash title="Request"
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>/execute' \
  --header 'Authorization: Bearer <your_application_token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "entity": "users",
    "action": "search",
    "params": {
      "query": {"filter": {"eq": {"active": true}}},
      "limit": 100
    }
  }'
```

## Download files

Some connectors support a `download` action for entities like attachments and media files. Unlike other actions that return JSON, download responses return raw binary content with a `Content-Disposition` header.

:::note Download responses bypass the envelope
`download` is the one execute response that does not use the `{status, result, connector_metadata, execution_metadata}` envelope described in [Response format](#response-format). The server streams the file bytes directly with an appropriate `Content-Type`, so your client reads the body as bytes instead of parsing JSON.
:::

:::warning Verify the downloaded file
If the target attachment ID doesn't exist (or the connector can't fetch it), the server currently returns `200 OK` with a zero-byte body rather than a structured error. Always check `Content-Length > 0` (or inspect the saved file size) before treating a download as successful.
:::

To find downloadable files, first list the relevant entity to discover IDs. For example, list a ticket's comments to find attachment metadata, then download a specific attachment.

```bash title="Step 1: Discover attachments"
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>/execute' \
  --header 'Authorization: Bearer <your_application_token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "entity": "ticket_comments",
    "action": "list",
    "params": {
      "ticket_id": "<ticket_id>"
    }
  }'
```

 The response includes attachment metadata (IDs, filenames, content types) within each comment. Use the attachment ID to download the file:

```bash title="Step 2: Download the file"
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>/execute' \
  --header 'Authorization: Bearer <your_application_token>' \
  --header 'Content-Type: application/json' \
  --output attachment.pdf \
  --data '{
    "entity": "attachments",
    "action": "download",
    "params": {
      "attachment_id": "<attachment_id>"
    }
  }'
```

You can also stream the response in your app code. For example, using JavaScript with `fetch`:

```javascript title="download.js"
const response = await fetch(
  `https://api.airbyte.ai/api/v1/integrations/connectors/${connectorId}/execute`,
  {
    method: "POST",
    headers: {
      Authorization: `Bearer ${applicationToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      entity: "attachments",
      action: "download",
      params: { attachment_id: attachmentId },
    }),
  }
);

const blob = await response.blob();
const url = URL.createObjectURL(blob);
```

## Response format

Every execute response uses the same top-level envelope. The connector's records land in `result`, pagination details land in `connector_metadata`, and timing and identity land in `execution_metadata`.

```json title="Response"
{
  "status": "success",
  "result": [
    { "id": "1", "name": "Ada Lovelace" },
    { "id": "2", "name": "Grace Hopper" }
  ],
  "connector_metadata": {
    "hasNextPage": true,
    "endCursor": "<cursor_for_next_page>"
  },
  "execution_metadata": {
    "connector_instance_id": "source_id:<connector_id>",
    "execution_time_ms": 1189
  }
}
```

- `result` is whatever the operation returns — an array for `list` and `search`, a single object for `get`, or a byte stream for `download`.
- `connector_metadata` surfaces pagination state. The exact key names depend on the connector. Expect `hasNextPage` and `endCursor` on most connectors; some connectors return `has_next_page` and `end_cursor` instead. Both mean the same thing.
- `execution_metadata` always includes `connector_instance_id` and `execution_time_ms`. `connector_instance_id` is a typed identifier string — for a connector created through [Add a connector](./add-connector), it currently comes back as `"source_id:<connector_id>"`. Strip the `source_id:` prefix if you need to compare it against the bare `connector_id` you passed in the URL.

### Paginate through results

When `connector_metadata.hasNextPage` is `true`, pass the cursor from the previous response as `params.cursor` to get the next page. On the request side, `cursor` is the conventional parameter name for pagination across Airbyte connectors, even when the response key is `endCursor` or `end_cursor`. A small number of connectors use different request keys (for example, an offset-based pager might accept `offset` and `limit`); check the connector's reference page if `cursor` is rejected.

```bash title="Request"
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>/execute' \
  --header 'Authorization: Bearer <your_application_token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "entity": "users",
    "action": "list",
    "params": {
      "cursor": "<endCursor_from_previous_response>"
    }
  }'
```

Keep requesting pages until `hasNextPage` is `false`.

## Next steps

For detailed information about the entities and actions available for each connector, see the connector's reference documentation in the [agent connectors](/ai-agents/connectors) section.
