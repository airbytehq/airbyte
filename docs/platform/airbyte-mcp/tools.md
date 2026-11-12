---
products: cloud, oss-community
---

# Airbyte MCP tools

The Airbyte MCP gives your agent a set of tools. Your agent chooses which tools to call based on your prompt, so you don't need to call them by name. This page lists each tool so you know what your agent can and can't do.

Your agent acts on behalf of the Airbyte user who signed in to the Airbyte MCP. If you connect with an [Airbyte application](install.md#connect-without-a-browser), that's the user who created the application. Every tool acts with that user's Airbyte permissions. If their Airbyte [role](/platform/access-management/rbac) doesn't allow an action, the tool fails.

Direct reads work differently. When your agent [reads directly from a source or destination](#direct-reads), the third-party system sees a request from the credentials stored in that connector in that workspace, not from you. Your Airbyte permissions still control which connectors your agent can use, but the stored credentials control which records it can read.

## Safety

Your agent can see and use every resource your Airbyte permissions allow. To prevent your agent from accidentally breaking existing pipelines, the Airbyte MCP adds safeguards to tools that change or delete resources.

- **Deletes require a marked name.** Tools that permanently delete sources, destinations, connections, and custom connector definitions only work if the resource's name contains `delete-me` or `deleteme`. To let your agent delete a resource, rename it yourself first.
- **You can turn off tools that change things.** To hide destructive tools or block changes to pipelines, see [Advanced configuration](advanced-configuration.md).
- **Local demo mode limits changes to the current session.** If you [run the Airbyte MCP locally](self-managed.md), set `AIRBYTE_CLOUD_MCP_LOCAL_DEMO_MODE=1` so tools only change or delete resources your agent created in the same session. The hosted server ignores this setting.
- **Your MCP client asks before acting.** Each tool tells your client whether it's read-only or destructive. Most clients ask you to approve tools that change things.

## Workspaces and organizations

| Tool                              | Description                                                                                                            |
| :-------------------------------- | :--------------------------------------------------------------------------------------------------------------------- |
| `get_default_workspace_context`   | Get your default organization and workspace.                                                                           |
| `list_organizations`              | List the organizations you can access.                                                                                 |
| `describe_organization`           | Get details about an organization.                                                                                     |
| `get_organization_billing_status` | Get billing and account status for an organization. Requires an organization reader or admin role. Airbyte Cloud only. |
| `list_workspaces`                 | List the workspaces you can access.                                                                                    |
| `describe_workspace`              | Get details about a workspace, like its name, URL, and organization.                                                   |
| `set_default_workspace`           | Change your default workspace. This changes your default workspace in the Airbyte web app, too.                        |

## Sources and destinations

| Tool                           | Description                                                                                                        |
| :----------------------------- | :----------------------------------------------------------------------------------------------------------------- |
| `list_connectors`              | List the sources and destinations in a workspace.                                                                  |
| `describe_connector`           | Get details about a source or destination, including its configuration, connections, and direct read instructions. |
| `deploy_connector`             | Create a source or destination in a workspace.                                                                     |
| `deploy_noop_destination`      | Create a No-op destination for testing a source.                                                                   |
| `check_connector`              | Test the configuration and credentials of a source or destination.                                                 |
| `rename_connector`             | Rename a source or destination.                                                                                    |
| `update_connector_config`      | Change the configuration of a source or destination.                                                               |
| `permanently_delete_connector` | Delete a source or destination.                                                                                    |

## Connections and syncs

| Tool                              | Description                                                                                                   |
| :-------------------------------- | :------------------------------------------------------------------------------------------------------------ |
| `list_connections`                | List the connections in a workspace.                                                                          |
| `describe_connection`             | Get details about a connection, like its streams, schedule, and status.                                       |
| `create_connection`               | Create a connection between a source and a destination.                                                       |
| `update_connection`               | Turn a connection on or off, change its sync schedule or stream configuration, or apply a discovered catalog. |
| `rename_connection`               | Rename a connection.                                                                                          |
| `set_connection_selected_streams` | Choose which streams a connection syncs.                                                                      |
| `set_connection_table_prefix`     | Set the table prefix for a connection.                                                                        |
| `discover_source_catalog`         | Discover a source's catalog, check discovery progress, or compare catalogs.                                   |
| `get_connection_artifact`         | Get a connection's state or configured catalog.                                                               |
| `permanently_delete_connection`   | Delete a connection.                                                                                          |
| `run_connection_sync`             | Start a sync.                                                                                                 |
| `cancel_connection_sync`          | Cancel a running sync.                                                                                        |
| `get_connection_sync_status`      | Get the status of a sync job.                                                                                 |
| `list_connection_sync_jobs`       | List the recent sync jobs for a connection.                                                                   |
| `get_connection_sync_logs`        | Read the logs from a sync job, to troubleshoot failures.                                                      |

## Dashboards

These tools display interactive views. They're only available in clients that support [MCP Apps](https://modelcontextprotocol.io/extensions/apps/overview).

| Tool                           | Description                                                    |
| :----------------------------- | :------------------------------------------------------------- |
| `show_workspace_sync_status`   | Show a sync status dashboard for a workspace.                  |
| `show_connection_sync_history` | Show sync history, success rates, and volume for a connection. |
| `show_connector_definitions`   | Show a catalog of Airbyte connectors you can browse.           |

## Custom connectors

| Tool                                          | Description                                                                                                                                  |
| :-------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------- |
| `list_custom_source_definitions`              | List the custom connectors in a workspace.                                                                                                   |
| `get_custom_source_definition`                | Get a custom connector, including its YAML manifest.                                                                                         |
| `get_connector_builder_draft_manifest`        | Get the unpublished draft of a custom connector from the [Connector Builder](/platform/connector-development/connector-builder-ui/overview). |
| `publish_custom_source_definition`            | Publish a YAML manifest as a custom connector.                                                                                               |
| `update_custom_source_definition`             | Update a custom connector's YAML manifest.                                                                                                   |
| `permanently_delete_custom_source_definition` | Delete a custom connector.                                                                                                                   |

## Direct reads

These tools read data directly from sources and destinations. They only work after an organization admin [enables agent access](../context-layer/manage-access.md#manage-agent-access) and agent access is on for the source or destination. They're read-only. They're only available in Airbyte Cloud. See [Agent access limitations](../context-layer/agent-access.md#limitations).

| Tool                             | Description                                                                                                                                                                        |
| :------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `get_external_access_skill_docs` | Get a deployed connector's direct-access skill docs: its entities, actions, and parameters. Your agent reads this before it reads data.                                            |
| `execute_external_api_query`     | Read live records from a source's API. Supports `list`, `get`, and `search` when the connector offers them.                                                                        |
| `execute_external_sql_query`     | Run a read-only SQL query on a Snowflake or BigQuery destination. Supports `SELECT`/`WITH` queries and the `SHOW TABLES`, `SHOW DATABASES`, and `DESCRIBE TABLE <table>` commands. |

### Connector skills

Every connector's API is different. A connector skill is a short document that tells your agent which entities it can read, like `contacts` or `tickets`, and which parameters each action accepts. Before your agent reads data from a source, it calls `get_external_access_skill_docs` to learn that connector's skill. This prevents your agent from guessing at parameter names. To learn more, see [Connector skills for Airbyte agents](https://airbyte.com/blog/connector-skills-airbyte-agents).

### Direct read actions

| Action   | What it does                                                                          | Example                                      |
| :------- | :------------------------------------------------------------------------------------ | :------------------------------------------- |
| `list`   | Return a page of records for an entity, with optional filters.                        | List open Zendesk tickets.                   |
| `get`    | Return one record by its ID.                                                          | Get the HubSpot contact with ID `123`.       |
| `search` | Search with the connector's own API, when supported. This isn't context layer search. | Search a source's API for contacts by email. |

Direct reads can't create, update, or delete records.

## Search

These tools work with the [context layer search index](../context-layer/search.md) in Airbyte Cloud. An organization administrator must enable **Semantic search**, and the connection must have search enabled. Unlike a direct read's `search` action, context layer search queries indexed synced data rather than a connector's API.

| Tool                            | Description                                                                                                                |
| :------------------------------ | :------------------------------------------------------------------------------------------------------------------------- |
| `execute_external_search_query` | Search a source or destination's indexed data by keyword, meaning, or both. Hybrid is the default. Searches are read-only. |
| `get_search_index_status`       | Check indexed streams and backfill progress for a source or destination.                                                   |
| `request_search_index_backfill` | Request indexing of data already in a connection's destination. Supports Snowflake and BigQuery; uses destination compute. |

Searches count toward the same monthly usage limit as direct reads. For examples and setup, see [Search your data](../context-layer/search.md).

### Search query parameters

The agent supplies these parameters to `execute_external_search_query`.

| Parameter             | What it controls                                                                                                                                                                                                                                         |
| :-------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `prompt`              | The words or question to search for.                                                                                                                                                                                                                     |
| `search_type`         | The mode: `keyword`, `semantic`, or `hybrid`. Defaults to `hybrid`.                                                                                                                                                                                      |
| `limit`               | The maximum number of results, from 1 to 100. Defaults to 10.                                                                                                                                                                                            |
| `streams`             | The streams to search. Omit it to search every indexed stream, or pass an empty list to search none. Each entry includes `stream_name` and can include `namespace` to distinguish streams with the same name.                                            |
| `streams[].source_id` | The source that owns a stream. Required for each stream in a destination search. Optional in a source search, where it must match the source you're searching.                                                                                           |
| `streams[].fields`    | The fields to return in each result's `entity_data`. This is an output projection, not a match filter: other indexed fields can still match and appear in the context. Omit it for the full indexed payload, or use an empty list for no payload fields. |
| `lookback_seconds`    | Restrict results to records whose cursor falls within this many seconds.                                                                                                                                                                                 |
| `min_similarity`      | The minimum semantic similarity for a match. Applies to semantic and hybrid searches only.                                                                                                                                                               |
| `max_similarity_diff` | The maximum similarity gap from the best semantic match in an index. Applies to semantic and hybrid searches only.                                                                                                                                       |
| `max_context_chars`   | Limit the text context returned for each result. A shortened keyword context stays centered on the match.                                                                                                                                                |
| `destination_id`      | Choose which destination's index to use for a source search. Required when the source syncs to multiple enabled destinations.                                                                                                                            |

### Backfill parameters

For `request_search_index_backfill`, provide the connection ID. Optionally, provide `streams` to backfill specific selected streams and `backfill_start_time` to limit history. Omit `streams` to backfill every selected stream, or omit `backfill_start_time` for full history. Backfills use destination compute but don't change destination records.

## Connector registry and documentation

| Tool                                       | Description                                                                                                                                |
| :----------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------- |
| `list_connector_definitions`               | Search the Airbyte connector catalog.                                                                                                      |
| `get_connector_definition`                 | Get a connector's metadata, documentation URL, and configuration specification.                                                            |
| `get_connector_definition_version_history` | Get a connector's recent versions and changelog.                                                                                           |
| `get_api_docs_urls`                        | Get links to the documentation for a connector's third-party API.                                                                          |
| `search_airbyte_knowledge_sources`         | Search Airbyte's documentation, website, API specifications, YouTube videos, and GitHub content. Only available in the hosted Airbyte MCP. |
