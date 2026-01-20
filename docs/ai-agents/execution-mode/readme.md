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

1. Airbyte Cloud account

2. Airbyte credentials

   - Client ID
   - Client Secret

3. The third-party API credentials you want to use (for example, a GitHub personal access token)

4. Python 3.11 or later

5. An installed agent connector package. For example:

   ```bash
   uv pip install airbyte-ai-github
   ```

   See [Connectors](../connectors) for a full list of connectors.

## Authentication

Before running operations in hosted mode, you must create a connector in Airbyte Cloud. This stores your API credentials securely and associates them with a workspace.

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

<!-- In E2E testing, Devin expressed a great deal of confusion about what this was. I am also confused. I think this creates a new workspace, because it returns a random workspace ID. But I can't find the workspace in the org. I don't know why we're doing this. Presumably this allows customer to run connector operations in their own specific workspace? -->

## Create a connector

Create a connector with your API credentials. Airbyte stores these credentials securely in Airbyte Cloud.

You'll need:

- **source_template_id**: The ID of the source template for the connector type. List available templates by calling `GET /api/v1/integrations/templates/sources` with your scoped token.
- **workspace_id**: Your workspace ID. Retrieve it by calling `GET /api/v1/embedded/scoped-token/info` with your scoped token.

```bash
curl -X POST "https://api.airbyte.ai/api/v1/embedded/sources" \
    -H "Authorization: Bearer <scoped_token>" \
    -H "Content-Type: application/json" \
    -d '{
      "source_template_id": "<source_template_id>",
      "workspace_id": "<workspace_id>",
      "name": "...",
      "auth_config": {
         ...
      },
      "source_config": {
         ...
      }
    }'
```

Note the returned connector ID for reference.

<!-- Devin and I both experienced failure at this step. The operation of the auth_config and source_config fields is completely ambiguous. There is no way to know what fields are required, what the schema is, or how to discover it (as far as I can tell). -->

## Run operations in hosted mode

Once you create your connector, you can use the connector in hosted mode.

<Tabs>
<TabItem value="python" label="Python" default>

Instead of providing API credentials directly, provide your Airbyte Cloud credentials and the connector ID:

```python
from airbyte_ai_github import GithubConnector

connector = GithubConnector(
    connector_id="<your_connector_id>",
    airbyte_client_id="<your_client_id>",
    airbyte_client_secret="<your_client_secret>",
)

# Execute connector operations
issues = await connector.issues.list(owner="airbytehq", repo="airbyte")
```

Once initialized, the connector works the same way as in local mode. The SDK handles the token exchange (application token → scoped token) automatically, so you don't need to manage tokens manually.

<!-- Devin struggled with this. It was not successful with external_user_id. I think the workspace name you chose earlier for the scoped token is the external_user_id, at least that's the intent, but that doesn't seem to be the actual field the connector uses  -->

<!-- Devin was never actually able to run this. It seems this still doesn't work. The HostedExecutor is configured to use `http://localhost:8001` instead of the Airbyte Cloud API. This means Python hosted mode DOES NOT WORK out of the box. The SDK needs to be configured with the correct API URL. The SDK is using wrong URL path: `/connectors/{id}/execute`. The correct path (per API docs) should be: `/api/v1/connectors/sources/{id}/execute`. Python SDK hosted mode is broken, but Devin believes the documentation shows the correct API paths. -->

</TabItem>
<TabItem value="api" label="API">

You can execute connector operations directly via the REST API.

First, retrieve your connector ID using your external user ID and connector definition ID:

```bash title="Request"
curl --location 'https://api.airbyte.ai/api/v1/connectors/connectors_for_user?external_user_id=<your_workspace_name>&definition_id=ef69ef6e-aa7f-4af1-a01d-ef775033524e' \
  --header 'Authorization: Bearer <APPLICATION_TOKEN>'
```

The response contains your connector ID:

```json title="Response"
{
  "connectors": [
    {
      "id": "<connector_id>",
      "name": "github-connector"
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
    "entity": "issues",
    "action": "list",
    "params": {
      "owner": "airbytehq",
      "repo": "airbyte"
    }
  }'
```

<!-- - The execute endpoint returns: "Unable to map source configuration to any supported auth scheme"
- This suggests the credentials weren't stored correctly when creating the connector
- The connector was created successfully (ID: 017a8b18-c1ad-4128-9a09-8944c1597267)
- But the execute endpoint can't find the auth credentials
- **POSSIBLE ISSUE**: The `source_config` structure I used may not have stored credentials correctly -->

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
- Verify the `external_user_id` matches the `workspace_name` used during setup.

### Authentication errors (401/403)

- Check that your Airbyte client ID and secret are correct.
- Verify your application token hasn't expired.
- Ensure the connector was created with valid API credentials.

### Token expiration

- Application tokens expire after ~15 minutes.
- The SDK handles token refresh automatically during normal operation.
- If you see persistent auth errors, verify your client credentials are still valid.
