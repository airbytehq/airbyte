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

## Add and manage sources and destinations

<DocCardList />
