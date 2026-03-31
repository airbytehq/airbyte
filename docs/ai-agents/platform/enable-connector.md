---
sidebar_position: 1
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Enable a connector

Agent Engine uses a three-layer model for connectors:

- **Definition**: A connector type available in the Airbyte catalog, like GitHub or Salesforce. Each definition has a `sourceDefinitionId`. List definitions with `GET /api/v1/integrations/definitions/sources`.
- **Source template**: An organization-level configuration for a connector type, including default settings and connector mode. Managed through `GET/POST/PATCH/DELETE /api/v1/integrations/templates/sources`.
- **Connector**: A per-user instance with actual credentials, created when an end user authenticates. Managed through `/api/v1/integrations/connectors`.

Many connectors work out of the box using Airbyte's standard (global) templates. When you create a connector with `POST /api/v1/integrations/connectors`, the system automatically resolves the appropriate template. You only need to explicitly enable a connector by creating an org-specific source template when you want to:

- Override default configuration values for your organization
- Set a specific [connector mode](#connector-modes), like switching from Replication to Direct
- Restrict or customize which connectors are available to your end users

## Connector modes

Agent Engine connectors operate in one of three modes:

- **Direct** (`DIRECT`): AI agents execute real-time queries against connected data sources. When a user asks a question, the agent calls the third-party API directly to fetch fresh data. This mode is ideal for operational queries, real-time lookups, and actions that need current information.

- **Replication** (`REPLICATION`): Data syncs from connected sources to object storage like S3, GCS, or Azure Blob Storage. This mode is useful for analytics, RAG pipelines, and scenarios where you need to process large volumes of historical data.

- **Multi** (`MULTI`): Both Direct and Replication modes are active. Agents can query the API in real time and data also syncs to object storage.

Some connectors support all three modes, while others support only one. If you don't specify a mode when creating a source template, it defaults to `REPLICATION`.

## With the UI

### Enable a new connector

Enable a connector through the Agent Engine dashboard.

1. Click **Connectors**.

2. Click **Manage Connectors** (or **Enable Connector** if you haven't enabled any connectors yet).

3. In the slide-out panel, the **Add Connector** tab displays available connectors. Browse or search for the connector you want to enable, and click it to enable it.

   The system automatically determines the connector mode based on the connector's capabilities and your organization's configuration.

4. Click **Done**.

The connector appears in your active connectors list. Your end users can now authenticate with this connector.

![Managing connectors in the user interface](img/managing-connectors.png)

### Update connector modes

To modify the modes of connectors you've already enabled:

1. Click **Connectors** > **Manage Connectors**.

2. Click the **Existing Connectors** tab.

3. For each connector, you can:

   - Toggle Direct mode on or off

   - Toggle Replication mode on or off, if data replication is configured

At least one mode must remain enabled for each active connector.

### Remove a connector

To remove a connector, click the trash icon next to it on the **Existing Connectors** tab. This removes the source template and prevents end users from creating new connections with that connector type.

## With the API

You can also manage connectors programmatically using the Agent Engine API. This approach is useful for automation, infrastructure-as-code workflows, or when building custom admin interfaces.

### Get an application token

Request an application token using your Airbyte client credentials.

```bash title="Request"
curl --location 'https://api.airbyte.ai/api/v1/account/applications/token' \
  --header 'Content-Type: application/json' \
  --data '{
    "client_id": "<your_client_id>",
    "client_secret": "<your_client_secret>"
  }'
```

Save the returned access token for subsequent API calls.

### List available connector definitions

To see which connector types are available in the Airbyte catalog:

```bash title="Request"
curl 'https://api.airbyte.ai/api/v1/integrations/definitions/sources' \
  --header 'Authorization: Bearer <APPLICATION_TOKEN>'
```

Each definition includes a `sourceDefinitionId` that you use when creating source templates.

### List source templates

To see which connectors have source templates for your organization:

```bash title="Request"
curl 'https://api.airbyte.ai/api/v1/integrations/templates/sources' \
  --header 'Authorization: Bearer <APPLICATION_TOKEN>'
```

By default, this returns your organization's source templates. To list Airbyte's standard global templates instead, add `?use_global=true`.

### Create a source template

To customize a connector for your organization, create a source template.

```bash title="Request"
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/templates/sources' \
  --header 'Authorization: Bearer <APPLICATION_TOKEN>' \
  --header 'Content-Type: application/json' \
  --data '{
    "actor_definition_id": "<connector_definition_id>",
    "partial_default_config": {},
    "mode": "DIRECT"
  }'
```

| Field | Required | Description |
| --- | --- | --- |
| `actor_definition_id` | Yes | The connector type identifier. This corresponds to the `sourceDefinitionId` returned by the [definitions endpoint](/ai-agents/api/#make-your-first-request). You can also find these IDs in the [Airbyte Connector Registry](https://connectors.airbyte.com/files/registries/v0/cloud_registry.json). |
| `partial_default_config` | Yes | Default configuration values for the connector, so your users don't need to provide them during authentication. Pass `{}` for no defaults. |
| `mode` | No | The connector mode: `DIRECT`, `REPLICATION`, or `MULTI`. Defaults to `REPLICATION`. |
| `name` | No | A display name for the source template. |

### Update a source template

To modify an existing source template:

```bash title="Request"
curl -X PATCH 'https://api.airbyte.ai/api/v1/integrations/templates/sources/<template_id>' \
  --header 'Authorization: Bearer <APPLICATION_TOKEN>' \
  --header 'Content-Type: application/json' \
  --data '{
    "partial_default_config": {
      "some_field": "new_default_value"
    }
  }'
```

By default, updates apply only to the source template itself. Existing connectors created from this template are not modified. To propagate default config changes to existing connectors, include `"propagate": true` in the request body.

### Delete a source template

To delete a source template and prevent end users from creating new connections with this connector type:

```bash title="Request"
curl -X DELETE 'https://api.airbyte.ai/api/v1/integrations/templates/sources/<template_id>' \
  --header 'Authorization: Bearer <APPLICATION_TOKEN>'
```

## Next steps

After enabling connectors, set up [authentication](authenticate) to let users connect their accounts.
