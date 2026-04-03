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

To remove a connector, click the trash icon next to it on the **Existing Connectors** tab. This removes the source template and prevents end users from creating new connections with that connector type.

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

```

```bash title="Response"

```

Each definition includes a `sourceDefinitionId` that you use when creating source templates.

### Create a new connector

To create a connector for your organization, create a source template.

```bash title="Request"

```

```bash title="Response"

```

## Next steps

After enabling connectors, set up [authentication](authenticate) to let users connect their accounts.
