---
products: cloud-no-flex
---

# Context layer

The context layer lets AI agents access and reason about your organization's data through the [Airbyte MCP](../airbyte-mcp/readme.md). It has two independent parts. Organization admins can turn on either part or both.

## Agent access

Agent access gives your agent read-only, live access to sources and destinations through their connectors. It uses the credentials you already stored in Airbyte and doesn't need a connection or a sync. Learn about [agent access](agent-access.md).

## Search

Search finds relevant records by keyword, meaning, or both in an index Airbyte builds from your connections' synced data. It helps agents find information across tickets, conversations, and notes without knowing record IDs or exact words. Learn about [search](search.md).

![Context layer overview: a connection replicates data from a source through source and destination connectors to a destination. An AI agent uses the Airbyte MCP for read-only direct reads through the connectors and queries an Airbyte-hosted search index fed by syncs or an optional destination backfill.](/img/context-layer-overview.svg)

## Data access methods

| | Replicated data | Agent access | Search |
| :--- | :--- | :--- | :--- |
| Freshness | As of your latest sync. | As of the API request or destination query. | As of your latest indexed sync or backfill. |
| Needs a connection | Yes. | No. | Yes, with search enabled. |
| Good for | Historical analysis and joins in your destination. | Current records, known IDs, and SQL queries. | Finding relevant records by keyword or meaning. |
| Tool | Your destination's query tools, or `execute_external_sql_query` for supported destinations. | `execute_external_api_query` or `execute_external_sql_query`. | `execute_external_search_query`. |

## How agents use the context layer

An organization admin [manages agent access and search independently](manage-access.md). After your organization enables the parts and resources it wants to make available, [connect your agent to the Airbyte MCP](../airbyte-mcp/install.md) and ask questions in plain language. Your agent picks the tools it needs. You don't need to choose an access method or name a tool.

## Availability

Agent access and search are available only in Airbyte Cloud, not self-managed Airbyte Core or Enterprise. In workspaces on customer-owned Enterprise Flex data planes, you can't turn on agent access for sources or destinations, and search isn't available for connections.

## Usage limits

The context layer is free to use. Each organization can make up to 100,000 direct reads and searches combined per month. Other Airbyte MCP tools don't count toward this limit. Direct reads also count toward the API rate limits of the source you read from. SQL queries and search backfills use destination compute, which your destination provider may charge for.
