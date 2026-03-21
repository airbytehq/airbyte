# Authentication module

The authentication module (also known as Airbyte Embedded) is a pre-built UI component you embed in your application so your end users can connect their data sources without leaving your app. Instead of building a custom credential collection flow, you integrate Airbyte's widget and let it handle connector selection, credential input, and validation.

When a user completes authentication through the module, Airbyte stores their credentials, creates a source in their customer, and begins syncing data according to your connection templates.

## Prerequisites

Before embedding the authentication module, complete the following prerequisites.

1. [Enable](../../enable-connector) at least one connector. The module displays only the connectors you've enabled.

2. Get your API credentials. Click **Authentication Module** and find your credentials under **Installation**.

3. If you need data replication, create a destination. If you don't need data replication, you can skip this step.

## Preview the authentication module widget

You can see what your authentication widget looks like before implementing it.

1. In the Agent Engine, click **Authentication Module**.

2. Enter a sample [customer name](../../customers).

3. Click **Preview your auth module**. This is exactly what users from that customer see when adding a connector.

## Implement it into your app

Since you probably want to overlay the Authentication Module on your own app, you can configure it on your backend and frontend. Here's a basic Node.js example.

### Backend

Your backend is responsible for securely generating widget tokens. Never expose your `client_id`, `client_secret`, or tokens in client-side code.

<details>
<summary>Backend Node.js example</summary>

```javascript title="server.js"
const express = require("express");
const app = express();
app.use(express.json());

const AIRBYTE_API = "https://api.airbyte.ai/api/v1";

async function getOperatorToken() {
  const response = await fetch(`${AIRBYTE_API}/account/applications/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      client_id: process.env.AIRBYTE_CLIENT_ID,
      client_secret: process.env.AIRBYTE_CLIENT_SECRET,
    }),
  });
  if (!response.ok) {
    throw new Error(`Operator token request failed: ${response.status}`);
  }
  const data = await response.json();
  return data.access_token;
}

app.post("/api/airbyte/widget-token", async (req, res) => {
  try {
    const { userId } = req.body;
    const operatorToken = await getOperatorToken();

    const response = await fetch(`${AIRBYTE_API}/account/applications/widget-token`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${operatorToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        customer_name: userId, // creates or reuses a customer for this user
        allowed_origin: process.env.ALLOWED_ORIGIN, // must match your frontend's origin exactly (including port)
      }),
    });
    if (!response.ok) {
      throw new Error(`Widget token request failed: ${response.status}`);
    }

    const data = await response.json();
    res.json({ token: data.token });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000);
```

</details>

### Frontend

Pin your widget version to avoid unexpected changes.

- If you're using a package manager, use a caret range in `package.json` to pin to a minor version. For example, `"@airbyte-embedded/airbyte-embedded-widget": "^0.4.5"`.

- If you're using a CDN, specify the exact version in the script URL. For example, `<script src="https://cdn.jsdelivr.net/npm/@airbyte-embedded/airbyte-embedded-widget@0.4.5"></script>`.

Below are two example implementations.

<details>
<summary>Frontend option 1: package manager</summary>

Install the Authentication Module widget using your package manager.

```bash npm2yarn
npm install @airbyte-embedded/airbyte-embedded-widget
```

Then, import the widget into your frontend.

```tsx title="ConnectData.tsx"
import { AirbyteEmbeddedWidget } from "@airbyte-embedded/airbyte-embedded-widget";

async function fetchWidgetToken() {
  const response = await fetch("/api/airbyte/widget-token", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ userId: "user_123" }),
  });
  return response.json();
}

export const ConnectData: React.FC = () => {
  const handleConnect = async () => {
    const { token } = await fetchWidgetToken();

    const widget = new AirbyteEmbeddedWidget({
      token,
      onEvent: (event) => {
        if (event.message === "source_created") {
          console.log("Source created:", event.data);
        }
      },
    });

    widget.open();
  };

  return <button onClick={handleConnect}>Connect your data</button>;
};
```

</details>

<details>
<summary>Frontend option 2: CDN script</summary>

Alternatively, load the widget from jsDelivr.

```html title="your-app.html"
<script src="https://cdn.jsdelivr.net/npm/@airbyte-embedded/airbyte-embedded-widget@0.4.5"></script>
<script>
  async function connectData() {
    const response = await fetch("/api/airbyte/widget-token", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ userId: "user_123" }),
    });
    const { token } = await response.json();

    const widget = new AirbyteEmbeddedWidget({ token });
    widget.open();
  }
</script>
<button onclick="connectData()">Connect your data</button>
```

</details>

## Event callbacks

Pass an `onEvent` callback to receive notifications when users complete actions in the widget.

### Success events

```typescript title="Success event"
{
  type: "end_user_action_result",
  message: "source_created" | "source_updated",
  data: SourceRead
}
```

The `data` field contains the full source object with the following top-level properties:

| Field | Description |
|-------|-------------|
| `id` | Unique identifier for the created or updated source. |
| `name` | Display name assigned to the source (e.g., `"GitHub - <uuid>"`). |
| `source_template` | The template used to create this source, including the connector's `source_definition_id`, `user_config_spec`, and `mode` (`DIRECT` or `REPLICATION`). |
| `replication_config` | The user-supplied configuration, including credentials (redacted) and connector-specific settings such as selected repositories or accounts. |
| `created_at` | ISO 8601 timestamp of when the source was created. |
| `updated_at` | ISO 8601 timestamp of the most recent update. |

### Error events

```typescript title="Error event"
{
  type: "end_user_action_result",
  message: "source_create_error" | "source_update_error",
  error: Error
}
```

### Example event handling

Use these events to trigger actions in your app, like showing a confirmation or error message, updating your UI, or logging the event.

```tsx title="ConnectData.jsx"
const widget = new AirbyteEmbeddedWidget({
  token,
  onEvent: (event) => {
    switch (event.message) {
      case "source_created":
        showNotification("Data source connected successfully!");
        refreshConnectorList();
        break;
      case "source_create_error":
        showError("Failed to connect. Please try again.");
        break;
    }
  },
});
```

## What happens after authentication

Once a user authenticates through the Authentication module, the following happens.

- Airbyte creates that connector in that customer. If a customer with the given `customer_name` already exists, Airbyte adds the connector to the others in that customer.

- If you configured data replication, Airbyte creates a connection between this connector and your configured destination, then replicates data on the schedule you defined.

Your AI agent can now [execute operations](../../execute) against the user's connector.

<!-- ## Filtering available connectors

By default, the authentication module displays all connectors you've enabled. To show only specific connectors to specific users, you can filter using tags on your source and connection templates.

Pass tag parameters when generating the widget token:

```bash
curl -X POST https://api.airbyte.ai/api/v1/account/applications/widget-token \
  -H 'Authorization: Bearer <operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "customer_name": "user_123",
    "allowed_origin": "https://yourapp.com",
    "selected_source_template_tags": ["pro-tier"],
    "selected_source_template_tags_mode": "any",
    "selected_connection_template_tags": ["standard-sync"],
    "selected_connection_template_tags_mode": "all"
  }'
```

| Parameter | Description |
|-----------|-------------|
| `selected_source_template_tags` | Tags to filter which connectors appear in the module. |
| `selected_source_template_tags_mode` | `any` (match at least one tag) or `all` (match all tags). |
| `selected_connection_template_tags` | Tags to filter which connection templates are used. |
| `selected_connection_template_tags_mode` | `any` or `all`. |

You can manage tags through the Agent Engine UI or the [API](/ai-agents/api). -->
