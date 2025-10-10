---
products: embedded
---

# Get Started with the Airbyte Embedded Widget

## Prerequisites

Before getting started with this guide, make sure you have access to Airbyte Embedded. Reach out to teo@airbyte.io if you need access!

## Let's go!

### Prepare your organization

::info
Steps 1 and 2, connection template and source template creation, can also be managed via API. View our API docs at https://api.airbyte.ai/api/v1/docs for more information.

_1. Create your connection template: _ Visit https://app.airbyte.ai and visit the "Connection templates" page to create at least one connection template for your organization. Connection templates will be used to create one connection for each source that your end users create, so that their data ends up in your bucket or data lake.

By default we will apply _all_ connection templates to each new source your users set up. This means if you have two templates for two separate S3 buckets, every source created will sync to both. To manage this more precisely, you can use tags.

For example, you might tag by product tier (`free`, `standard`, `enterprise`), usecase (`sales`, `retail`, `crm`), or whatever else makes sense for your organzation. These tags will be used later on when we load the widget itself.

_2. Add integrations: _ Next, visit the "Integrations" page to clone source templates into your organization or create custom ones.

By default, we will show all of your organization's integrations to all of your users. These can also be managed via tags.

**3. Gather your credentials: ** On the "Embed Code" page, you will find the credentials you need to request a widget token.

:::warning
Never store your client_id and client_secret in client-side code.

### Start implementing

#### In your backend

Your backend should implement the token fetching implementation for your widget. There are two steps to this -- fetching an application token, and then using that to fetch a widget token.

_1. Request an Appliation token: _ An application token is a jwt associated with you (the organization admin) that can be used to request a widget token (the token for your end user).

```BASH
curl -X POST https://api.airbyte.ai/account/applications/token \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "your_client_id",
    "client_secret": "your_client_secret"
  }'
```

_2. Add a way to request a widget token: _ A widdget token is a string that contains an encoded version of both a jwt and the URL the widget will use to open. To request a widget token, you will make a request like:

```BASH
curl -X POST https://api.airbyte.ai/embedded/widget_token \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_APPLICATION_TOKEN" \
  -d '{
    "workspace_name": "unique_user_identifier", # this should be something unique to each of your end users, like a user id
    "allowed_origin": "your_url" # where you are embedding the widget. used for authentication.
    "selected_source_template_tags": ["pro"] # optional! if you set up tags above, you can use them here
    "selected_source_template_tags_mode": ["all"] # optional! whether to match any tag or all tags when listing
     "selected_connection_template_tags": ["pro"] # optional! if you set up tags above, you can use them here
    "selected_connection_template_tags_mode": ["all"] # optional! whether to match any tag or all tags when listing
  }'
```

#### In your frontend

_1. Add the widget package to your project: _ The Airbyte Embedded widget is available as an npm package at https://www.npmjs.com/package/@airbyte-embedded/airbyte-embedded-widget. Install this using your package manager of choice.

_2. Add the widget to your page: _ Embed the widget!

```typescript
import { AirbyteEmbeddedWidget } from "@airbyte-embedded/airbyte-embedded-widget";

export const EmbeddedSection: React.FC = () => {
  const handleConnectData = async () => {
    try {
    // Fetch the widget token via your backend implementation
      const { data } = await apiClient.getAirbyteWidgetToken(
        {   "workspace_name": "unique_user_identifier",
            "allowed_origin": "your_url"
            "selected_source_template_tags": ["pro"]
            "selected_source_template_tags_mode": ["all"]
            "selected_connection_template_tags": ["pro"]
            "selected_connection_template_tags_mode": ["all"]
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

#### Event Callbacks

You can pass an `onEvent` callback to the widget receive messages when the user completes actions in the widget:

```ts
{
  type: "end_user_action_result";
  message: "source_created" | "source_updated";
  data: SourceRead; // The sanitized configuration info of the created source
}
```

Or, in case of error:

```ts
{
  type: "end_user_action_result";
  message: "source_create_error" | "source_update_error";
  error: Error;
}
```

You can use this to trigger actions within your own application.

#### Next

As users begin setting up integrations in the widget, the following will happen:

1. We will check the user's configuration (credentials, etc.) prior to saving the source
2. Once the source is created, behind the scenes Airbyte Embedded will kick off a job to create the destination(s) and connection(s) you have set it up to
3. Airbyte will begin syncing data to your destination(s) according to the sync preferences you set up in your connection templates
