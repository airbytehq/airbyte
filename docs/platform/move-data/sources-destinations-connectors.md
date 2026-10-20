---
products: all
---

import DocCardList from '@theme/DocCardList';

# Sources, destinations, and connectors

In Airbyte, you move data from **sources** to **destinations** using **connectors**.

## Sources and destinations

A **source** is the database, API, or other system **from** which you sync data. A **destination** is the data warehouse, data lake, database, or other system **to** which you sync data.

## Connectors

A **connector** is the component Airbyte uses to connect to and interact with your source or destination. Connectors are a key difference between a resilient Airbyte deployment and a more brittle in-house data pipeline.

Airbyte has two types of connectors: source connectors and destination connectors. Sometimes, people abbreviate these to "sources" and "destinations." That can be a little confusing, so to be clear, a connector isn't the same thing as the source or destination it connects to, but it's closely related to them.

Connectors have [different support levels](/integrations/connector-support-levels). Some are built and maintained by Airbyte and some are contributed by members of Airbyte's community.

### Connectors are open source

Airbyte provides over 600 connectors, almost all of which are open source. You can contribute to connectors to make them better or keep them up-to-date as third-parties make changes, or fork it to make it more suitable to your particular needs.

If you don't see the connector you need, you can build one from scratch. Airbyte provides a no-code and low-code [Connector Builder](../connector-development/connector-builder-ui/overview). For advanced use cases, you can use Connector Development Kits (CDKs), which are more traditional software development tools.

### Connector capabilities

A connector can have one or both of these capabilities:

- **Data replication** moves data. The connector extracts data from a source and loads it into a destination during a sync. Everything in the [connector catalog](/integrations/) supports data replication.

- **Agent access** answers questions. The connector calls a third-party system in real time and returns only the records an AI agent asks for. Some connectors, like HubSpot or Zendesk, support [agent access](/ai-agents/connectors/) as well as data replication.

Each connector's page shows which capabilities it has under **Connector type**.

In Airbyte Cloud, the [context layer](/platform/context-layer) lets a single source or destination you set up use both capabilities. When it's on, a connector you set up for data replication can also answer read-only requests from AI agents through the [Airbyte MCP](/platform/airbyte-mcp), using the same stored credentials. These direct reads support the `list` and `get` actions. They don't affect your syncs.

## Add and manage sources and destinations

<DocCardList />
