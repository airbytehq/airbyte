---
sidebar_position: 1
---

# Authentication

When you subscribe to the Airbyte Agents, you authenticate with Airbyte Cloud using your Airbyte client credentials, and Airbyte manages your end users' credentials securely. This approach is ideal for production B2B applications where you need centralized credential management across multiple customers. When your agent executes operations, your app proxies API calls through Airbyte Cloud.

- You authenticate using Airbyte Cloud client credentials.
- You store end-user API credentials securely in Airbyte Cloud.
- API calls are proxied through Airbyte Cloud.
- Airbyte handles credential lifecycle management, including token refresh.

If you're building a Python app, the [SDK](../../sdk/authenticate) handles token refresh and most of these concerns for you.

## Token types

The Airbyte Agent API uses a hierarchical token system. Each token type has a different scope and is designed for specific use cases.

| Token type        | Use case                                                                                     | Scope                                |
| ----------------- | -------------------------------------------------------------------------------------------- | ------------------------------------ |
| Application token | Organization management, generating scoped and widget tokens, executing connector operations | Organization-wide                    |
| Scoped token      | Company-level administration                                                                 | Single workspace                     |
| Widget token      | Embedding the authentication module in your app                                              | Single workspace with CORS protection |

### Application token

The application token provides organization-level access. Use it for administrative operations like managing connectors, listing workspaces, and generating other tokens lower in the hierarchy. Most API endpoints require an application token.

To obtain an application token, send your app credentials to the token endpoint. Find your credentials in the Airbyte Agents under **Authentication Module** > **Installation**.

```bash title="Request"
curl -X POST https://api.airbyte.ai/api/v1/account/applications/token \
  -H 'Content-Type: application/json' \
  -d '{
    "client_id": "<your_client_id>",
    "client_secret": "<your_client_secret>"
  }'
```

The response contains your application token:

```json title="Response"
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "organization_id": "12345678-1234-1234-1234-123456789012"
}
```

Application tokens expire after 15 minutes. Request a new token when needed.

### Scoped token

Scoped tokens provide workspace-level access for some end-user operations. Each scoped token is limited to a single workspace, ensuring data isolation between workspaces. Generate a scoped token using your application token:

```bash title="Request"
curl -X POST https://api.airbyte.ai/api/v1/account/applications/scoped-token \
  -H 'Authorization: Bearer <your_application_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "workspace_name": "workspace_123"
  }'
```

If the workspace doesn't exist, Airbyte creates it automatically. Scoped tokens expire after 20 minutes.

### Widget token

Widget tokens are specialized tokens used by the embeddable authentication module. They include all features of scoped tokens plus origin validation for CORS protection.

```bash title="Request"
curl -X POST https://api.airbyte.ai/api/v1/account/applications/widget-token \
  -H 'Authorization: Bearer <your_application_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "workspace_name": "workspace_123",
    "allowed_origin": "https://yourapp.com"
  }'
```

## Authentication flow

A typical flow for authenticating an end user and executing an operation looks like this:

1. **Get an application token** using your Airbyte client credentials.

2. **Generate a scoped token** for the end user's workspace.

3. **Create a connector** using the end user's API credentials. Airbyte stores these credentials securely. See [Add a connector](../add-connector).

4. **Execute operations** against the connector using your application token. See [Execute operations](../execute).

## Creating connectors with credentials

Once you have a scoped token, create a connector to store your end user's credentials. The shape of the `credentials` object varies by connector and by authentication method. See the [Connectors](../../../connectors) reference for exact field names.

### With API tokens

For connectors that authenticate with an API token or personal access token:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <scoped_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_name": "<your_workspace_name>",
    "connector_type": "github",
    "name": "My GitHub Connector",
    "credentials": {
      "token": "<user_github_personal_access_token>"
    }
  }'
```

### With OAuth credentials

For connectors that authenticate with OAuth, pass the end user's `client_id`, `client_secret`, and `refresh_token`. Airbyte uses the refresh token to mint and rotate access tokens automatically at execution time.

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <scoped_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_name": "<your_workspace_name>",
    "connector_type": "hubspot",
    "name": "My HubSpot Connector",
    "credentials": {
      "client_id": "<hubspot_client_id>",
      "client_secret": "<hubspot_client_secret>",
      "refresh_token": "<hubspot_refresh_token>"
    }
  }'
```

### With your own OAuth flow

You can build your own OAuth flow and use Airbyte's server-side OAuth endpoints to handle the token exchange. This allows you to show your own branding on the OAuth consent screen. See [Build your own OAuth flow](./build-your-own) for details.

## Security considerations

When using hosted authentication, follow these best practices:

- **Never expose tokens in client-side code.** These tokens provide organization-wide or workspace-level access and should only be used in your backend. Ensure your frontend calls your backend instead of the API's authentication endpoints directly.

- **Handle token expiration.** Application tokens expire after 15 minutes and scoped tokens expire after 20 minutes. The Python SDK handles token refresh automatically, but API users must request new tokens when the current token expires.

- **Validate the `allowed_origin`** when using widget tokens to ensure requests only come from your app.
