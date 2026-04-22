---
sidebar_position: 3
---

import SdkVsApi from '@site/static/_ai-agents-sdk-vs-api.md';

# API

The Airbyte Agent API lets you manage connectors, credentials, and data operations programmatically over HTTP. Use it to integrate Airbyte Agents into any language or framework, or to build custom backend services that interact with third-party data sources.

This section walks through the four operations most apps need: authenticate, add a connector, execute operations, and manage workspaces. Deeper endpoint details (every parameter, response schema, and error code) live in the [API reference](/ai-agents/reference/api).

## Choose your interface

<SdkVsApi />

## Base URL

All API requests use the base URL `https://api.airbyte.ai`.

If your account belongs to multiple organizations, include the `X-Organization-Id` header in every request to specify which organization you're targeting. If you belong to a single organization, this header is optional.

## How the pieces fit together

The four pages in this section are designed to map one-to-one with the [SDK](../sdk) section so the same mental model works in either environment.

1. **[Authentication](./authentication)**: Get an application token (and, when needed, scoped and widget tokens). This is how every subsequent call is authorized.

2. **[Add a connector](./add-connector)**: Create a connector from a `definition_id` plus the credentials for the third-party service. For connectors that support OAuth with your own branding, see [Build your own OAuth flow](./authentication/build-your-own).

3. **[Execute operations](./execute)**: Call `POST /integrations/connectors/<connector_id>/execute` to read from or take action on the connected service.

4. **[Manage workspaces](./workspaces)**: Administer workspaces (list, update, delete) — operations the SDK defers to the API. Most apps use the `default` workspace and don't need this page.

## End-to-end example

This snippet authenticates, creates a connector, and executes a single operation. It parallels the [SDK end-to-end example](../sdk).

```bash title="1. Get an application token"
curl -X POST https://api.airbyte.ai/api/v1/account/applications/token \
  -H 'Content-Type: application/json' \
  -d '{
    "client_id": "<your_client_id>",
    "client_secret": "<your_client_secret>"
  }'
```

```bash title="2. Create a connector"
curl -X POST https://api.airbyte.ai/api/v1/integrations/connectors \
  -H 'Authorization: Bearer <application_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "customer_name": "default",
    "definition_id": "<hubspot_definition_id>",
    "name": "My HubSpot Connector",
    "credentials": {
      "client_id": "<hubspot_client_id>",
      "client_secret": "<hubspot_client_secret>",
      "refresh_token": "<hubspot_refresh_token>"
    }
  }'
```

```bash title="3. Execute an operation"
curl -X POST https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>/execute \
  -H 'Authorization: Bearer <application_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "entity": "contacts",
    "action": "list",
    "params": { "limit": 10 }
  }'
```

## Make your first request

A good zero-setup starting point is listing the available source connector definitions. This read-only endpoint returns the catalog of connectors available in Airbyte Agents, so it returns data even if you haven't configured anything yet.

```bash title="Request"
curl https://api.airbyte.ai/api/v1/integrations/definitions/sources \
  -H 'Authorization: Bearer <application_token>'
```

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
  -H 'Authorization: Bearer <application_token>'
```

## Use the API

import DocCardList from '@theme/DocCardList';

<DocCardList />
