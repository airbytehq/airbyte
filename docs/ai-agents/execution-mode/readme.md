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

Before running operations in hosted mode, you must create a connector instance in Airbyte Cloud. This stores your API credentials securely and associates them with a workspace.

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

Operations work the same way as local mode. The connector handles authentication and routing through Airbyte Cloud.

```python title="agent.py"
import asyncio

async def main():
    connector = GongConnector(
        external_user_id="<your_workspace_name>",
        airbyte_client_id="<your_client_id>",
        airbyte_client_secret="<your_client_secret>",
    )
    
    # List users
    result = await connector.users.list()
    
    print(f"Found {len(result.data)} users")
    for user in result.data[:5]:
        print(f"  - {user.first_name} {user.last_name} ({user.email_address})")
    
    # Handle pagination
    if result.meta and result.meta.pagination:
        print(f"Total records: {result.meta.pagination.total_records}")

asyncio.run(main())
```

### Complete example

```python
#!/usr/bin/env python3
"""Example: Using Gong connector in hosted execution mode."""

import asyncio
from airbyte_ai_gong import GongConnector


async def main():
    # Initialize connector in hosted mode
    connector = GongConnector(
        external_user_id="customer-workspace-123",
        airbyte_client_id="your_airbyte_client_id",
        airbyte_client_secret="your_airbyte_client_secret",
    )
    
    print(f"Connector: {connector.connector_name} v{connector.connector_version}")
    
    # Fetch users
    print("Fetching users...")
    result = await connector.users.list()
    
    if result.data:
        print(f"Found {len(result.data)} users:")
        for user in result.data[:5]:
            print(f"  - {user.first_name} {user.last_name}")
            print(f"    Email: {user.email_address}")
            print(f"    Active: {user.active}")
    
    # Fetch calls with date filter
    print("\nFetching recent calls...")
    calls_result = await connector.calls.list(
        from_date_time="2025-01-01T00:00:00Z",
        to_date_time="2025-01-14T00:00:00Z"
    )
    
    if calls_result.data:
        print(f"Found {len(calls_result.data)} calls")

if __name__ == "__main__":
    asyncio.run(main())
```

</TabItem>
<TabItem value="api" label="API">

You can execute connector operations directly via the REST API.

First, retrieve your connector instance ID using your external user ID and connector definition ID:

```bash title="Request"
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances_for_user?external_user_id=<your_workspace_name>&definition_id=32382e40-3b49-4b99-9c5c-4076501914e7' \
  --header 'Authorization: Bearer <APPLICATION_TOKEN>'
```

The response contains your connector instance ID:

```json title="Response"
{
  "instances": [
    {
      "id": "<connector_instance_id>",
      "name": "gong-connector"
    }
  ]
}
```

Use the connector instance ID to execute operations:

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/<connector_instance_id>/execute' \
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

### No connector instance found for user

- Ensure you've created a connector instance for the workspace.
- Verify the `external_user_id` matches the `workspace_name` used during setup.

### Authentication errors (401/403)

- Check that your Airbyte client ID and secret are correct.
- Verify your application token hasn't expired.
- Ensure the connector instance was created with valid API credentials.

### Token expiration

- Application tokens expire after ~15 minutes.
- The SDK handles token refresh automatically during normal operation.
- If you see persistent auth errors, verify your client credentials are still valid.
