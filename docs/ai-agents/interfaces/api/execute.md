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

### Example: List users

This example lists users from a Gong connector.

```bash title="Request"
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>/execute' \
  --header 'Authorization: Bearer <your_application_token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "entity": "users",
    "action": "list"
  }'
```

### Example: Get a specific record

This example retrieves a specific user by ID.

```bash title="Request"
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>/execute' \
  --header 'Authorization: Bearer <your_application_token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "entity": "users",
    "action": "get",
    "params": {
      "id": "<user_id>"
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

Responses include the requested data along with pagination information when applicable.

```json title="Response"
{
  "data": [...],
  "meta": {
    "pagination": {
      "totalRecords": 150,
      "currentPageSize": 50,
      "currentPageNumber": 1,
      "cursor": "<cursor_for_next_page>"
    }
  }
}
```

To retrieve additional pages, include the cursor in subsequent requests.

```bash title="Request"
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>/execute' \
  --header 'Authorization: Bearer <your_application_token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "entity": "users",
    "action": "list",
    "params": {
      "cursor": "<cursor_from_previous_response>"
    }
  }'
```

## Next steps

For detailed information about the entities and actions available for each connector, see the connector's reference documentation in the [agent connectors](/ai-agents/connectors) section.
