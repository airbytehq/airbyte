# Implement your own OAuth flow

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

If you provide an environment where your users can create connectors, they need to supply their credentials so their agents can access their data. Airbyte provides a standard [Embedded widget](../embedded/widget) for this purpose. However, you might prefer to create a fully customized OAuth flow with your own branding and UX. In this case, implement your own OAuth flow.

This tutorial walks you through implementing a server-side OAuth flow for your users. By the end, you'll be able to initiate OAuth consent, handle the callback, and create connectors using the obtained credentials.

## How it works

The server-side OAuth flow involves four main steps:

1. **Initiate OAuth**: Your backend calls Airbyte's API to get a consent URL for the connector.
2. **User consent**: You redirect your user to the consent URL where they authorize access to their account.
3. **Handle callback**: After authorization, Airbyte redirects your user back to your app with a `secret_id`.
4. **Create connector**: You use that `secret_id` to create a connector without handling raw credentials.

```mermaid
sequenceDiagram
    participant App as Your App
    participant Airbyte as Airbyte
    participant ThirdParty as Third-Party (e.g., HubSpot)

    App->>Airbyte: POST /connectors/oauth/initiate
    Airbyte-->>App: consent_url

    App->>ThirdParty: Redirect user to consent_url
    Note over ThirdParty: User authorizes access
    ThirdParty-->>App: Redirect with secret_id

    App->>Airbyte: POST /connectors (with secret_id)
    Airbyte-->>App: connector created
```

## Prerequisites

Before implementing an OAuth flow, ensure you have:

1. **Airbyte Cloud credentials**: Your `client_id` and `client_secret` from the Airbyte Cloud dashboard under **Settings > Applications**.

2. **An bearer token**: See [Authentication](../embedded/api/authentication.md) for how to obtain one.

3. **A scoped token**: Required for workspace-level operations. Generate one using your operator token.

4. **A redirect URL**: A URL in your app that receives the OAuth callback with the `secret_id`.

## Part 1 (Optional): Configure OAuth overrides

By default, Airbyte uses its own OAuth app credentials for each connector. To use your own OAuth app, configure OAuth credential overrides.

### Endpoint

```text
PUT https://api.airbyte.ai/api/v1/oauth/credentials
```

### Authentication

Requires a bearer token.

### Request body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `connector_type` | string | Yes* | Connector name (case-insensitive). For example, `hubspot`, `Salesforce`. |
| `connector_definition_id` | UUID | Yes* | Actor definition ID for the connector. |
| `configuration` | object | Yes | Your OAuth app credentials (client_id, client_secret, etc.). |

You must provide `connector_type` or `connector_definition_id`, but it doesn't matter which one.

### Example

```bash title="Request"
curl -X PUT https://api.airbyte.ai/api/v1/oauth/credentials \
  -H 'Authorization: Bearer <operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "connector_type": "hubspot",
    "configuration": {
      "client_id": "your-hubspot-client-id",
      "client_secret": "your-hubspot-client-secret"
    }
  }'
```

```json title="Response"
{
  "id": "a1b2c3d4-e5f6-7890-ab12-cd34ef567890",
  "scope_type": "organization",
  "scope_id": "12345678-1234-1234-1234-123456789012",
  "connector_type": "source",
  "connector_definition_id": "36c891d9-4bd9-43ac-bad2-10e12756272c",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

The configuration schema varies by connector. To get the required fields for a specific connector, call `GET /api/v1/oauth/credentials/spec?connector_type=<connector_type>`.

## Part 2: Initiate the OAuth flow

When your user wants to connect a third-party service, initiate the OAuth flow to get a consent URL.

### Endpoint

```text
POST https://api.airbyte.ai/api/v1/integrations/connectors/oauth/initiate
```

### Authentication

Requires **Operator Bearer Token** or **Scoped Token**.

### Request body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `external_user_id` | string | Yes | Your user's identifier. Maps to a workspace name in Airbyte. |
| `redirect_url` | string | Yes | URL where Airbyte redirects the user after OAuth consent. Airbyte appends `?secret_id=<value>` to this URL. |
| `connector_type` | string | Yes* | Connector name (case-insensitive). For example, `hubspot`, `Salesforce`, `Intercom`. |
| `definition_id` | UUID | Yes* | Actor definition ID for the connector. |
| `oauth_input_configuration` | object | No | Additional OAuth parameters required by some connectors. |

You must provide `connector_type` or `definition_id`, but it doesn't matter which one.

### Example

```bash title="Request"
curl -X POST https://api.airbyte.ai/api/v1/integrations/connectors/oauth/initiate \
  -H 'Authorization: Bearer <operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "external_user_id": "user_12345",
    "connector_type": "hubspot",
    "redirect_url": "https://yourapp.com/oauth/callback"
  }'
```

```json title="Response"
{
  "consent_url": "https://app.hubspot.com/oauth/authorize?client_id=...&redirect_uri=...&scope=..."
}
```

In your app, redirect your user to the `consent_url` from the response. This takes them to the third-party service's authorization page where they grant access to their account.

```javascript title="your-app.js"
// Request a consent URL
const response = await fetch('https://api.airbyte.ai/api/v1/integrations/connectors/oauth/initiate', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    external_user_id: userId,
    connector_type: 'hubspot',
    redirect_url: 'https://yourapp.com/oauth/callback'
  })
});

const { consent_url } = await response.json();

// Redirect the user to the consent URL
window.location.href = consent_url;
```

## Part 3: Create a connector

After the user authorizes access, the third-party authorization flow redirects them to your `redirect_url` with a `secret_id` query parameter. Use this `secret_id` to create a connector.

Some connectors require additional configuration options. See the documentation for [your connector](../connectors/) to learn more.

### Handle the OAuth callback

When the third party redirects your user back to your app, extract the `secret_id` from the URL.

```text
https://yourapp.com/oauth/callback?secret_id=abc123def456
```

```javascript title="your-app.js"
// Example: Extract secret_id from callback URL
const urlParams = new URLSearchParams(window.location.search);
const secretId = urlParams.get('secret_id'); // Store this securely - you need it to create the connector
```

### Create the connector

Use the `secret_id` to create a connector without providing raw credentials.

### Endpoint

```text
POST https://api.airbyte.ai/api/v1/integrations/connectors
```

### Authentication

Requires **Operator Bearer Token** or **Scoped Token**.

### Request body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `external_user_id` | string | Yes | Your user's identifier. Must match the value used in the initiate step. |
| `connector_type` | string | Yes* | Connector name (case-insensitive). |
| `definition_id` | UUID | Yes* | Actor definition ID for the connector. |
| `source_template_id` | UUID | Yes* | Source template ID. Required when multiple templates exist for the connector. |
| `name` | string | No | Display name for the connector. Auto-generated if not provided. |
| `server_side_oauth_secret_id` | string | Yes** | The `secret_id` from the OAuth callback. |
| `replication_config` | object | No | Connector-specific configuration like `start_date`, `lookback_window`, etc. |
| `environment` | object | No | Additional environment configuration for the connector. |

You must provide either `connector_type`, `definition_id`, or `source_template_id`, but it doesn't matter which.

### Example

```bash title="Request"
curl -X POST https://api.airbyte.ai/api/v1/integrations/connectors \
  -H 'Authorization: Bearer <operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "external_user_id": "user_12345",
    "connector_type": "hubspot",
    "name": "My HubSpot Connection",
    "server_side_oauth_secret_id": "abc123def456"
  }'
```

```json title="Response"
{
  "id": "f1e2d3c4-b5a6-7890-fe12-dc34ba567890",
  "name": "My HubSpot Connection",
  "source_template": {
    "id": "a1b2c3d4-e5f6-7890-ab12-cd34ef567890",
    "name": "HubSpot",
    "connector_type": "hubspot"
  },
  "replication_config": {},
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

## Part 4: Execute operations

Once you create your connector, you can use the connector in hosted mode.

<Tabs>
<TabItem value="python" label="Python" default>

Instead of providing API credentials directly, provide your Airbyte Cloud credentials and the connector ID:

```python
from airbyte_agent_github import GithubConnector

connector = GithubConnector(
    external_user_id="<your_external_user_id>",
    airbyte_client_id="<your_client_id>",
    airbyte_client_secret="<your_client_secret>",
)

# Execute connector operations
@agent.tool_plain # assumes you're using Pydantic AI
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

The SDK handles the token exchange automatically. You don't need to manage tokens manually.

</TabItem>
<TabItem value="api" label="API">

```
POST https://api.airbyte.ai/api/v1/connectors/sources/<connector_id>/execute
```

Requires a **Scoped Token**.

Airbyte requires these fields in the request body.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `entity` | string | Yes | The entity to operate on (for example, `contacts`, `deals`, `companies`). |
| `action` | string | Yes | The action to perform (for example, `list`, `get`, `create`). |
| `params` | object | No | Parameters for the operation. |

Here is an example of the request.

```bash title="Request"
curl -X POST https://api.airbyte.ai/api/v1/connectors/sources/f1e2d3c4-b5a6-7890-fe12-dc34ba567890/execute \
  -H 'Authorization: Bearer <scoped_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "entity": "contacts",
    "action": "list",
    "params": {
      "limit": 10
    }
  }'
```

### Response example

```json title="Response"
{
  "result": [
    {
      "id": "123",
      "email": "contact@example.com",
      "firstname": "John",
      "lastname": "Doe"
    }
  ],
  "connector_metadata": {
    "pagination": {
      "cursor": "next_page_cursor"
    }
  }
}
```

</TabItem>
</Tabs>

## Complete example

Here's a complete Node.js example implementing the server-side OAuth flow:

```javascript title="your-app.js"
const express = require('express');
const app = express();

const AIRBYTE_API_BASE = 'https://api.airbyte.ai/api/v1';
const OPERATOR_TOKEN = process.env.AIRBYTE_OPERATOR_TOKEN;

// Step 1: Initiate OAuth when user clicks "Connect HubSpot"
app.post('/api/connect/:connectorType', async (req, res) => {
  const { connectorType } = req.params;
  const { userId } = req.body;

  const response = await fetch(`${AIRBYTE_API_BASE}/integrations/connectors/oauth/initiate`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${OPERATOR_TOKEN}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      external_user_id: userId,
      connector_type: connectorType,
      redirect_url: `https://yourapp.com/oauth/callback?user_id=${userId}&connector_type=${connectorType}`
    })
  });

  const { consent_url } = await response.json();
  res.json({ consent_url });
});

// Step 2: Handle OAuth callback
app.get('/oauth/callback', async (req, res) => {
  const { secret_id, user_id, connector_type } = req.query;

  // Step 3: Create the connector using the secret_id
  const response = await fetch(`${AIRBYTE_API_BASE}/integrations/connectors`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${OPERATOR_TOKEN}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      external_user_id: user_id,
      connector_type: connector_type,
      server_side_oauth_secret_id: secret_id
    })
  });

  const connector = await response.json();

  // Store connector.id for future operations
  await saveConnectorForUser(user_id, connector.id);

  // Redirect user to success page
  res.redirect('/connection-success');
});

// Step 4: Execute operations using the connector
app.post('/api/execute', async (req, res) => {
  const { userId, entity, action, params } = req.body;

  // Get the user's scoped token and connector ID
  const scopedToken = await getScopedTokenForUser(userId);
  const connectorId = await getConnectorIdForUser(userId);

  const response = await fetch(`${AIRBYTE_API_BASE}/connectors/sources/${connectorId}/execute`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${scopedToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ entity, action, params })
  });

  const result = await response.json();
  res.json(result);
});

app.listen(3000);
```

## Troubleshooting

### "Workspace not found" error

Ensure the `external_user_id` you provide in the initiate step matches exactly what you use when creating the connector. Airbyte creates the workspace automatically on first use.

### OAuth consent URL returns an error

- Verify your OAuth credentials are configured correctly (Part 1).
- Check that the connector supports OAuth authentication.
- Ensure your redirect URL is properly URL-encoded if it contains special characters.

### "Invalid secret_id" when creating connector

- The `secret_id` may have expired. OAuth secrets are short-lived. Initiate a new OAuth flow.
- Ensure you're using the exact `secret_id` from the callback URL without modification.

### Connector creation succeeds but operations fail

- Verify the user completed the OAuth consent flow and granted all required permissions.
- Check that you properly provided all of that connector's required fields.
- Some connectors require specific scopes. Review the connector's documentation.
