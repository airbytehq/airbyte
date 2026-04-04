---
sidebar_position: 1
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Add a connector

When you add a connector to a customer, that customer can use the connector to read and/or write data through your agent.

## With the UI

### Add a new connector

Enable a connector through the Agent Engine dashboard.

1. Click **Connector Credentials**.

2. Click **Add Credential**.

3. In the slide-out panel, select the customer you want to add the connector to, then search for and click the connector you want to add.

4. Click **Done**.

Your end users can now authenticate with this connector.

![Managing connectors in the user interface](img/managing-connectors.png)

### Remove a connector

To remove a connector, click the trash icon next to it on the **Existing Connectors** tab.

## With the API

You can manage connectors programmatically using the Agent Engine API. This approach is useful for automation, infrastructure-as-code workflows, or when building custom admin interfaces.

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

### List available connectors

To see which connector types are available in the Airbyte catalog:

```bash title="Request"
curl 'https://api.airbyte.ai/api/v1/integrations/definitions/sources' \
  --header 'Authorization: Bearer <APPLICATION_TOKEN>'
```

```json title="Response"
{
  "definitions": [
    {
      "sourceDefinitionId": "<uuid>",
      "name": "Hubspot",
      "iconUrl": "https://...",
      "supportLevel": "certified"
    }
  ]
}
```

| Field | Description |
| --- | --- |
| `sourceDefinitionId` | Unique identifier for this connector type. Use this as the `definition_id` when creating a connector. |
| `name` | Display name of the connector. |
| `iconUrl` | URL to the connector's icon. |
| `supportLevel` | Support tier: `certified`, `community`, or `archived`. |

You can filter by name with the `name` query parameter (case-insensitive partial match), for example `?name=hub` returns Hubspot.

### Create a new connector

To create a connector for a customer, send a POST request to the connectors endpoint. You must identify the connector type using one of `connector_type` or `definition_id`, and provide the `customer_name` to associate the connector with a specific customer.

```bash title="Request"
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors' \
  --header 'Authorization: Bearer <APPLICATION_TOKEN>' \
  --header 'Content-Type: application/json' \
  --data '{
    "connector_type": "hubspot",
    "customer_name": "<customer_name>",
    "credentials": {
      "api_key": "<api_key>"
    }
  }'
```

| Field | Required | Description |
| --- | --- | --- |
| `connector_type` | Yes (or `definition_id`) | Connector name, case-insensitive (for example, `hubspot`). Provide either `connector_type` or `definition_id` to identify the connector. |
| `definition_id` | Yes (or `connector_type`) | The `sourceDefinitionId` from the [definitions endpoint](#list-available-connectors). Provide either `connector_type` or `definition_id` to identify the connector. |
| `customer_name` | Yes | The customer to associate this connector with. |
| `credentials` | Conditional | Authentication credentials for the connector. Required unless using OAuth (`server_side_oauth_secret_id`). |
| `replication_config` | No | Configuration for data replication. For replication-mode connectors, this is the full config. For direct-mode connectors, this can contain settings like `start_date` or `lookback_window`. |
| `name` | No | A display name for the connector. |
| `server_side_oauth_secret_id` | No | OAuth secret ID from the OAuth callback. When provided, `credentials` is not required. |

```json title="Response"
{
  "id": "<connector_id>",
  "name": "Hubspot",
  "source_template": {
    "id": "<source_template_id>",
    "name": "Hubspot",
    "source_definition_id": "<uuid>",
    "mode": "DIRECT"
  },
  "replication_config": {},
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

## Next steps

After adding connectors, set up [authentication](authenticate) to let users connect their accounts.
