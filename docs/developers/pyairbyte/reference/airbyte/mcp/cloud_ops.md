---
id: airbyte-mcp-cloud_ops
title: airbyte.mcp.cloud_ops
---

Module airbyte.mcp.cloud_ops
============================
Airbyte Cloud MCP operations.

Functions
---------

`check_airbyte_cloud_workspace(*, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')]) ‑> airbyte.mcp.cloud_ops.CloudWorkspaceResult`
:   Check if we have a valid Airbyte Cloud connection and return workspace info.
    
    Returns workspace details including workspace ID, name, and organization info.

`create_connection_on_cloud(connection_name: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The name of the connection.')], source_id: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The ID of the deployed source.')], destination_id: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The ID of the deployed destination.')], selected_streams: Annotated[str | list[str], FieldInfo(annotation=NoneType, required=True, description="The selected stream names to sync within the connection. Must be an explicit stream name or list of streams. Cannot be empty or '*'.")], *, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')], table_prefix: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Optional table prefix to use when syncing to the destination.')]) ‑> str`
:   Create a connection between a deployed source and destination on Airbyte Cloud.

`deploy_destination_to_cloud(destination_name: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The name to use when deploying the destination.')], destination_connector_name: Annotated[str, FieldInfo(annotation=NoneType, required=True, description="The name of the destination connector (e.g., 'destination-postgres').")], *, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')], config: Annotated[dict | str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='The configuration for the destination connector.')], config_secret_name: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='The name of the secret containing the configuration.')], unique: Annotated[bool, FieldInfo(annotation=NoneType, required=False, default=True, description='Whether to require a unique name.')]) ‑> str`
:   Deploy a destination connector to Airbyte Cloud.

`deploy_noop_destination_to_cloud(name: str = 'No-op Destination', *, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')], unique: bool = True) ‑> str`
:   Deploy the No-op destination to Airbyte Cloud for testing purposes.

`deploy_source_to_cloud(source_name: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The name to use when deploying the source.')], source_connector_name: Annotated[str, FieldInfo(annotation=NoneType, required=True, description="The name of the source connector (e.g., 'source-faker').")], *, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')], config: Annotated[dict | str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='The configuration for the source connector.')], config_secret_name: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='The name of the secret containing the configuration.')], unique: Annotated[bool, FieldInfo(annotation=NoneType, required=False, default=True, description='Whether to require a unique name.')]) ‑> str`
:   Deploy a source connector to Airbyte Cloud.

`describe_cloud_connection(connection_id: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The ID of the connection to describe.')], *, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')]) ‑> airbyte.mcp.cloud_ops.CloudConnectionDetails`
:   Get detailed information about a specific deployed connection.

`describe_cloud_destination(destination_id: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The ID of the destination to describe.')], *, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')]) ‑> airbyte.mcp.cloud_ops.CloudDestinationDetails`
:   Get detailed information about a specific deployed destination connector.

`describe_cloud_organization(*, organization_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Organization ID. Required if organization_name is not provided.')], organization_name: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Organization name (exact match). Required if organization_id is not provided.')]) ‑> airbyte.mcp.cloud_ops.CloudOrganizationResult`
:   Get details about a specific organization.
    
    Requires either organization_id OR organization_name (exact match) to be provided.
    This tool is useful for looking up an organization's ID from its name, or vice versa.

`describe_cloud_source(source_id: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The ID of the source to describe.')], *, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')]) ‑> airbyte.mcp.cloud_ops.CloudSourceDetails`
:   Get detailed information about a specific deployed source connector.

`get_cloud_sync_logs(connection_id: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The ID of the Airbyte Cloud connection.')], job_id: Annotated[int | None, FieldInfo(annotation=NoneType, required=True, description='Optional job ID. If not provided, the latest job will be used.')] = None, attempt_number: Annotated[int | None, FieldInfo(annotation=NoneType, required=True, description='Optional attempt number. If not provided, the latest attempt will be used.')] = None, *, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')], max_lines: Annotated[int, FieldInfo(annotation=NoneType, required=False, default=4000, description="Maximum number of lines to return. Defaults to 4000 if not specified. If '0' is provided, no limit is applied.")], from_tail: Annotated[bool | None, FieldInfo(annotation=NoneType, required=False, default=None, description="Pull from the end of the log text if total lines is greater than 'max_lines'. Defaults to True if `line_offset` is not specified. Cannot combine `from_tail=True` with `line_offset`.")], line_offset: Annotated[int | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Number of lines to skip from the beginning of the logs. Cannot be combined with `from_tail=True`.')]) ‑> airbyte.mcp.cloud_ops.LogReadResult`
:   Get the logs from a sync job attempt on Airbyte Cloud.

`get_cloud_sync_status(connection_id: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The ID of the Airbyte Cloud connection.')], job_id: Annotated[int | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Optional job ID. If not provided, the latest job will be used.')], *, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')], include_attempts: Annotated[bool, FieldInfo(annotation=NoneType, required=False, default=False, description='Whether to include detailed attempts information.')]) ‑> dict[str, typing.Any]`
:   Get the status of a sync job from the Airbyte Cloud.

`get_connection_artifact(connection_id: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The ID of the Airbyte Cloud connection.')], artifact_type: Annotated[Literal['state', 'catalog'], FieldInfo(annotation=NoneType, required=True, description="The type of artifact to retrieve: 'state' or 'catalog'.")], *, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')]) ‑> dict[str, typing.Any] | list[dict[str, typing.Any]]`
:   Get a connection artifact (state or catalog) from Airbyte Cloud.
    
    Retrieves the specified artifact for a connection:
    - 'state': Returns the persisted state for incremental syncs as a list of
      stream state objects, or \{"ERROR": "..."\} if no state is set.
    - 'catalog': Returns the configured catalog (syncCatalog) as a dict,
      or \{"ERROR": "..."\} if not found.

`get_custom_source_definition(definition_id: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The ID of the custom source definition to retrieve.')], *, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')]) ‑> dict[str, typing.Any]`
:   Get a custom YAML source definition from Airbyte Cloud, including its manifest.
    
    Returns the full definition details including the manifest YAML content,
    which can be used to inspect or store the connector configuration locally.
    
    Note: Only YAML (declarative) connectors are currently supported.
    Docker-based custom sources are not yet available.

`list_cloud_sync_jobs(connection_id: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The ID of the Airbyte Cloud connection.')], *, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')], max_jobs: Annotated[int, FieldInfo(annotation=NoneType, required=False, default=20, description='Maximum number of jobs to return. Defaults to 20 if not specified. Maximum allowed value is 500.')], from_tail: Annotated[bool | None, FieldInfo(annotation=NoneType, required=False, default=None, description='When True, jobs are ordered newest-first (createdAt DESC). When False, jobs are ordered oldest-first (createdAt ASC). Defaults to True if `jobs_offset` is not specified. Cannot combine `from_tail=True` with `jobs_offset`.')], jobs_offset: Annotated[int | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Number of jobs to skip from the beginning. Cannot be combined with `from_tail=True`.')]) ‑> airbyte.mcp.cloud_ops.SyncJobListResult`
:   List sync jobs for a connection with pagination support.
    
    This tool allows you to retrieve a list of sync jobs for a connection,
    with control over ordering and pagination. By default, jobs are returned
    newest-first (from_tail=True).

`list_cloud_workspaces(*, organization_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Organization ID. Required if organization_name is not provided.')], organization_name: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Organization name (exact match). Required if organization_id is not provided.')], name_contains: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Optional substring to filter workspaces by name (server-side filtering)')], max_items_limit: Annotated[int | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Optional maximum number of items to return (default: no limit)')]) ‑> list[airbyte.mcp.cloud_ops.CloudWorkspaceResult]`
:   List all workspaces in a specific organization.
    
    Requires either organization_id OR organization_name (exact match) to be provided.
    This tool will NOT list workspaces across all organizations - you must specify
    which organization to list workspaces from.

`list_custom_source_definitions(*, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')]) ‑> list[dict[str, typing.Any]]`
:   List custom YAML source definitions in the Airbyte Cloud workspace.
    
    Note: Only YAML (declarative) connectors are currently supported.
    Docker-based custom sources are not yet available.

`list_deployed_cloud_connections(*, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')], name_contains: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Optional case-insensitive substring to filter connections by name')], max_items_limit: Annotated[int | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Optional maximum number of items to return (default: no limit)')], with_connection_status: Annotated[bool | None, FieldInfo(annotation=NoneType, required=False, default=False, description="If True, include status info for each connection's most recent sync job")], failing_connections_only: Annotated[bool | None, FieldInfo(annotation=NoneType, required=False, default=False, description='If True, only return connections with failed/cancelled last sync')]) ‑> list[airbyte.mcp.cloud_ops.CloudConnectionResult]`
:   List all deployed connections in the Airbyte Cloud workspace.
    
    When with_connection_status is True, each connection result will include
    information about the most recent sync job status, skipping over any
    currently in-progress syncs to find the last completed job.
    
    When failing_connections_only is True, only connections where the most
    recent completed sync job failed or was cancelled will be returned.
    This implicitly enables with_connection_status.

`list_deployed_cloud_destination_connectors(*, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')], name_contains: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Optional case-insensitive substring to filter destinations by name')], max_items_limit: Annotated[int | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Optional maximum number of items to return (default: no limit)')]) ‑> list[airbyte.mcp.cloud_ops.CloudDestinationResult]`
:   List all deployed destination connectors in the Airbyte Cloud workspace.

`list_deployed_cloud_source_connectors(*, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')], name_contains: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Optional case-insensitive substring to filter sources by name')], max_items_limit: Annotated[int | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Optional maximum number of items to return (default: no limit)')]) ‑> list[airbyte.mcp.cloud_ops.CloudSourceResult]`
:   List all deployed source connectors in the Airbyte Cloud workspace.

`permanently_delete_cloud_connection(connection_id: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The ID of the connection to delete.')], name: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The expected name of the connection (for verification).')], *, cascade_delete_source: Annotated[bool, FieldInfo(annotation=NoneType, required=False, default=False, description='Whether to also delete the source connector associated with this connection.')] = False, cascade_delete_destination: Annotated[bool, FieldInfo(annotation=NoneType, required=False, default=False, description='Whether to also delete the destination connector associated with this connection.')] = False) ‑> str`
:   Permanently delete a connection from Airbyte Cloud.
    
    IMPORTANT: This operation requires the connection name to contain "delete-me" or "deleteme"
    (case insensitive).
    
    If the connection does not meet this requirement, the deletion will be rejected with a
    helpful error message. Instruct the user to rename the connection appropriately to authorize
    the deletion.
    
    The provided name must match the actual name of the connection for the operation to proceed.
    This is a safety measure to ensure you are deleting the correct resource.

`permanently_delete_cloud_destination(destination_id: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The ID of the deployed destination to delete.')], name: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The expected name of the destination (for verification).')]) ‑> str`
:   Permanently delete a deployed destination connector from Airbyte Cloud.
    
    IMPORTANT: This operation requires the destination name to contain "delete-me" or "deleteme"
    (case insensitive).
    
    If the destination does not meet this requirement, the deletion will be rejected with a
    helpful error message. Instruct the user to rename the destination appropriately to authorize
    the deletion.
    
    The provided name must match the actual name of the destination for the operation to proceed.
    This is a safety measure to ensure you are deleting the correct resource.

`permanently_delete_cloud_source(source_id: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The ID of the deployed source to delete.')], name: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The expected name of the source (for verification).')]) ‑> str`
:   Permanently delete a deployed source connector from Airbyte Cloud.
    
    IMPORTANT: This operation requires the source name to contain "delete-me" or "deleteme"
    (case insensitive).
    
    If the source does not meet this requirement, the deletion will be rejected with a
    helpful error message. Instruct the user to rename the source appropriately to authorize
    the deletion.
    
    The provided name must match the actual name of the source for the operation to proceed.
    This is a safety measure to ensure you are deleting the correct resource.

`permanently_delete_custom_source_definition(definition_id: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The ID of the custom source definition to delete.')], name: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The expected name of the custom source definition (for verification).')], *, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')]) ‑> str`
:   Permanently delete a custom YAML source definition from Airbyte Cloud.
    
    IMPORTANT: This operation requires the connector name to contain "delete-me" or "deleteme"
    (case insensitive).
    
    If the connector does not meet this requirement, the deletion will be rejected with a
    helpful error message. Instruct the user to rename the connector appropriately to authorize
    the deletion.
    
    The provided name must match the actual name of the definition for the operation to proceed.
    This is a safety measure to ensure you are deleting the correct resource.
    
    Note: Only YAML (declarative) connectors are currently supported.
    Docker-based custom sources are not yet available.

`publish_custom_source_definition(name: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The name for the custom connector definition.')], *, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')], manifest_yaml: Annotated[str | pathlib.Path | None, FieldInfo(annotation=NoneType, required=False, default=None, description='The Low-code CDK manifest as a YAML string or file path. Required for YAML connectors.')] = None, unique: Annotated[bool, FieldInfo(annotation=NoneType, required=False, default=True, description='Whether to require a unique name.')] = True, pre_validate: Annotated[bool, FieldInfo(annotation=NoneType, required=False, default=True, description='Whether to validate the manifest client-side before publishing.')] = True, testing_values: Annotated[dict | str | None, FieldInfo(annotation=NoneType, required=False, default=None, description="Optional testing configuration values for the Builder UI. Can be provided as a JSON object or JSON string. Supports inline secret refs via 'secret_reference::ENV_VAR_NAME' syntax. If provided, these values replace any existing testing values for the connector builder project, allowing immediate test read operations.")], testing_values_secret_name: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Optional name of a secret containing testing configuration values in JSON or YAML format. The secret will be resolved by the MCP server and merged into testing_values, with secret values taking precedence. This lets the agent reference secrets without sending raw values as tool arguments.')]) ‑> str`
:   Publish a custom YAML source connector definition to Airbyte Cloud.
    
    Note: Only YAML (declarative) connectors are currently supported.
    Docker-based custom sources are not yet available.

`register_cloud_ops_tools(app: fastmcp.server.server.FastMCP) ‑> None`
:   @private Register tools with the FastMCP app.
    
    This is an internal function and should not be called directly.
    
    Tools are filtered based on mode settings:
    - AIRBYTE_CLOUD_MCP_READONLY_MODE=1: Only read-only tools are registered
    - AIRBYTE_CLOUD_MCP_SAFE_MODE=1: All tools are registered, but destructive
      operations are protected by runtime session checks

`rename_cloud_connection(connection_id: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The ID of the connection to rename.')], name: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='New name for the connection.')], *, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')]) ‑> str`
:   Rename a connection on Airbyte Cloud.

`rename_cloud_destination(destination_id: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The ID of the deployed destination to rename.')], name: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='New name for the destination.')], *, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')]) ‑> str`
:   Rename a deployed destination connector on Airbyte Cloud.

`rename_cloud_source(source_id: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The ID of the deployed source to rename.')], name: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='New name for the source.')], *, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')]) ‑> str`
:   Rename a deployed source connector on Airbyte Cloud.

`run_cloud_sync(connection_id: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The ID of the Airbyte Cloud connection.')], *, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')], wait: Annotated[bool, FieldInfo(annotation=NoneType, required=False, default=False, description='Whether to wait for the sync to complete. Since a sync can take between several minutes and several hours, this option is not recommended for most scenarios.')], wait_timeout: Annotated[int, FieldInfo(annotation=NoneType, required=False, default=300, description='Maximum time to wait for sync completion (seconds).')]) ‑> str`
:   Run a sync job on Airbyte Cloud.

`set_cloud_connection_selected_streams(connection_id: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The ID of the connection to update.')], stream_names: Annotated[str | list[str], FieldInfo(annotation=NoneType, required=True, description='The selected stream names to sync within the connection. Must be an explicit stream name or list of streams.')], *, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')]) ‑> str`
:   Set the selected streams for a connection on Airbyte Cloud.
    
    This is a destructive operation that can break existing connections if the
    stream selection is changed incorrectly. Use with caution.

`set_cloud_connection_table_prefix(connection_id: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The ID of the connection to update.')], prefix: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='New table prefix to use when syncing to the destination.')], *, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')]) ‑> str`
:   Set the table prefix for a connection on Airbyte Cloud.
    
    This is a destructive operation that can break downstream dependencies if the
    table prefix is changed incorrectly. Use with caution.

`update_cloud_connection(connection_id: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The ID of the connection to update.')], *, enabled: Annotated[bool | None, FieldInfo(annotation=NoneType, required=False, default=None, description="Set the connection's enabled status. True enables the connection (status='active'), False disables it (status='inactive'). Leave unset to keep the current status.")], cron_expression: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description="A cron expression defining when syncs should run. Examples: '0 0 * * *' (daily at midnight UTC), '0 */6 * * *' (every 6 hours), '0 0 * * 0' (weekly on Sunday at midnight UTC). Leave unset to keep the current schedule. Cannot be used together with 'manual_schedule'.")], manual_schedule: Annotated[bool | None, FieldInfo(annotation=NoneType, required=False, default=None, description="Set to True to disable automatic syncs (manual scheduling only). Syncs will only run when manually triggered. Cannot be used together with 'cron_expression'.")], workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')]) ‑> str`
:   Update a connection's settings on Airbyte Cloud.
    
    This tool allows updating multiple connection settings in a single call:
    - Enable or disable the connection
    - Set a cron schedule for automatic syncs
    - Switch to manual scheduling (no automatic syncs)
    
    At least one setting must be provided. The 'cron_expression' and 'manual_schedule'
    parameters are mutually exclusive.

`update_cloud_destination_config(destination_id: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The ID of the deployed destination to update.')], config: Annotated[dict | str, FieldInfo(annotation=NoneType, required=True, description='New configuration for the destination connector.')], config_secret_name: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='The name of the secret containing the configuration.')], *, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')]) ‑> str`
:   Update a deployed destination connector's configuration on Airbyte Cloud.
    
    This is a destructive operation that can break existing connections if the
    configuration is changed incorrectly. Use with caution.

`update_cloud_source_config(source_id: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The ID of the deployed source to update.')], config: Annotated[dict | str, FieldInfo(annotation=NoneType, required=True, description='New configuration for the source connector.')], config_secret_name: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='The name of the secret containing the configuration.')] = None, *, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')]) ‑> str`
:   Update a deployed source connector's configuration on Airbyte Cloud.
    
    This is a destructive operation that can break existing connections if the
    configuration is changed incorrectly. Use with caution.

`update_custom_source_definition(definition_id: Annotated[str, FieldInfo(annotation=NoneType, required=True, description='The ID of the definition to update.')], manifest_yaml: Annotated[str | pathlib.Path | None, FieldInfo(annotation=NoneType, required=False, default=None, description='New manifest as YAML string or file path. Optional; omit to update only testing values.')] = None, *, workspace_id: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Workspace ID. Defaults to `AIRBYTE_CLOUD_WORKSPACE_ID` env var.')], pre_validate: Annotated[bool, FieldInfo(annotation=NoneType, required=False, default=True, description='Whether to validate the manifest client-side before updating.')] = True, testing_values: Annotated[dict | str | None, FieldInfo(annotation=NoneType, required=False, default=None, description="Optional testing configuration values for the Builder UI. Can be provided as a JSON object or JSON string. Supports inline secret refs via 'secret_reference::ENV_VAR_NAME' syntax. If provided, these values replace any existing testing values for the connector builder project. The entire testing values object is overwritten, so pass the full set of values you want to persist.")], testing_values_secret_name: Annotated[str | None, FieldInfo(annotation=NoneType, required=False, default=None, description='Optional name of a secret containing testing configuration values in JSON or YAML format. The secret will be resolved by the MCP server and merged into testing_values, with secret values taking precedence. This lets the agent reference secrets without sending raw values as tool arguments.')]) ‑> str`
:   Update a custom YAML source definition in Airbyte Cloud.
    
    Updates the manifest and/or testing values for an existing custom source definition.
    At least one of manifest_yaml, testing_values, or testing_values_secret_name must be provided.

Classes
-------

`CloudConnectionDetails(**data: Any)`
:   Detailed information about a deployed connection in Airbyte Cloud.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `connection_id: str`
    :   The connection ID.

    `connection_name: str`
    :   Display name of the connection.

    `connection_url: str`
    :   Web URL for managing this connection in Airbyte Cloud.

    `destination_id: str`
    :   ID of the destination used by this connection.

    `destination_name: str`
    :   Display name of the destination.

    `model_config`
    :

    `selected_streams: list[str]`
    :   List of stream names selected for syncing.

    `source_id: str`
    :   ID of the source used by this connection.

    `source_name: str`
    :   Display name of the source.

    `table_prefix: str | None`
    :   Table prefix applied when syncing to the destination.

`CloudConnectionResult(**data: Any)`
:   Information about a deployed connection in Airbyte Cloud.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `currently_running_job_id: int | None`
    :   Job ID of a currently running sync, if any.
        Only populated when with_connection_status=True.

    `currently_running_job_start_time: str | None`
    :   ISO 8601 timestamp of when the currently running sync started.
        Only populated when with_connection_status=True.

    `destination_id: str`
    :   ID of the destination used by this connection.

    `id: str`
    :   The connection ID.

    `last_job_id: int | None`
    :   Job ID of the most recent completed sync. Only populated when with_connection_status=True.

    `last_job_status: str | None`
    :   Status of the most recent completed sync job (e.g., 'succeeded', 'failed', 'cancelled').
        Only populated when with_connection_status=True.

    `last_job_time: str | None`
    :   ISO 8601 timestamp of the most recent completed sync.
        Only populated when with_connection_status=True.

    `model_config`
    :

    `name: str`
    :   Display name of the connection.

    `source_id: str`
    :   ID of the source used by this connection.

    `url: str`
    :   Web URL for managing this connection in Airbyte Cloud.

`CloudDestinationDetails(**data: Any)`
:   Detailed information about a deployed destination connector in Airbyte Cloud.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `connector_definition_id: str`
    :   The connector definition ID (e.g., the ID for 'destination-snowflake').

    `destination_id: str`
    :   The destination ID.

    `destination_name: str`
    :   Display name of the destination.

    `destination_url: str`
    :   Web URL for managing this destination in Airbyte Cloud.

    `model_config`
    :

`CloudDestinationResult(**data: Any)`
:   Information about a deployed destination connector in Airbyte Cloud.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str`
    :   The destination ID.

    `model_config`
    :

    `name: str`
    :   Display name of the destination.

    `url: str`
    :   Web URL for managing this destination in Airbyte Cloud.

`CloudOrganizationResult(**data: Any)`
:   Information about an organization in Airbyte Cloud.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str`
    :   Email associated with the organization.

    `id: str`
    :   The organization ID.

    `model_config`
    :

    `name: str`
    :   Display name of the organization.

`CloudSourceDetails(**data: Any)`
:   Detailed information about a deployed source connector in Airbyte Cloud.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `connector_definition_id: str`
    :   The connector definition ID (e.g., the ID for 'source-postgres').

    `model_config`
    :

    `source_id: str`
    :   The source ID.

    `source_name: str`
    :   Display name of the source.

    `source_url: str`
    :   Web URL for managing this source in Airbyte Cloud.

`CloudSourceResult(**data: Any)`
:   Information about a deployed source connector in Airbyte Cloud.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str`
    :   The source ID.

    `model_config`
    :

    `name: str`
    :   Display name of the source.

    `url: str`
    :   Web URL for managing this source in Airbyte Cloud.

`CloudWorkspaceResult(**data: Any)`
:   Information about a workspace in Airbyte Cloud.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :

    `organization_id: str`
    :   ID of the organization (requires ORGANIZATION_READER permission).

    `organization_name: str | None`
    :   Name of the organization (requires ORGANIZATION_READER permission).

    `workspace_id: str`
    :   The workspace ID.

    `workspace_name: str`
    :   Display name of the workspace.

    `workspace_url: str | None`
    :   URL to access the workspace in Airbyte Cloud.

`LogReadResult(**data: Any)`
:   Result of reading sync logs with pagination support.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attempt_number: int`
    :   The attempt number the logs belong to.

    `job_id: int`
    :   The job ID the logs belong to.

    `log_text: str`
    :   The string containing the log text we are returning.

    `log_text_line_count: int`
    :   Count of lines we are returning.

    `log_text_start_line: int`
    :   1-based line index of the first line returned.

    `model_config`
    :

    `total_log_lines_available: int`
    :   Total number of log lines available, shows if any lines were missed due to the limit.

`SyncJobListResult(**data: Any)`
:   Result of listing sync jobs with pagination support.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `from_tail: bool`
    :   Whether jobs are ordered newest-first (True) or oldest-first (False).

    `jobs: list[airbyte.mcp.cloud_ops.SyncJobResult]`
    :   List of sync jobs.

    `jobs_count: int`
    :   Number of jobs returned in this response.

    `jobs_offset: int`
    :   Offset used for this request (0 if not specified).

    `model_config`
    :

`SyncJobResult(**data: Any)`
:   Information about a sync job.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bytes_synced: int`
    :   Number of bytes synced in this job.

    `job_id: int`
    :   The job ID.

    `job_url: str`
    :   URL to view the job in Airbyte Cloud.

    `model_config`
    :

    `records_synced: int`
    :   Number of records synced in this job.

    `start_time: str`
    :   ISO 8601 timestamp of when the job started.

    `status: str`
    :   The job status (e.g., 'succeeded', 'failed', 'running', 'pending').