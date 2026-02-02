# Airbyte Embedded

Airbyte Embedded enables you to add hundreds of integrations into your product instantly. Your end-users can authenticate into their data sources and begin syncing data to your product. You no longer need to spend engineering cycles on data movement. Focus on what makes your product great, rather than maintaining ELT pipelines.

There are three components to Airbyte Embedded:
1. Configuring connections: Connections define where your users data will land.
2. Configuring source templates: Templates define which connectors are available for your end users
3. Configuring sources: Collect your users credentials so their data is synced to your data warehouse.

You can read more about about how Airbyte Embedded fits in your application [here](https://airbyte.com/blog/how-to-build-ai-apps-with-customer-context).

Before using any Airbyte developer tools, ensure you have:

- **Airbyte Cloud account**: Sign up at [cloud.airbyte.com](https://cloud.airbyte.com)
- **Embedded access**: Contact michel@airbyte.io or teo@airbyte.io to enable Airbyte Embedded on your account
- **API credentials**: Available in your Airbyte Cloud dashboard under Settings > Applications

There are two approaches to set up Airbyte Embedded: the widget and the API.

## When to Use the Widget

Use the [Airbyte Embedded Widget](./widget/README.md) if you:

- Want to get started quickly with minimal development effort
- Are comfortable with a pre-built UI that matches Airbyte's design
- Want Airbyte to handle authentication, error states, and validation

## When to Use the API

Use the [Airbyte API](./api/README.md) if you:

- Need complete control over the user experience and UI design
- Want to integrate data source configuration into your existing workflows

The complete API reference can be found at [https://api.airbyte.ai/api/v1/docs](https://api.airbyte.ai/api/v1/docs)
