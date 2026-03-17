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

The Agent Engine uses a hierarchical token system with three token types: application tokens for organization-level access, scoped tokens for workspace-level end-user operations, and widget tokens for embedding the authentication module with CORS protection.

For complete details on each token type, how to generate them, and security considerations, see [Token types](/ai-agents/api/#token-types) in the API documentation.

## Authentication flow

The typical authentication flow for hosted mode involves these steps:

1. **Get an application token** using your Airbyte credentials.

2. **Generate a Scoped Token** for the customer.

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
    "customer_name": "<your_customer_name>",
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
    "customer_name": "<your_customer_name>",
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

You can build your own OAuth flow and use Airbyte's server-side OAuth endpoints to handle the token exchange. This allows you to show your own branding on the OAuth consent screen. See [Build your own OAuth flow](build-auth/build-your-own.md) for details.

## Security considerations

When using hosted authentication, follow these best practices:

- **Never expose tokens in client-side code**. Only use tokens in your backend and ensure you frontend calls the backend instead of the API's authentication endpoints.

- **Handle token expiration**. Application tokens expire after 15 minutes and scoped tokens expire after 20 minutes. The Python SDK handles token refresh automatically, but if you use the API, you must request new tokens manually.

- **Validate the `allowed_origin`** when using widget tokens to ensure requests can only come from your application.

## When to use hosted mode

Hosted authentication is most appropriate when:

- You're building a production application with multiple end-users.
- You want centralized credential management without storing credentials yourself.
- You need Airbyte to handle credential lifecycle management, including token refresh.
- Security and compliance are priorities for your application.

For development, testing, or single-user scenarios, you might find it easier to use [open source authentication](open-source.md).
