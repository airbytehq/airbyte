# Airbyte Embedded

Airbyte Embedded enables you to add hundreds of integrations into your product instantly. Your end-users can authenticate into their data sources and begin syncing data to your product. You no longer need to spend engineering cycles on data movement. Focus on what makes your product great, rather than maintaining ELT pipelines.

There are three components to Airbyte Embedded:
1. Configuring connections: Connections define where your users data will land.
2. Configuring source templates: Templates define which connectors are available for your end users
3. Configuring sources: Collect your users credentials so their data is synced to your data warehouse.

There are two approaches to set up Airbyte Embedded.
1. Use the [Airbyte Embedded Widget](./widget/README.md). This simple Javascript plugin will allow you to easily sync your customer's data.
2. Use the [Airbyte API](./api/README.md). Build a fully customized experience on top of Airbyte's API. 

The complete API reference can be found at https://api.airbyte.ai/api/v1/redoc