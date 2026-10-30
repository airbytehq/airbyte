---
products: cloud
---

# Context layer

:::info
The context layer is available to all Airbyte Cloud organizations. Self-managed deployments of Airbyte aren't supported.
:::

The context layer is how AI agents access and reason about your organization's data through the [Airbyte MCP](../airbyte-mcp/readme.md). It combines three ways to get data:

- **Replicated data**: the data Airbyte syncs into your warehouse. It's complete, historical, and joined across all your sources.
- **Direct reads**: live data your agent reads from a source or destination at the moment it needs it, without a sync.
- **Search**: relevant records your agent finds by keyword, meaning, or both in an index Airbyte builds from your synced data. See [Search your data](search.md).

![Context layer overview: a connection replicates data from a source through source and destination connectors to a destination. An AI agent uses the Airbyte MCP for read-only direct reads through the connectors and queries an Airbyte-hosted search index fed by syncs or an optional destination backfill.](/img/context-layer-overview.svg)

## Choose how to access data

| | Replicated data | Direct reads | Search |
| :--- | :--- | :--- | :--- |
| Freshness | As of your latest sync. | As of the API request or destination query. | As of your latest indexed sync or backfill. |
| Needs a connection | Yes. | No. | Yes, with search enabled. |
| Good for | Historical analysis and joins in your destination. | Current records, known IDs, and SQL queries. | Finding relevant records by keyword or meaning. |
| Tool | Your destination's query tools, or `execute_external_sql_query` for supported destinations. | `execute_external_api_query` or `execute_external_sql_query`. | `execute_external_search_query`. |

## What are direct reads?

A direct read is a request your agent makes to a source or destination through the Airbyte MCP, outside of a sync. For example:

- Your agent asks Zendesk for the current status of a ticket, instead of waiting for the next sync.
- Your agent runs a SQL query on Snowflake to count last week's orders.

Direct reads use the credentials you already configured for that source or destination in Airbyte. You don't need to create a connection, and your agent never sees the credentials.

Direct reads are read-only. Your agent can list, get, and search records when the connector supports those actions, but it can't create, update, or delete them. A connector's API search is different from [context layer search](search.md), which queries an index of synced data.

## Why organization admins control the context layer

Direct reads give AI agents access to data in your business systems. That's a decision for your organization, so only organization admins can turn on the context layer. Turning it on is a one-time task for your organization. After that, admins and workspace members with edit permission choose which sources and destinations agents can read from.

What an agent can read is also governed by:

- The Airbyte permissions of the person or application using the Airbyte MCP. Airbyte users can only work in the organizations and workspaces they have access to, and can only perform actions allowed by their role in Airbyte.
- The permissions of the credentials used to set up each source or destination. When an agent queries a source or destination directly, it uses the credentials saved in that connector in that workspace. This means it's possible for a user to see data they might not otherwise have access to, or to not see data they otherwise do have access to.

To turn on the context layer, see [Manage context layer access](manage-access.md).

## How agents use the context layer

After you turn on the context layer and give agents access to a source or destination, any agent connected to the [Airbyte MCP](../airbyte-mcp/install.md) can read from it.

1. Your agent finds the source or destination with `list_cloud_connectors`.
2. Your agent reads the connector's skill with `get_agent_skill_docs` to learn which entities and actions it supports.
3. Your agent reads data with `execute_external_api_query` for a source, or `execute_external_sql_query` for a destination.

If you [turn on search](search.md#turn-on-search), your agent can also find indexed records with `execute_external_search_query`.

You don't need to name these tools. Ask your agent a question, like "What are the five most recent Salesforce opportunities?" and it picks the tools for you. For details, see [Airbyte MCP tools](../airbyte-mcp/tools.md#direct-reads).

## Supported connectors {#supported-connectors}

### Sources

[Agent connectors](/platform/move-data/sources-destinations-connectors#connector-capabilities) support agent access for direct reads and search. Depending on the connector, direct reads support `list`, `get`, and the connector's own API `search` action. Check the connector's skill for its supported read actions. Context layer search indexes a connection's synced data and requires both the source and destination to be agent connectors.

When a source doesn't support direct reads, the **Context layer** page in Airbyte shows that it isn't supported yet.

### Destinations

Direct reads are available for these destinations:

- [BigQuery](/integrations/destinations/bigquery)
- [Snowflake](/integrations/destinations/snowflake)

Agents query these destinations with read-only SQL. Only `SELECT` statements and `SHOW TABLES` are allowed.

## Usage limits

The context layer is free to use. Each organization can make up to 100,000 direct reads and searches combined per month. Other Airbyte MCP tools don't count toward this limit. Direct reads also count toward the API rate limits of the source you read from, and SQL queries and search backfills use compute in your destination, which your destination provider may charge for.

## Limitations

- The context layer is only available for Airbyte Cloud.
- Direct reads and searches are read-only. Agents can't write to sources or destinations through the context layer.
- Direct reads are only available for [supported connectors](#supported-connectors).
- Direct reads don't work with connectors whose secrets are stored in an [external secrets manager](../operating-airbyte/external-secrets.md).
