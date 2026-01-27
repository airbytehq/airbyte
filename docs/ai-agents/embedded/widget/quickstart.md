# Get started with the Airbyte Embedded Widget

This guide walks you through implementing the Airbyte Embedded Widget into your existing web application. You'll learn how to set up connection templates, authenticate your application, and embed the widget to allow your users to sync their data. This should take approximately 30 minutes to complete.

## Prerequisites

Before getting started with this guide, make sure you have access to Airbyte Embedded. Reach out to teo@airbyte.io if you need access!

## Prepare your organization

:::info
Steps 1 and 2, connection template and source template creation, can also be managed via API. View the API docs at https://api.airbyte.ai/api/v1/docs for more information.
:::

**1. Create your connection template:** visit https://app.airbyte.ai and visit the "Connection templates" page to create at least one connection template for your organization. Connection templates create one connection for each source that your end users create, so that their data ends up in your bucket or data lake.

By default, the system applies _all_ connection templates to each new source your users set up. This means if you have two templates for two separate S3 buckets, every source created syncs to both. To manage this more precisely, you can use tags.

For example, you might tag by product tier such as `free`, `standard`, or `enterprise`; by use case such as `sales`, `retail`, or `crm`; or by whatever else makes sense for your organization. These tags are used later on when the widget loads.

**2. Add integrations:** next, visit the "Integrations" page to clone source templates into your organization or create custom ones.

By default, the system shows all of your organization's integrations to all of your users. You can also manage these via tags.

**3. Gather your credentials:** on the "Embed Code" page, you find the credentials you need to request a widget token.

:::warning
Never store your `client_id` and `client_secret` in client-side code.
:::

### Implement in your backend

Your backend should implement the token fetching implementation for your widget. This requires two steps: first, fetch an app token, and then use that to fetch a widget token.

**1. Request an app token:** an app token is a JSON Web Token (JWT) associated with you, the organization administrator, that you use to request a widget token, the token for your end user.

```bash title="Request an application token"
curl -X POST https://api.airbyte.ai/api/v1/account/applications/token \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "your_client_id",
    "client_secret": "your_client_secret"
  }'
```

**2. Add a way to request a widget token:** a widget token is a string that contains an encoded version of both a JWT and the URL the widget uses to open. To request a widget token, make a request like the following:

```bash title="Request a widget token"
curl -X POST https://api.airbyte.ai/api/v1/embedded/widget-token \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_APPLICATION_TOKEN" \
  -d '{
    "workspace_name": "unique_user_identifier",
    "allowed_origin": "your_url",
    "selected_source_template_tags": ["pro"],
    "selected_source_template_tags_mode": "all",
    "selected_connection_template_tags": ["pro"],
    "selected_connection_template_tags_mode": "all"
  }'
```

Parameters:

- `workspace_name`: a unique identifier for each of your end users, for example, user ID
- `allowed_origin`: the URL where you are embedding the widget, used for authentication
- `selected_source_template_tags`: optional - filter source templates by tags configured earlier
- `selected_source_template_tags_mode`: optional - whether to match "any" or "all" tags when listing
- `selected_connection_template_tags`: optional - filter connection templates by tags configured earlier
- `selected_connection_template_tags_mode`: optional - whether to match "any" or "all" tags when listing

### Implement in your frontend

**1. Add the widget package to your project:** the Airbyte Embedded widget is available as an npm package at https://www.npmjs.com/package/@airbyte-embedded/airbyte-embedded-widget.

```bash npm2yarn
npm install @airbyte-embedded/airbyte-embedded-widget
```

**2. Add the widget to your page:** embed the widget.

```ts title="EmbeddedSection.tsx"
import { AirbyteEmbeddedWidget } from "@airbyte-embedded/airbyte-embedded-widget";

export const EmbeddedSection: React.FC = () => {
  const handleConnectData = async () => {
    try {
      // Fetch the widget token via your backend implementation
      const { data } = await apiClient.getAirbyteWidgetToken({
        workspace_name: "unique_user_identifier",
        allowed_origin: "your_url",
        selected_source_template_tags: ["pro"],
        selected_source_template_tags_mode: "all",
        selected_connection_template_tags: ["pro"],
        selected_connection_template_tags_mode: "all",
      });

      const widget = new AirbyteEmbeddedWidget({
        token: data.token,
      });

      widget.open();
    } catch (error) {
      console.error("Error connecting data:", error);
    }
  };

  return <button onClick={handleConnectData}>Connect your Data</button>;
};
```

### Event callbacks

You can pass an `onEvent` callback to the widget to receive messages when the user completes actions in the widget:

```ts title="Success callback"
{
  type: "end_user_action_result";
  message: "source_created" | "source_updated";
  data: SourceRead; // The sanitized configuration info of the created source
}
```

Or, in case of error:

```ts title="Error callback"
{
  type: "end_user_action_result";
  message: "source_create_error" | "source_update_error";
  error: Error;
}
```

You can use this to trigger actions within your own app.

## Next steps

As users begin setting up integrations in the widget, the following happens:

1. Airbyte checks the user's configuration such as credentials prior to saving the source.
2. Once Airbyte creates the source, Airbyte Embedded kicks off a job to create the destinations and connections you configured.
3. Airbyte begins syncing data to your destinations according to the sync preferences you set up in your connection templates.
