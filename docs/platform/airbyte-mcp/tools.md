---
products: cloud
---

# Airbyte MCP tools

:::info Private beta
Airbyte MCP is in private beta. Features and tools may change. It's available to Airbyte Cloud organizations enrolled in the beta. Self-managed versions of Airbyte aren't supported during the beta.
:::

Airbyte MCP gives your agent a set of tools. Your agent chooses which tools to call based on your prompt, so you don't need to call them by name. This page lists each tool so you know what your agent can and can't do.

Every tool acts with your Airbyte permissions. If your Airbyte [role](/platform/access-management/rbac) doesn't allow an action, the tool fails.

## Safety

Airbyte MCP protects resources you didn't create with your agent.

- **Destructive tools are limited to the current session.** Tools that delete, overwrite, or reconfigure resources only act on resources your agent created in the same session. They can't delete a connection someone else built.
- **Your MCP client asks before acting.** Each tool tells your client whether it's read-only or destructive. Most clients ask you to approve tools that change things.

## Workspaces and organizations

| Tool | Description |
| :--- | :--- |
| `get_default_cloud_context` | Get your default organization and workspace. |
| `list_cloud_organizations` | List the organizations you can access. |
| `describe_cloud_organization` | Get details about an organization. |
| `get_cloud_organization_billing_status` | Get billing and account status for an organization. Requires an organization reader or admin role. |
| `list_cloud_workspaces` | List the workspaces you can access. |
| `describe_cloud_workspace` | Get details about a workspace, like its name, URL, and organization. |
| `set_default_cloud_workspace` | Change your default workspace. This changes your default workspace in the Airbyte web app, too. |

## Sources and destinations

| Tool | Description |
| :--- | :--- |
| `list_cloud_connectors` | List the sources and destinations in a workspace. |
| `describe_cloud_connector` | Get details about a source or destination, including its configuration, connections, and direct read instructions. |
| `deploy_connector_to_cloud` | Create a source or destination in a workspace. |
| `deploy_noop_destination_to_cloud` | Create a No-op destination for testing a source. |
| `check_cloud_connector` | Test the configuration and credentials of a source or destination. |
| `rename_cloud_connector` | Rename a source or destination. |
| `update_cloud_connector_config` | Change the configuration of a source or destination. |
| `permanently_delete_cloud_connector` | Delete a source or destination. |

## Connections and syncs

| Tool | Description |
| :--- | :--- |
| `list_cloud_connections` | List the connections in a workspace. |
| `describe_cloud_connection` | Get details about a connection, like its streams, schedule, and status. |
| `create_connection_on_cloud` | Create a connection between a source and a destination. |
| `update_cloud_connection` | Turn a connection on or off, or change its sync schedule. |
| `rename_cloud_connection` | Rename a connection. |
| `set_cloud_connection_selected_streams` | Choose which streams a connection syncs. |
| `set_cloud_connection_table_prefix` | Set the table prefix for a connection. |
| `get_connection_artifact` | Get a connection's state or configured catalog. |
| `permanently_delete_cloud_connection` | Delete a connection. |
| `run_cloud_sync` | Start a sync. |
| `cancel_cloud_sync` | Cancel a running sync. |
| `get_cloud_sync_status` | Get the status of a sync job. |
| `list_cloud_sync_jobs` | List the recent sync jobs for a connection. |
| `get_cloud_sync_logs` | Read the logs from a sync job, to troubleshoot failures. |

## Dashboards

These tools display interactive views in clients that support [MCP Apps](https://modelcontextprotocol.io/extensions/apps/overview). In other clients, they return the same information as text.

| Tool | Description |
| :--- | :--- |
| `show_workspace_sync_status` | Show a sync status dashboard for a workspace. |
| `show_connection_sync_history` | Show sync history, success rates, and volume for a connection. |
| `show_connectors_list` | Show a catalog of Airbyte connectors you can browse. |

## Custom connectors

| Tool | Description |
| :--- | :--- |
| `list_custom_source_definitions` | List the custom connectors in a workspace. |
| `get_custom_source_definition` | Get a custom connector, including its YAML manifest. |
| `get_connector_builder_draft_manifest` | Get the unpublished draft of a custom connector from the [Connector Builder](/platform/connector-development/connector-builder-ui/overview). |
| `publish_custom_source_definition` | Publish a YAML manifest as a custom connector. |
| `update_custom_source_definition` | Update a custom connector's YAML manifest. |
| `permanently_delete_custom_source_definition` | Delete a custom connector. |

## Direct reads

These tools read data directly from sources and destinations. They only work after an organization admin [enables the Context layer](../context-layer/manage-access.md) and turns on agent access for the source or destination. They're read-only.

| Tool | Description |
| :--- | :--- |
| `get_agent_skill_docs` | Get a connector skill: the entities, actions, and parameters a source or destination supports for direct reads. Your agent reads this before it reads data. |
| `execute_external_api_query` | Read live records from a source's API. Supports the `list` and `get` actions. |
| `execute_external_sql_query` | Run a read-only SQL query on a Snowflake or BigQuery destination. Only `SELECT` statements and `SHOW TABLES` are allowed. |

### Connector skills

Every connector's API is different. A connector skill is a short document that tells your agent which entities it can read, like `contacts` or `tickets`, and which parameters each action accepts. Before your agent reads data from a source, it calls `get_agent_skill_docs` to learn that connector's skill. This prevents your agent from guessing at parameter names.

### Direct read actions

| Action | What it does | Example |
| :--- | :--- | :--- |
| `list` | Return a page of records for an entity, with optional filters. | List open Zendesk tickets. |
| `get` | Return one record by its ID. | Get the HubSpot contact with ID `123`. |

Direct reads can't create, update, or delete records.

## Connector registry and documentation

| Tool | Description |
| :--- | :--- |
| `list_connectors` | Search the Airbyte connector catalog. |
| `get_connector_info` | Get a connector's metadata, documentation URL, and configuration specification. |
| `get_connector_version_history` | Get a connector's recent versions and changelog. |
| `get_api_docs_urls` | Get links to the documentation for a connector's third-party API. |
| `search_airbyte_knowledge_sources` | Look up answers in Airbyte's documentation and other Airbyte knowledge sources. |
