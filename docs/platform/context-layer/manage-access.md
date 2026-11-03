---
products: cloud-no-flex
---

# Manage context layer access

Manage [agent access](agent-access.md) and [search](search.md) independently. Organization admins turn each part on or off. Workspace members with edit permission choose the resources available to agents.

## Permissions

Only [organization admins](/platform/access-management/rbac) can change organization-wide settings and accept search terms. You need workspace edit permission to change agent access for a source or destination or search for a connection.

Agents act with the Airbyte permissions of the person or application using the [Airbyte MCP](../airbyte-mcp/readme.md). For direct reads, the credentials saved in the connector determine which records agents can see. Those credentials might allow access to data the person couldn't otherwise read in the third-party system. Review their scope before enabling access.

## Manage agent access

### Turn on agent access

1. In Airbyte, open **Context layer**.
2. Turn on **Agent access**.

Airbyte turns on agent access for all supported sources in your organization. Destinations aren't turned on automatically.

### Choose sources and destinations

1. Open **Context layer** and click **Sources** or **Destinations**.
2. Find the workspace.
3. Turn **Agent access** on or off for each source or destination.

You can also change **Agent access** in a source or destination's **Settings**. When you create a supported source or destination, its setup form includes this option if organization agent access is on. For sources, it's on by default.

### Turn off agent access

To stop direct reads from one resource, turn off its **Agent access** setting. To stop direct reads across the organization, turn off **Agent access** in **Context layer** and click **Disable** to confirm.

Airbyte keeps your resource selections and restores them if you turn organization agent access back on. Turning off agent access doesn't stop replication or independently enabled search.

## Manage search

### Turn on search

1. In Airbyte, open **Context layer** settings.
2. Turn on **Semantic search**.
3. Review and accept the new terms of service for storing indexed data on Airbyte infrastructure.

### Choose connections

Open **Context layer** > **Semantic search** and turn **Semantic search** on or off for each connection. Both its source and destination must be agent connectors.

After your organization enables search, new eligible connections have **Semantic search** on by default. You can change this when creating a connection or in its settings.

Search indexes data synced after you enable it. To make previously synced data searchable, [start a backfill](search.md#backfill-existing-data).

### Turn off search

Turn off **Semantic search** for a connection to stop indexing it, or turn off the organization setting to stop search for the organization. Airbyte deletes the affected index. Re-enabling search requires a new backfill to search previously synced data, using destination compute again.

Turning off search doesn't turn off agent access or data replication.

## Availability

Agent access and search are available only in Airbyte Cloud, not self-managed Airbyte Core or Enterprise. You can't enable agent access for resources in workspaces on customer-owned Enterprise Flex data planes. Keep search off for connections on those data planes: if search is on, their syncs fail before they start.

## Connect your agent

After you configure access, [connect your agent to the Airbyte MCP](../airbyte-mcp/install.md). Ask questions in plain language, and your agent uses the available resources.
