---
products: embedded
---

# Authentication & Token Management

## Overview
Airbyte Embedded uses a two-tier authentication system:
1. **Organization-level tokens**: Your main API credentials for managing templates and connections
2. **User-scoped tokens**: Temporary tokens that allow end-users to configure sources in their isolated workspaces

## Generating User-Scoped Tokens

When collecting credentials from your users, generate a scoped access token that only has permissions to read and modify integrations in their specific workspace. This follows the principle of least privilege and ensures user data isolation.

This can be done by submitting a request to

```
curl --location 'https://api.airbyte.ai/api/v1/embedded/widget_token' \
--header 'Content-Type: application/json'\
-H 'Authorization: Bearer <token>' \
--header 'Accept: application/json' \
--data '{
  "externalUserId": "<external_user_id>", 
  "organizationId": "<organization_id>",
  "allowedOrigin": "https://api.airbyte.ai"
}'
```

Where:
- externalUserId is a unique identifier within your organization
- allowedOrigin is the origin where you're embedding the widget (used for CORS validation). It can be an arbitrary string if you're not using the Embedded Widget.

The API will return a JSON object with a token string:
```
{"token":"eyJ0b2tlbiI6ImV5SmhiR2NpT2lKSVV6STFOaUo5LmV5SmhkV1FpT2lKaGFYSmllWFJsTFhObGNuWmxjaUlzSW5OMVlpSTZJbVUyTUdRNE1XRTFMVGt6WkdZdE5HWTVZUzA0TURFekxXSmlZbVkzT1ROalpqQmhNaUlzSW1sdkxtRnBjbUo1ZEdVdVlYVjBhQzUzYjNKcmMzQmhZMlZmYzJOdmNHVWlPbnNpZDI5eWEzTndZV05sU1dRaU9pSm1ZbUU0TVRJeE9DMHpORFkzTFRRMU9EZ3RZVGhrTlMxaE9ETTVObU5rWlRaak1ETWlmU3dpWVdOMElqcDdJbk4xWWlJNkltWmtOR1kzWVdNd0xURmhaREV0TkRJME9DMWlZekZqTFRZNU1HSXdPREk0T1RVNU9TSjlMQ0p5YjJ4bGN5STZXeUpGVFVKRlJFUkZSRjlGVGtSZlZWTkZVaUpkTENKcGMzTWlPaUpvZEhSd2N6b3ZMMk5zYjNWa0xtRnBjbUo1ZEdVdVkyOXRJaXdpZEhsd0lqb2lhVzh1WVdseVlubDBaUzVoZFhSb0xtVnRZbVZrWkdWa1gzWXhJaXdpWlhod0lqb3hOelV6TXpFNE1EVXdmUS4tZ0xJYkQ2OVZ4VUpyajE2QnluSTJhMTJjTDZwU19lVlNTZGxMVGdIbTdFIiwid2lkZ2V0VXJsIjoiaHR0cHM6Ly9jbG91ZC5haXJieXRlLmNvbS9lbWJlZGRlZC13aWRnZXQ/d29ya3NwYWNlSWQ9ZmJhODEyMTgtMzQ2Ny00NTg4LWE4ZDUtYTgzOTZjZGU2YzAzJmFsbG93ZWRPcmlnaW49aHR0cHMlM0ElMkYlMkZhcGkuYWlyYnl0ZS5haSJ9"}
```

## Understanding the Token Response

The response contains:
- `token`: A JWT token scoped to the user's workspace 
- `widgetUrl`: A pre-configured URL for the Airbyte Embedded Widget

### Using with the Embedded Widget
Pass the entire response directly to the Airbyte Embedded Widget - no additional processing needed.

### Using with Custom Implementation  
If building a custom integration, base64 decode the token field to extract the scoped access token:

Here's an example decoded token:
```
{"token":"eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhaXJieXRlLXNlcnZlciIsInN1YiI6ImU2MGQ4MWE1LTkzZGYtNGY5YS04MDEzLWJiYmY3OTNjZjBhMiIsImlvLmFpcmJ5dGUuYXV0aC53b3Jrc3BhY2Vfc2NvcGUiOnsid29ya3NwYWNlSWQiOiJmYmE4MTIxOC0zNDY3LTQ1ODgtYThkNS1hODM5NmNkZTZjMDMifSwiYWN0Ijp7InN1YiI6ImZkNGY3YWMwLTFhZDEtNDI0OC1iYzFjLTY5MGIwODI4OTU5OSJ9LCJyb2xlcyI6WyJFTUJFRERFRF9FTkRfVVNFUiJdLCJpc3MiOiJodHRwczovL2Nsb3VkLmFpcmJ5dGUuY29tIiwidHlwIjoiaW8uYWlyYnl0ZS5hdXRoLmVtYmVkZGVkX3YxIiwiZXhwIjoxNzUzMzE4MDUwfQ.-gLIbD69VxUJrj16BynI2a12cL6pS_eVSSdlLTgHm7E","widgetUrl":"https://cloud.airbyte.com/embedded-widget?workspaceId=fba81218-3467-4588-a8d5-a8396cde6c03&allowedOrigin=https%3A%2F%2Fapi.airbyte.ai"}
```

You can use the value of this token string as bearer token when creating a source.

# Creating a Source

You'll need 3 pieces of information to create a source for your users:
1. Their workspace ID
2. The ID of the [Source Template](./source-templates.md) used
3. The connection configuration

Here is an example request:
```
curl 'https://api.airbyte.ai/api/v1/integrations/sources/' \
  -H 'authorization: Bearer <token>' \
  -H 'content-type: application/json' \
  --data-raw '{
  "workspace_id": "0967198e-ec7b-4c6b-b4d3-f71244cadbe9",
  "source_template_id": "7bb1bee0-a40f-46a0-83fc-d70ade5dfeb2",
  "source_config": {}
}'
```

The connection configuration should include all required fields from the connector specification, except for the ones included as default values in your source template.
You can find the full connector specification in the [Connector Registry](https://connectors.airbyte.com/files/registries/v0/cloud_registry.json).

You can find [the reference docs for creating a source here](https://api.airbyte.ai/api/v1/docs#tag/Sources/operation/create_integrations_sources).
