---
sidebar_position: 4
---

# Agent engine API

The Agent Engine API lets you manage connectors, credentials, and data operations programmatically. Use it to integrate Airbyte's agent connectors into any language or framework, or to build custom backend services that interact with your end-users' data sources.

All API requests use the base URL `https://api.airbyte.ai`.

If your account belongs to multiple organizations, include the `X-Organization-Id` header in every request to specify which organization you're targeting. If you belong to a single organization, this header is optional.

## Token types

The Agent Engine uses a hierarchical token system. Each token type has a different scope and is designed for specific use cases.

| Token type        | Use case                                                                                     | Scope                                |
| ----------------- | -------------------------------------------------------------------------------------------- | ------------------------------------ |
| Application Token | Organization management, generating scoped and widget tokens, executing connector operations | Organization-wide                    |
| Scoped Token      | Company-level administration                                                                 | Single customer                      |
| Widget Token      | Embedding the authentication module in your app                                              | Single customer with CORS protection |

### Application token

The application token provides organization-level access. Use it for administrative operations like managing connectors, listing customers, and generating other tokens lower in the hierarchy. Most API endpoints require an application token.

To obtain an application token, send your app credentials to the token endpoint. Find your credentials in the Agent Engine under **Authentication Module** > **Installation**.

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

application tokens expire after 15 minutes. Request a new token when needed.

### Scoped token

Scoped tokens provide customer-level access for some end-user operations. Each scoped token is limited to a single customer, ensuring data isolation between customers. Generate a scoped token using your application token:

```bash title="Request"
curl -X POST https://api.airbyte.ai/api/v1/account/applications/scoped-token \
  -H 'Authorization: Bearer <your_operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "customer_name": "customer_workspace_123"
  }'
```

If the customer doesn't exist, Airbyte creates it automatically. Scoped tokens expire after 20 minutes.

### Widget token

Widget tokens are specialized tokens for embedding the [authentication module](/ai-agents/platform/authenticate/build-auth/authentication-module) in your app. They include all features of scoped tokens plus origin validation for CORS protection.

```bash title="Request"
curl -X POST https://api.airbyte.ai/api/v1/account/applications/widget-token \
  -H 'Authorization: Bearer <your_operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "customer_name": "customer_workspace_123",
    "allowed_origin": "https://yourapp.com"
  }'
```

For more details on widget tokens and template filtering, see the [authentication module](/ai-agents/platform/authenticate/build-auth/authentication-module) documentation.

### Security considerations

- **Never expose tokens in client-side code.** These tokens provide organization-wide access and should only be used in your backend.

- **Handle token expiration.** Application tokens expire after 15 minutes and scoped tokens expire after 20 minutes. The Python SDK handles token refresh automatically, but API users must request new tokens when the current token expires.

- **Validate the `allowed_origin`** when using widget tokens to ensure requests only come from your app.

## Make your first request

After you obtain an application token, you can make your first API call. A good starting point is to list the available source connector definitions. This read-only endpoint returns the catalog of connectors available in Agent Engine, so it returns data even if you haven't configured anything yet.

```bash title="Request"
curl https://api.airbyte.ai/api/v1/integrations/definitions/sources \
  -H 'Authorization: Bearer <your_operator_token>'
```

The response contains a list of available source connectors:

```json title="Response"
{
  "definitions": [
    {
      "sourceDefinitionId": "acd81c8-0aeb-4e29-955d-a4a25d550401",
      "name": "GitHub",
      "iconUrl": "https://connectors.airbyte.com/files/metadata/airbyte/source-github/latest/icon.svg",
      "supportLevel": "certified"
    },
    {
      "sourceDefinitionId": "b117307c-14b6-41aa-9571-75e6871e6d44",
      "name": "Salesforce",
      "iconUrl": "https://connectors.airbyte.com/files/metadata/airbyte/source-salesforce/latest/icon.svg",
      "supportLevel": "certified"
    }
  ]
}
```

You can filter results by name using the `name` query parameter:

```bash title="Request"
curl 'https://api.airbyte.ai/api/v1/integrations/definitions/sources?name=github' \
  -H 'Authorization: Bearer <your_operator_token>'
```

## Full API reference

For the complete list of endpoints, request and response schemas, and authentication requirements, see the Agent Engine API reference in the sidebar.
