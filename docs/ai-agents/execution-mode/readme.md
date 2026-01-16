import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Using agent connectors in hosted execution mode

## Overview

Hosted execution mode allows you to run agent connector operations through Airbyte. In this mode, you still execute connectors and tool calls from your agent, but API credentials are stored securely in Airbyte Cloud, and the connector proxies all requests through Airbyte's infrastructure.

## Local mode vs hosted mode

When you run connector operations locally, you store API credentials locally and provide them directly to the API, running those connector operations in your local environment. This approach, while viable at first, reaches limits quickly when you're dealing with large numbers of customers who have their own environments and credentials. You may not want to manage these credentials and may not want to store them at all.

With hosted execution, sensitive API credentials never leave Airbyte Cloud, multiple end-users can have separate credentials managed centrally, and credential lifecycle (refresh, rotation) is handled automatically.

| Aspect                   | Local Mode                            | Hosted Mode                             |
| ------------------------ | ------------------------------------- | --------------------------------------- |
| **Credentials provided** | Actual API keys/tokens                | Airbyte Cloud client credentials        |
| **Credential storage**   | Managed by you locally                | Stored securely in Airbyte Cloud        |
| **API calls**            | Direct HTTP calls to external APIs    | Proxied through Airbyte Cloud           |
| **Entity cache**         | Not available                         | Available                               |

### When to use local mode

- Development and testing
- Single-user scenarios
- You need full, local control over credentials
- Quick prototyping

### When to use hosted mode

- Production B2B applications
- Multi-tenant scenarios where different customers have different credentials
- Credential security is a priority
- You want centralized credential management

## Prerequisites

Before using hosted execution mode, ensure you have:

1. Airbyte Cloud account

2. Airbyte credentials

   - Client ID
   - Client Secret

3. The third-party API credentials you want to use (for example, a Gong access key and access key secret)

4. An installed agent connector package. For example:

   ```bash
   uv pip install airbyte-ai-gong
   ```

   See [Connectors](../connectors) for a full list of connectors.

## Authentication

Before running operations in hosted mode, you must create a connector in Airbyte Cloud. This stores your API credentials securely and associates them with a workspace.

### Step 1: Get an application token

Request an application token using your Airbyte client credentials:

```bash
curl --location 'https://cloud.airbyte.com/api/v1/applications/token' \
  --header 'Content-Type: application/json' \
  --data '{
    "client_id": "<your_client_id>",
    "client_secret": "<your_client_secret>"
  }'
```

Save the returned token for the next steps.

### Step 2: Get a scoped token

Request a scoped token for your workspace. The `workspace_name` becomes your `external_user_id` when using the connector:

```bash
curl --location 'https://api.airbyte.ai/api/v1/embedded/scoped-token' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Bearer <APPLICATION_TOKEN>' \
  --data '{
    "workspace_name": "<your_workspace_name>"
  }'
```

## Create a connector

Create a connector with your API credentials. Airbyte stores these credentials securely in Airbyte Cloud.

```bash
curl -X POST "https://api.airbyte.ai/v1/integrations/sources" \
    -H "Authorization: Bearer {SCOPED_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
      "source_template_id": "{SOURCE_TEMPLATE_ID}",
      "workspace_id": "{WORKSPACE_ID}",
      "name": "...",
      "auth_config": {
         ...
      }
    }'
```

Note the returned connector ID for reference.

## Run operations in hosted mode

Once you create your connector, you can use the connector in hosted mode.

<Tabs>
<TabItem value="python" label="Python" default>

Instead of providing API credentials directly, provide your Airbyte Cloud credentials and the external user ID (workspace name).

```python title="agent.py"
from airbyte_ai_gong import GongConnector

connector = GongConnector(
    external_user_id="<your_workspace_name>",
    airbyte_client_id="<your_client_id>",
    airbyte_client_secret="<your_client_secret>",
)
```

Use the `@Connector.describe` decorator to expose the connector as a tool for your agent. The decorator automatically generates a comprehensive tool description from the connector's metadata.

```python title="agent.py"
from pydantic_ai import Agent
from airbyte_ai_gong import GongConnector

agent = Agent("openai:gpt-4o")
connector = GongConnector(
    external_user_id="<your_workspace_name>",
    airbyte_client_id="<your_client_id>",
    airbyte_client_secret="<your_client_secret>",
)

@agent.tool_plain
@GongConnector.describe
async def gong_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

The `@GongConnector.describe` decorator automatically expands the docstring to include all available entities and actions, their required and optional parameters, and response structure details. This gives the LLM everything it needs to correctly call the connector.

### Complete example

```python
#!/usr/bin/env python3
"""Example: Using Gong connector in hosted execution mode with an AI agent."""

import asyncio
from pydantic_ai import Agent
from airbyte_ai_gong import GongConnector


# Initialize connector in hosted mode
connector = GongConnector(
    external_user_id="customer-workspace-123",
    airbyte_client_id="your_airbyte_client_id",
    airbyte_client_secret="your_airbyte_client_secret",
)

# Create agent
agent = Agent("openai:gpt-4o")

# Register connector as a tool using the describe decorator
@agent.tool_plain
@GongConnector.describe
async def gong_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})


async def main():
    # The agent can now use the Gong connector to answer questions
    result = await agent.run("List the users in Gong")
    print(result.data)


if __name__ == "__main__":
    asyncio.run(main())
```

</TabItem>
<TabItem value="api" label="API">

You can execute connector operations directly via the REST API.

First, retrieve your connector ID using your external user ID and connector definition ID:

```bash title="Request"
curl --location 'https://api.airbyte.ai/api/v1/connectors/connectors_for_user?external_user_id=<your_workspace_name>&definition_id=32382e40-3b49-4b99-9c5c-4076501914e7' \
  --header 'Authorization: Bearer <APPLICATION_TOKEN>'
```

The response contains your connector ID:

```json title="Response"
{
  "connectors": [
    {
      "id": "<connector_id>",
      "name": "gong-connector"
    }
  ]
}
```

Use the connector ID to execute operations:

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/<connector_id>/execute' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Bearer <APPLICATION_TOKEN>' \
  --data '{
    "entity": "users",
    "action": "list",
    "params": {}
  }'
```

The response contains the operation result:

```json
{
  "result": [
    {
      "id": "user-123",
      "first_name": "John",
      "last_name": "Doe",
      "email_address": "john.doe@example.com"
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

## Troubleshooting

### No connector found for user

- Ensure you've created a connector for the workspace.
- Verify the `external_user_id` matches the `workspace_name` used during setup.

### Authentication errors (401/403)

- Check that your Airbyte client ID and secret are correct.
- Verify your application token hasn't expired.
- Ensure the connector was created with valid API credentials.

### Token expiration

- Application tokens expire after ~15 minutes.
- The SDK handles token refresh automatically during normal operation.
- If you see persistent auth errors, verify your client credentials are still valid.
