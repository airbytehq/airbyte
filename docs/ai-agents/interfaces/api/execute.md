---
sidebar_position: 3
---

# Execute operations

You can execute operations directly through the Airbyte Agent API. This approach is useful when you're not using Python, when building custom integrations, or when you need to execute operations from a backend service.

To execute operations from Python code instead, see [Execute operations](../sdk/execute) in the SDK section.

## Authentication

Before making API calls, you need an application token. For details on obtaining tokens, see [Token types](./authentication#token-types).

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

This example searches for records using filter conditions. The search action is available when you have the context store enabled.

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
    "connector_instance_id": "<connector_id>",
    "execution_time_ms": 1189
  }
}
```

- `result` is whatever the operation returns — an array for `list` and `search`, a single object for `get`, or a byte stream for `download`.
- `connector_metadata` surfaces pagination state. The exact key names depend on the connector. Expect `hasNextPage` and `endCursor` on most connectors; some connectors return `has_next_page` and `end_cursor` instead. Both mean the same thing.
- `execution_metadata` always includes `connector_instance_id` and `execution_time_ms`.

### Paginate through results

When `connector_metadata.hasNextPage` is `true`, pass the cursor from the previous response as `params.cursor` to get the next page.

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
