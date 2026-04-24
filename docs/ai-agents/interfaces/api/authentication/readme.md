---
sidebar_position: 1
---

# Authenticate

You authenticate with the Airbyte Agent API using your Airbyte Agents client credentials. Airbyte stores the credentials for each connector securely and mints short-lived tokens for your backend to call.

- You authenticate using Airbyte Agents client credentials.
- Airbyte stores connector credentials securely and handles refresh for you.
- API calls are proxied through Airbyte Agents.

If you're building a Python app, the [SDK](../../sdk/authenticate) handles token refresh and most of these concerns for you.

## Token types

The Airbyte Agent API uses a hierarchical token system. Each token type has a different scope and is designed for specific use cases.

| Token type        | Use case                                                                                     | Scope                                |
| ----------------- | -------------------------------------------------------------------------------------------- | ------------------------------------ |
| Application token | Organization management, generating scoped and widget tokens, executing connector operations | Organization-wide                    |
| Scoped token      | Workspace-scoped access                                                                      | Single workspace                     |
| Widget token      | Embedding the authentication module in your app                                              | Single workspace with CORS protection |

### Application token

The application token provides organization-level access. Use it for administrative operations like managing connectors, listing workspaces, and generating other tokens lower in the hierarchy. Most API endpoints require an application token.

To obtain an application token, send your app credentials to the token endpoint. Copy your `AIRBYTE_CLIENT_ID` and `AIRBYTE_CLIENT_SECRET` from the [Profile page](https://app.airbyte.ai/profile) in the Airbyte Agents app.

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

Application tokens are short-lived — `expires_in` is 900 seconds (15 minutes) by design, because they carry organization-wide privileges. Request a new token when yours expires. [Scoped tokens](#scoped-token) and [widget tokens](#widget-token) live longer (20 minutes) because they're already limited to a single workspace and their exposure is lower. If you're building a long-running app, cache the current token and refresh it just before `expires_in` elapses.

### Scoped token

Scoped tokens are limited to a single [workspace](../workspaces). Most apps use the `default` workspace and can skip this token type; generate a scoped token only when you need to isolate credentials across tenants or teams. Generate a scoped token using your application token:

```bash title="Request"
curl -X POST https://api.airbyte.ai/api/v1/account/applications/scoped-token \
  -H 'Authorization: Bearer <your_application_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "workspace_name": "default"
  }'
```

The response carries the scoped token as a single `token` field:

```json title="Response"
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

If the workspace doesn't exist, Airbyte creates it automatically. Scoped tokens expire after 20 minutes.

### Widget token

Widget tokens are specialized tokens used by the embeddable authentication module. They include all features of scoped tokens plus origin validation for CORS protection.

```bash title="Request"
curl -X POST https://api.airbyte.ai/api/v1/account/applications/widget-token \
  -H 'Authorization: Bearer <your_application_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "workspace_name": "default",
    "allowed_origin": "https://yourapp.com"
  }'
```

The widget token response also has a `token` field. The value is a JWT that wraps both a scoped token and the widget URL. The embedded authentication widget decodes this itself — your backend just forwards the `token` string to the frontend.

```json title="Response"
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## Authentication flow

A typical flow for getting connected and executing an operation looks like this:

1. **Get an application token** using your Airbyte client credentials.

2. **Create a connector** for the third-party service you want to access. Airbyte stores the credentials securely. See [Add a connector](../add-connector).

3. **Execute operations** against the connector using your application token. See [Execute operations](../execute).

## Security considerations

When using hosted authentication, follow these best practices:

- **Never expose tokens in client-side code.** These tokens provide organization-wide or workspace-level access and should only be used in your backend. Ensure your frontend calls your backend instead of the API's authentication endpoints directly.

- **Handle token expiration.** Application tokens expire after 15 minutes and scoped tokens expire after 20 minutes. The Python SDK handles token refresh automatically, but API users must request new tokens when the current token expires.

- **Validate the `allowed_origin`** when using widget tokens to ensure requests only come from your app.
