---
products: cloud
---

# Manage context layer access

:::info Private beta
The context layer is in private beta. Features may change. It's available to Airbyte Cloud organizations enrolled in the beta. Self-managed deployments of Airbyte aren't supported.
:::

Control which sources and destinations AI agents can read directly through the [Airbyte MCP](../airbyte-mcp/readme.md). First, an organization admin turns on the context layer for the organization. Then, choose which sources and destinations agents can access.

## Turn on the context layer for your organization

You need to do this once for your organization. You must be an [organization admin](/platform/access-management/rbac).

1. In Airbyte, click **Context layer** in the navigation bar.

2. Turn on **Agent access**.

When you turn on agent access, Airbyte turns on agent access for all supported sources in your organization. Destinations aren't turned on automatically. You must turn on each destination individually.

If you aren't an organization admin, the **Context layer** page tells you that an admin needs to turn it on. Ask an organization admin in your Airbyte organization.

## Choose which sources and destinations agents can access

After the context layer is on, you can turn agent access on or off for each source and destination. You need edit permission for sources or destinations in that workspace.

Turning off agent access doesn't affect data replication. Connections that use that source or destination keep syncing.

### From the Context layer page

1. In Airbyte, click **Context layer** in the navigation bar.

2. Click **Sources** or **Destinations**.

3. Find the workspace, then turn **Agent access** on or off for each source or destination. Connectors that don't support direct reads are marked as not supported.

### When you create a source or destination

When the context layer is on, the setup form for a supported source or destination includes an **Agent access** option. For sources, it's on by default. Turn it off if you don't want agents to read from this source.

### From a source or destination's settings

1. Open the source or destination.

2. Click **Settings**.

3. Turn **Agent access** on or off.

## Turn off the context layer for your organization

You must be an organization admin.

1. In Airbyte, click **Context layer** in the navigation bar.

2. Turn off **Agent access**.

3. Click **Disable** to confirm.

Agents lose access to every source and destination in the organization. Airbyte keeps your source and destination selections and restores them if you turn the context layer back on.

## Connect your agent

After you give agents access, [connect the Airbyte MCP to your agent](../airbyte-mcp/install.md). Your agent can then read from the sources and destinations you chose.
