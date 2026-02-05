---
sidebar_position: 1
---

# Agent Engine authentication

When you subscribe to the Agent Engine, you authenticate with Airbyte Cloud using your Airbyte credentials, and Airbyte manages your end-users' credentials securely. This approach is ideal for production B2B applications where you need centralized credential management across multiple customers. When your agent executes operations, your proxy API calls through Airbyte Cloud.

- You authenticate using Airbyte Cloud client credentials.
- You store end-user API credentials securely in Airbyte Cloud.
- API calls are proxied through Airbyte Cloud.
- Airbyte handles credential lifecycle management, including token refresh.

## Token types

The Agent Engine uses a hierarchical token system with three types of tokens, each designed for specific use cases.

| Token type            | Use case                                                       | Scope                                 |
| --------------------- | -------------------------------------------------------------- | ------------------------------------- |
| Operator Bearer Token | Organization management, template creation                     | Organization-wide                     |
| Scoped Token          | API integration, programmatic workspace access                 | Single workspace                      |
| Widget Token          | Using the [authentication module](../authentication-module) | Single workspace with CORS protection |

### Operator bearer token

The Operator Bearer Token provides organization-level access. use it for administrative operations like generating other tokens, lower in the hierarchy. To obtain an Operator Bearer Token, use the client credentials endpoint with your application credentials. Find your credentials in the Agent Engine under **Authentication Module** > **Installation**.

```bash title="Request"
curl -X POST https://api.airbyte.ai/api/v1/account/applications/token \
  -H 'Content-Type: application/json' \
  -d '{
    "client_id": "<your_client_id>",
    "client_secret": "<your_client_secret>"
  }'
```

The response contains your Operator Bearer Token:

```json title="Response"
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "organization_id": "12345678-1234-1234-1234-123456789012"
}
```

### Scoped token

Scoped tokens provide workspace-level access for end-user operations. Each scoped token is limited to a single customer, ensuring data isolation between customers. Generate a scoped token using your Operator Bearer Token:

```bash
curl -X POST https://api.airbyte.ai/api/v1/embedded/scoped-token \
  -H 'Authorization: Bearer <your_operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "workspace_name": "customer_workspace_123"
  }'
```

If the workspace doesn't exist, Airbyte creates it automatically.

### Widget token

Widget tokens are specialized tokens for embedding the authentication module in your app. They include all features of scoped tokens plus origin validation for CORS protection.

```bash
curl -X POST https://api.airbyte.ai/api/v1/embedded/widget-token \
  -H 'Authorization: Bearer <your_operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "workspace_name": "customer_workspace_123",
    "allowed_origin": "https://yourapp.com"
  }'
```

For more details on widget tokens and template filtering, see the [Authentication Module](authentication-module) documentation.

## Authentication flow

The typical authentication flow for hosted mode involves these steps:

1. **Get an Operator Bearer Token** using your Airbyte credentials.

2. **Generate a Scoped Token** for the customer's workspace.

3. **Create a connector** using the end-user's API credentials. Airbyte stores these credentials securely.

4. **Use the connector** in your agent with your Airbyte credentials.

## Creating connectors with credentials

Once you have a scoped token, create a connector to store your end-user's credentials. The connector creation request varies by authentication method.

### With API tokens

For connectors that support token-based authentication:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <scoped_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "<your_user_identifier>",
    "connector_type": "github",
    "name": "My GitHub Connector",
    "credentials": {
      "token": "<user_github_personal_access_token>"
    }
  }'
```

### With OAuth credentials

For connectors that support OAuth:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <scoped_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "<your_user_identifier>",
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

You can build your own OAuth flow and use Airbyte's server-side OAuth endpoints to handle the token exchange. This allows you to show your own branding on the OAuth consent screen. See [Build your own OAuth flow](build-your-own.md) for details.

## Security considerations

When using hosted authentication, follow these best practices:

- **Never expose Operator Bearer Tokens in client-side code**. These tokens provide organization-wide access and should only be used in your backend.

- **Use scoped tokens for end-user operations**. Scoped tokens are limited to a single workspace and are safer to use in contexts closer to end-users.

- **Handle token expiration**. Operator Bearer Tokens expire after 15 minutes and scoped tokens expire after 20 minutes. The Python SDK handles token refresh automatically, but API users must request new tokens manually.

- **Validate the `allowed_origin`** when using widget tokens to ensure requests only come from your application.

## When to use hosted mode

Hosted authentication is most appropriate when:

- You're building a production B2B application with multiple end-users.
- You want centralized credential management without storing credentials yourself.
- You need Airbyte to handle credential lifecycle management, including token refresh.
- Security and compliance are priorities for your application.

For development, testing, or single-user scenarios, consider using [open source authentication](open-source.md) instead.
