---
sidebar_label: "Hosted connectors"
sidebar_position: 3
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Hosted agent connectors in the Agent Engine

When you run connector operations with the [Python SDK](tutorial-python), you store API credentials locally and provide them directly to the API through agent connectors. This approach, while viable at first, reaches limits quickly. You may find yourself dealing with large numbers of customers who have their own environments and credentials. You may not want to manage these credentials and or store them at all.

With hosted execution, sensitive API credentials never leave Airbyte, multiple end-users can have separate credentials managed centrally, and Airbyte handles credential lifecycle (refresh, rotation) automatically.

Generally, local mode is most appropriate for development, testing, single-user scenarios, and cases where you need local control over credentials. Hosted mode is most appropriate for production applications, multi-tenant scenarios, when security is a priority, and when you want centralized credential management.

| Aspect                   | Local Mode                         | Hosted Mode                           |
| ------------------------ | ---------------------------------- | ------------------------------------- |
| **Credentials provided** | Actual API keys/tokens             | Agent Engine client credentials      |
| **Credential storage**   | Managed by you locally             | Stored securely in Airbyte      |
| **API calls**            | Direct HTTP calls to external APIs | API calls proxy through Airbyte |
| **Context store**         | Not available                      | Available                             |

## Prerequisites

Before using hosted execution mode, ensure you have:

1. An Agent Engine account and credentials:

2. Agent Engine credentials

   - Client ID
   - Client Secret

3. The third-party API credentials you want to use. For example, a GitHub personal access token.

If you're using the Python SDK, you also need:

1. Python 3.13 or later

2. An installed agent connector package. For example:

   ```bash
   uv pip install airbyte-agent-github
   ```

## Authentication

Before you can run connectors in hosted mode, you need a scoped token for authentication. This stores your API credentials securely and associates them with a customer.

### Step 1: Get an application token

Request an application token using your Airbyte client credentials:

```bash title="Request"
curl --location 'https://api.airbyte.ai/api/v1/account/applications/token' \
  --header 'Content-Type: application/json' \
  --data '{
    "client_id": "<your_client_id>",
    "client_secret": "<your_client_secret>"
  }'
```

Save the returned token for the next step.

### Step 2: Get a scoped token

Create a scoped token for your customer. A scoped token supports certain customer-level operations, and you need it later when you create a connector.

```bash title="Request"
curl --location 'https://api.airbyte.ai/api/v1/account/applications/scoped-token' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Bearer <APPLICATION_TOKEN>' \
  --data '{
    "customer_name": "<your_customer_name>"
  }'
```

## Create a connector

Once you have a scoped token, create a connector with your API credentials. Airbyte stores these credentials securely in the Agent Engine. You need the following values.

- `connector_type`: The case-insensitive name or ID of the source template for the connector type. For example, `GitHub` or `github`. List available templates by calling `GET /api/v1/integrations/templates/sources` with your scoped token.

- `customer_name`: Retrieve this by calling `GET /api/v1/account/applications/scoped-token/info` with your scoped token.

- Additional configuration fields that may or may not be mandatory, depending on the source. If applicable, these fields are explained in the reference docs for your connector.

  - `credentials`: Authentication information for your connector.

  - `environment`: Connector-specific configurations for the connector.

This is what the request looks like when you're using a personal access token. See more examples in the [authentication docs](/ai-agents/connectors/github/AUTH).

```bash title="Request"
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
    -H "Authorization: Bearer <scoped_token>" \
    -H "Content-Type: application/json" \
    -d '{      
      "connector_type": "github",
      "customer_name": "<your_customer_name>",
      "replication_config": {
        "repositories": ["airbytehq/airbyte"],
        "credentials": {
            "option_title": "PAT Credentials",
            "personal_access_token": "<GitHub personal access token (fine-grained or classic)>"
        }
      }
    }'
```

## Execute operations in hosted mode

Once you create your connector, you can use the connector in hosted mode.

<Tabs>
<TabItem value="python" label="Python" default>

Instead of providing API credentials directly, provide your Agent Engine credentials and the connector ID:

```python
from airbyte_agent_github import GithubConnector, AirbyteAuthConfig

connector = GithubConnector(
    auth_config=AirbyteAuthConfig(
        external_user_id="<your_external_user_id>",
        airbyte_client_id="<your_client_id>",
        airbyte_client_secret="<your_client_secret>",
    )
)

# Execute connector operations
@agent.tool_plain # assumes you're using Pydantic AI
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

Once initialized, the connector works the same way as in local mode. The SDK handles the token exchange automatically. You don't need to manage tokens manually.

</TabItem>
<TabItem value="api" label="API">

You can execute connector operations directly via the REST API.

```bash title="Request"
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>/execute' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Bearer <application_token>' \
  --data '{
    "entity": "issues",
    "action": "list",
    "params": {
      "owner": "airbytehq",
      "repo": "airbyte"
    }
  }'
```

The response contains the operation result.

```json title="Response"
{
  "result": [
    {
      "id": 12345,
      "number": 100,
      "title": "Example issue title",
      "state": "open",
      "user": {
        "login": "octocat"
      }
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

### No connector found for this user

- Ensure you've created a connector for the right customer name.

### Authentication errors (401/403)

- Check that your Airbyte client ID and secret are correct.
- Verify your application token hasn't expired.

### Token expiration

- Application tokens expire after ~15 minutes.
- The Python SDK handles token refresh automatically during normal operation. The API doesn't and you must request new tokens manually.
- If you see persistent authentication errors, verify your client ID and client secret are still valid.
