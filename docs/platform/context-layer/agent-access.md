---
products: cloud-no-flex
---

# Agent access

Agent access lets your AI agent read live data from a source or destination through the [Airbyte MCP](../airbyte-mcp/readme.md). Use it to check a record's current state, retrieve recent data without waiting for a sync, or query your warehouse with SQL.

For example, your agent can check the current status of a Zendesk ticket or count last week's orders in Snowflake. Agent access works independently of [search](search.md).

## How agent access works

Direct reads use the credentials you already configured for a source or destination in Airbyte. You don't need a connection, and your agent never sees the credentials.

Your agent reads the connector's skill to learn which entities and actions it supports, then requests data. Depending on the connector, it can list records, get a record by ID, or search through the connector's own API. For supported destinations, it runs read-only SQL.

Direct reads can't create, update, or delete records. The stored credentials determine which records the agent can read, while your Airbyte permissions determine which connectors it can use. See [Manage context layer access](manage-access.md) to enable agent access and select resources.

## Supported connectors

### Sources

[Agent connectors](/platform/move-data/sources-destinations-connectors#connector-capabilities) support direct reads. Check the connector's skill for its supported entities, actions, and filters. The **Context layer** page marks unsupported connectors as not supported.

### Destinations

Agents can query these destinations with read-only SQL:

- [BigQuery](/integrations/destinations/bigquery)
- [Snowflake](/integrations/destinations/snowflake)

Only `SELECT` statements and `SHOW TABLES` are allowed.

## Example prompts

After you [connect your agent to the Airbyte MCP](../airbyte-mcp/install.md), ask questions such as:

- "What's the current status of Zendesk ticket 123?"
- "Show the five most recent Salesforce opportunities."
- "Count last week's orders in our Snowflake destination."

Your agent chooses the tools and reads the connector's skill as needed. For tool and action details, see [Direct read tools](../airbyte-mcp/tools.md#direct-reads).

## Limitations

- Agent access is available only in Airbyte Cloud, not self-managed Airbyte Core or Enterprise. You can't turn on agent access for sources or destinations in workspaces on customer-owned Enterprise Flex data planes.
- Direct reads don't work with connectors whose secrets are stored in an [external secrets manager](../operating-airbyte/external-secrets.md).
- Requests are subject to the source's API rate limits and the [shared context layer usage limit](readme.md#usage-limits). SQL queries use destination compute.
