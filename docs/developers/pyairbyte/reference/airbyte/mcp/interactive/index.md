---
id: airbyte-mcp-interactive-index
title: "airbyte.mcp.interactive Module"
sidebar_label: "airbyte.mcp.interactive"
toc_max_heading_level: 5
---

# `airbyte.mcp.interactive` Module

Interactive MCP tools for UI-capable clients.

### `register_interactive_tools` {#airbyte.mcp.interactive.register_interactive_tools}

<ApiMember kind="function">

<ApiSignature>

```python
def register_interactive_tools(app: FastMCP) -> None
```

</ApiSignature>

Register UI-presenting tools.

</ApiMember>

### `show_connection_sync_history` {#airbyte.mcp.interactive.show_connection_sync_history}

<ApiMember kind="function">

<ApiSignature>

```python
def show_connection_sync_history(
    connection_id: "Annotated[str, Field(description='The ID of the Airbyte Cloud connection to show sync history for.')]",
    ctx: Context = <fastmcp.server.dependencies._CurrentContext object>,
    *,
    workspace_id: Annotated[str | None, Field(description=WORKSPACE_ID_TIP_TEXT, default=None)] = None,
    max_jobs: "Annotated[int, Field(description='Maximum number of recent sync jobs to display. Defaults to 30. Maximum allowed value is 100.', default=30, ge=1, le=100)]" = 30,
    agent_context: Annotated[Literal[\'verbose\', \'summary\', \'min\'], Field(description="Controls how much context is returned to the agent in the text response. \'verbose\': full job-level data for detailed follow-up analysis. \'summary\': aggregates and key observations only. \'min\': one-liner confirmation that the dashboard rendered.", default=\'min\')] = 'min',
    suppress_ui: "Annotated[bool, Field(description='If True, skip rendering the visual dashboard and return only the agent text response. Use this for follow-up data retrieval without re-rendering the UI that the user has already seen.', default=False)]" = False,
) -> fastmcp.tools.base.ToolResult
```

</ApiSignature>

Show interactive sync history dashboard for an Airbyte Cloud connection.

    Renders a rich UI with metrics (success rate, total records, total bytes),
    charts (success/fail by date, records over time, bytes over time), and
    a detailed job history table.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

</ApiMember>

### `show_connectors_list` {#airbyte.mcp.interactive.show_connectors_list}

<ApiMember kind="function">

<ApiSignature>

```python
def show_connectors_list(
    support_level: typing.Annotated[str, FieldInfo(annotation=NoneType, required=True, description='Exact support level to match, such as `certified`, `community`, or `archived`. Empty string means no filter.')] = '',
    certified: typing.Annotated[bool, FieldInfo(annotation=NoneType, required=True, description="When `True`, return only certified connectors. Shorthand for `support_level='certified'`.")] = False,
    min_support_level: typing.Annotated[str, FieldInfo(annotation=NoneType, required=True, description='Minimum support level threshold. Levels: `archived` < `community` < `certified`. Empty string means no filter.')] = '',
    connector_type: typing.Annotated[str, FieldInfo(annotation=NoneType, required=True, description='Filter by connector type: `source` or `destination`. Empty string means no filter.')] = '',
    search: typing.Annotated[str, FieldInfo(annotation=NoneType, required=True, description='Case-insensitive search across connector name, display name, definition ID, Docker repository, subtype, and docs URL.')] = '',
    limit: typing.Annotated[int, FieldInfo(annotation=NoneType, required=True, description='Maximum number of connectors to return. Use `0` for no limit.', metadata=[Ge(ge=0)])] = 0,
) -> fastmcp.tools.base.ToolResult
```

</ApiSignature>

Show an interactive public connector catalog from the OSS registry.

</ApiMember>

### `show_workspace_sync_status` {#airbyte.mcp.interactive.show_workspace_sync_status}

<ApiMember kind="function">

<ApiSignature>

```python
def show_workspace_sync_status(
    ctx: Context = <fastmcp.server.dependencies._CurrentContext object>,
    *,
    workspace_id: Annotated[str | None, Field(description=WORKSPACE_ID_TIP_TEXT, default=None)] = None,
    max_connections: "Annotated[int, Field(description='Maximum number of workspace connections to inspect. Defaults to 50. Maximum allowed value is 100.', default=50, ge=1, le=100)]" = 50,
    max_jobs_per_connection: "Annotated[int, Field(description='Maximum number of recent jobs to inspect for each connection. Defaults to 5. Maximum allowed value is 10.', default=5, ge=1, le=10)]" = 5,
    recent_hours: "Annotated[int, Field(description='Window, in hours, used for the Recently Synced metric. Defaults to 24.', default=_RECENT_HOURS_DEFAULT, ge=1, le=720)]" = 24,
    agent_context: Annotated[Literal[\'verbose\', \'summary\', \'min\'], Field(description="Controls how much context is returned to the agent in the text response. \'verbose\': capped connection-level data for follow-up analysis. \'summary\': aggregates and key observations only. \'min\': one-liner confirmation that the dashboard rendered.", default=\'min\')] = 'min',
    suppress_ui: "Annotated[bool, Field(description='If True, skip rendering the visual dashboard and return only the agent text response. Use this for follow-up data retrieval without re-rendering the UI that the user has already seen.', default=False)]" = False,
) -> fastmcp.tools.base.ToolResult
```

</ApiSignature>

Show an interactive sync status dashboard for an Airbyte Cloud workspace.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

</ApiMember>