import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Using agent connectors in hosted execution mode

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

1. An Airbyte Cloud account and credentials:

2. Airbyte credentials

   - Client ID
   - Client Secret

3. The third-party API credentials you want to use. For example, a GitHub personal access token.

If you're using the Python SDK, you also need:

1. Python 3.11 or later

2. An installed agent connector package. For example:

   ```bash
   uv pip install airbyte-agent-github
   ```

## Authentication

Before you can run connectors in hosted mode, you need a scoped token for authentication. This stores your API credentials securely and associates them with a workspace.

### Step 1: Get an application token

Request an application token using your Airbyte client credentials:

```bash title="Request"
curl --location 'https://cloud.airbyte.com/api/v1/applications/token' \
  --header 'Content-Type: application/json' \
  --data '{
    "client_id": "<your_client_id>",
    "client_secret": "<your_client_secret>"
  }'
```

Save the returned token for the next step.

### Step 2: Get a scoped token

Create a scoped token for your workspace.

```bash title="Request"
curl --location 'https://api.airbyte.ai/api/v1/embedded/scoped-token' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Bearer <APPLICATION_TOKEN>' \
  --data '{
    "workspace_name": "<your_workspace_name>"
  }'
```

## Create a connector

Once you have a scoped token, create a connector with your API credentials. Airbyte stores these credentials securely in Airbyte Cloud. You need the following values.

- **source_template_id**: The ID of the source template for the connector type. List available templates by calling `GET /api/v1/integrations/templates/sources` with your scoped token.

- **workspace_id**: Your workspace ID. Retrieve it by calling `GET /api/v1/embedded/scoped-token/info` with your scoped token.

- Additional configuration fields that may or may not be mandatory, depending on the source. If applicable, these fields are explained in the reference docs for your connector.

  - **source_config**: Connector-specific configurations for direct connectors.

  - **auth_config**: Authentication information for your connector.

  - **user_config**: Connector-specific configurations for replication connectors.

For GitHub, you only need an authentication configuration. See the examples in the [authentication docs](/ai-agents/connectors/github/REFERENCE). This is what the request looks like when you're using a personal access token.

```bash title="Request"
curl -X POST "https://api.airbyte.ai/api/v1/integrations/sources" \
    -H "Authorization: Bearer <scoped_token>" \
    -H "Content-Type: application/json" \
    -d '{
      "source_template_id": "<source_template_id>",
      "workspace_id": "<workspace_id>",
      "name": "...",
      "auth_config": {
        "token": "<GitHub personal access token (fine-grained or classic)>"
      },
    }'
```

## Run operations in hosted mode

Once you create your connector, you can use the connector in hosted mode.

First, retrieve your connector ID.

1. Log into [app.airbyte.ai](https://app.airbyte.ai).

2. Click **Connectors**.

3. Find your connector in the list of connectors. Under the connector name, click the copy button next to the connector ID.

4. Use the connector ID to execute operations.

<Tabs>
<TabItem value="python" label="Python" default>

Instead of providing API credentials directly, provide your Airbyte Cloud credentials and the connector ID:

```python
from airbyte_agent_github import GithubConnector

connector = GithubConnector(
    connector_id="<your_connector_id>",
    airbyte_client_id="<your_client_id>",
    airbyte_client_secret="<your_client_secret>",
)

# Execute connector operations
issues = await connector.issues.list(owner="airbytehq", repo="airbyte")
```

Once initialized, the connector works the same way as in local mode. The SDK handles the token exchange (application token → scoped token) automatically, so you don't need to manage tokens manually.

</TabItem>
<TabItem value="api" label="API">

You can execute connector operations directly via the REST API.

    ```bash
    curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/<connector_id>/execute' \
      --header 'Content-Type: application/json' \
      --header 'Authorization: Bearer <APPLICATION_TOKEN>' \
      --data '{
        "entity": "issues",
        "action": "list",
        "params": {
          "owner": "airbytehq",
          "repo": "airbyte"
        }
      }'
    ```

The response contains the operation result:

```json
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

### No connector found for user

- Ensure you've created a connector for the workspace.

### Authentication errors (401/403)

- Check that your Airbyte client ID and secret are correct.
- Verify your application token hasn't expired.

### Token expiration

- Application tokens expire after ~15 minutes.
- The Python SDK handles token refresh automatically during normal operation. The API doesn't and you must request new tokens manually.
- If you see persistent authentication errors, verify your client credentials are still valid.
