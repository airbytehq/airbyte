---
sidebar_position: 1
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Enable a connector

Before your AI agents can interact with external data sources, you need to enable connectors in the Agent Engine. Enabling a connector makes it available for your end users to authenticate and use with their own credentials.

## What enabling a connector does

When you enable a connector in Agent Engine, you're configuring which data sources your application supports. This is separate from authentication, which happens when individual users connect their accounts.

Enabling a connector does the following:

- Makes the connector available in your organization's connector catalog
- Allows your end users to authenticate with their own credentials for that data source
- Configures which modes the connector operates in (Direct mode, Replication mode, or both)

## Connector modes

Agent Engine connectors can operate in two modes:

**Direct mode** allows AI agents to execute real-time queries against connected data sources. When a user asks a question, the agent calls the third-party API directly to fetch fresh data. This mode is ideal for operational queries, real-time lookups, and actions that need current information.

**Replication mode** syncs data from connected sources to object storage (such as S3, GCS, or Azure Blob Storage). This mode is useful for analytics, RAG pipelines, and scenarios where you need to process large volumes of historical data.

Some connectors support both modes, while others support only one. When enabling a connector, you can choose which modes to activate based on your application's needs.

## Enable a connector in the UI

To enable a connector through the Agent Engine dashboard:

1. Navigate to the **Connectors** page in the Agent Engine dashboard.

2. Click **Manage Connectors** (or **Enable Connector** if you haven't enabled any connectors yet).

3. In the slide-out panel, browse or search for the connector you want to enable.

4. Select the modes you want to enable for the connector:
   - Check **Direct** to enable real-time agent queries
   - Check **Replication** to enable data syncing (requires a configured destination)

5. Click the connector card to enable it.

The connector now appears in your active connectors list. Your end users can authenticate with this connector using the [authentication module](/ai-agents/platform/authenticate/authentication-module) or the API.

### Manage existing connectors

To modify or remove connectors you've already enabled:

1. Navigate to the **Connectors** page.

2. Click **Manage Connectors**.

3. Select the **Existing Connectors** tab.

4. For each connector, you can:
   - Toggle Direct mode on or off
   - Toggle Replication mode on or off (if a destination is configured)
   - Remove the connector entirely by clicking the trash icon

At least one mode must remain enabled for each active connector.

## Enable a connector with the API

You can also enable connectors programmatically using the Agent Engine API. This approach is useful for automation, infrastructure-as-code workflows, or when building custom admin interfaces.

### Prerequisites

Before enabling connectors via the API, you need:

1. An Airbyte Cloud account with Agent Engine access
2. API credentials (Client ID and Client Secret) from your Airbyte Cloud dashboard under **Settings > Applications**
3. An application token for authentication

### Get an application token

Request an application token using your Airbyte client credentials:

```bash
curl --location 'https://cloud.airbyte.com/api/v1/applications/token' \
  --header 'Content-Type: application/json' \
  --data '{
    "client_id": "<your_client_id>",
    "client_secret": "<your_client_secret>"
  }'
```

Save the returned token for subsequent API calls.

### Create a source template

Enabling a connector via the API means creating a source template. Source templates control which connectors appear in your application and how they're configured.

```bash
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/templates/sources' \
  --header 'Authorization: Bearer <APPLICATION_TOKEN>' \
  --header 'Content-Type: application/json' \
  --data '{
    "organization_id": "<your_organization_id>",
    "actor_definition_id": "<connector_definition_id>",
    "partial_default_config": {}
  }'
```

The `actor_definition_id` identifies the specific connector type. You can find connector definition IDs in the [Airbyte Connector Registry](https://connectors.airbyte.com/files/registries/v0/cloud_registry.json).

The `partial_default_config` object lets you pre-configure default values for the connector, so your users don't need to provide them during authentication.

### List available source templates

To see which connectors are enabled for your organization:

```bash
curl 'https://api.airbyte.ai/api/v1/integrations/templates/sources' \
  --header 'Authorization: Bearer <APPLICATION_TOKEN>'
```

This returns both templates you've created and standard templates available to all Agent Engine users.

### Update a source template

To modify an existing source template:

```bash
curl -X PATCH 'https://api.airbyte.ai/api/v1/integrations/templates/sources/<template_id>' \
  --header 'Authorization: Bearer <APPLICATION_TOKEN>' \
  --header 'Content-Type: application/json' \
  --data '{
    "partial_default_config": {
      "some_field": "new_default_value"
    }
  }'
```

When you update a source template, all existing sources created from it are also updated.

### Delete a source template

To disable a connector by removing its template:

```bash
curl -X DELETE 'https://api.airbyte.ai/api/v1/integrations/templates/sources/<template_id>' \
  --header 'Authorization: Bearer <APPLICATION_TOKEN>'
```

Sources created from a deleted template will no longer appear in the authentication widget.

## Organize connectors with tags

You can use tags to organize and filter your enabled connectors. This is useful when you have different connector sets for different user tiers or use cases.

### Add tags when creating a template

```bash
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/templates/sources' \
  --header 'Authorization: Bearer <APPLICATION_TOKEN>' \
  --header 'Content-Type: application/json' \
  --data '{
    "organization_id": "<your_organization_id>",
    "actor_definition_id": "<connector_definition_id>",
    "partial_default_config": {},
    "tags": ["crm", "pro-tier"]
  }'
```

### Filter templates by tags

```bash
curl 'https://api.airbyte.ai/api/v1/integrations/templates/sources?tags=crm&tags=sales&tags_mode=any' \
  --header 'Authorization: Bearer <APPLICATION_TOKEN>'
```

Use `tags_mode=any` to match templates with at least one of the specified tags, or `tags_mode=all` to match only templates with all specified tags.

For more information on tag management, see [Template Tags](/ai-agents/embedded/api/tags).

## Next steps

After enabling connectors, you can:

- Set up the [authentication module](/ai-agents/platform/authenticate/authentication-module) to let users connect their accounts
- Configure [data replication](/ai-agents/platform/data-replication) to sync data to your storage
- Enable the [entity cache](/ai-agents/platform/entity-cache) to optimize agent search performance
