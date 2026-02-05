# Authentication module

The authentication module is a pre-built UI component you embed in your application so your end users can connect their data sources without leaving your app. Instead of building a custom credential collection flow, you integrate Airbyte's widget and let it handle connector selection, credential input, and validation.

When a user completes authentication through the module, Airbyte stores their credentials, creates a source in their workspace, and begins syncing data according to your connection templates.

## Prerequisites

Before embedding the authentication module, complete the following setup:

1. **Enable at least one connector.** The module displays only the connectors you've enabled. See [Enable a connector](../enable-connector).

2. **Get your API credentials.** You need your `client_id` and `client_secret` from the Agent Engine under **Authentication Module** > **Installation**. See [Agent Engine authentication](hosted) for details on the token system.

3. **(Optional) Create a connection template.** If you want data replication, connection templates define where your users' data lands when they authenticate a source. You can create connection templates in the Agent Engine UI under **Data Replication**, or via the [API](https://api.airbyte.ai/api/v1/docs). If you only need direct connector access (no replication), you can skip this step.

## Agent Engine UI

The **Authentication Module** page in the Agent Engine dashboard provides everything you need to get started:

- **Installation credentials**: Your `organization_id`, `client_id`, and `client_secret` are displayed under the **Installation** section. Copy these into your application's environment variables.
- **Widget preview**: Click **Preview your auth module** to see what the authentication widget looks like with your currently enabled connectors. This preview reflects the same connector selection UI your end users will see.

You'll use the `client_id` and `client_secret` from this page in your backend to generate tokens. The `organization_id` is included for reference but isn't required in the widget token request.

## Backend implementation

Your backend is responsible for securely generating widget tokens. Never expose your `client_id`, `client_secret`, or operator token in client-side code.

Here's a complete Node.js example:

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

    const response = await fetch(`${AIRBYTE_API}/embedded/widget-token`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${operatorToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        workspace_name: userId, // creates or reuses a workspace for this user
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

## Frontend implementation

### Using the npm package

The recommended approach is to install the widget as an npm package:

```bash npm2yarn
npm install @airbyte-embedded/airbyte-embedded-widget
```

```tsx title="ConnectData.tsx"
import { AirbyteEmbeddedWidget } from "@airbyte-embedded/airbyte-embedded-widget";

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

### Using a CDN script

Alternatively, load the widget from a CDN. Pin to a specific version to avoid unexpected changes:

```html
<script src="https://cdn.jsdelivr.net/npm/@airbyte-embedded/airbyte-embedded-widget@0.4.2"></script>
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

### Versioning

Pin your widget version to avoid unexpected changes:

- **npm**: Use a caret range in `package.json` to pin to a minor version: `"@airbyte-embedded/airbyte-embedded-widget": "^0.4.2"`
- **CDN**: Specify the exact version in the script URL

## Event callbacks

Pass an `onEvent` callback to receive notifications when users complete actions in the widget.

### Success events

```typescript
{
  type: "end_user_action_result",
  message: "source_created" | "source_updated",
  data: SourceRead
}
```

### Error events

```typescript
{
  type: "end_user_action_result",
  message: "source_create_error" | "source_update_error",
  error: Error
}
```

Use these events to trigger actions in your app, such as showing a confirmation message, updating your UI, or logging the event.

```tsx title="Example: handle events"
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

When a user authenticates through the module:

1. Airbyte validates the user's credentials against the data source.
2. Airbyte creates a source in the user's workspace. If a workspace with the given `workspace_name` already exists, Airbyte reuses it.
3. If you configured connection templates, Airbyte applies them automatically — creating connections between the source and your configured destinations, and syncing data on the schedule you defined.

You can then [execute operations](../execute) against the user's connector to query their data in your AI agent.

## Sample applications

The [embedded-demoapp](https://github.com/airbytehq/embedded-demoapp) repository contains complete working examples in three frameworks:

- **Vanilla JS** with Express server
- **React** with Vite
- **Next.js**

All examples share a common Express backend that handles token generation. To run them:

```bash
git clone https://github.com/airbytehq/embedded-demoapp.git
cd embedded-demoapp
npm install

cd apps/server
cp .env.example .env
# Add your credentials to .env

cd ../..
npm run dev
```

This starts all apps simultaneously: the server at `http://localhost:3000`, Next.js at `http://localhost:3001`, and React at `http://localhost:3002`.

## Filtering available connectors

By default, the authentication module displays all connectors you've enabled. To show only specific connectors to specific users, you can filter using tags on your source and connection templates.

Pass tag parameters when generating the widget token:

```bash
curl -X POST https://api.airbyte.ai/api/v1/embedded/widget-token \
  -H 'Authorization: Bearer <operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "workspace_name": "user_123",
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

You can manage tags through the Agent Engine UI or the [API](https://api.airbyte.ai/api/v1/docs).
