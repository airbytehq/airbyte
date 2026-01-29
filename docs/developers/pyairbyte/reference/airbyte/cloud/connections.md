---
id: airbyte-cloud-connections
title: airbyte.cloud.connections
---

Module airbyte.cloud.connections
================================
Cloud Connections.

Classes
-------

`CloudConnection(workspace: CloudWorkspace, connection_id: str, source: str | None = None, destination: str | None = None)`
:   A connection is an extract-load (EL) pairing of a source and destination in Airbyte Cloud.
    
    You can use a connection object to run sync jobs, retrieve logs, and manage the connection.
    
    It is not recommended to create a `CloudConnection` object directly.
    
    Instead, use `CloudWorkspace.get_connection()` to create a connection object.

    ### Instance variables

    `connection_id`
    :   The ID of the connection.

    `connection_url: str | None`
    :   The web URL to the connection.

    `destination: CloudDestination`
    :   Get the destination object.

    `destination_id: str`
    :   The ID of the destination.

    `enabled: bool`
    :   Get the current enabled status of the connection.
        
        This property always fetches fresh data from the API to ensure accuracy,
        as another process or user may have toggled the setting.
        
        Returns:
            True if the connection status is 'active', False otherwise.

    `job_history_url: str | None`
    :   The URL to the job history for the connection.

    `name: str | None`
    :   Get the display name of the connection, if available.
        
        E.g. "My Postgres to Snowflake", not the connection ID.

    `source: CloudSource`
    :   Get the source object.

    `source_id: str`
    :   The ID of the source.

    `stream_names: list[str]`
    :   The stream names.

    `table_prefix: str`
    :   The table prefix.

    `workspace`
    :   The workspace that the connection belongs to.

    ### Methods

    `check_is_valid(self) ‑> bool`
    :   Check if this connection exists and belongs to the expected workspace.
        
        This method fetches connection info from the API (if not already cached) and
        verifies that the connection's workspace_id matches the workspace associated
        with this CloudConnection object.
        
        Returns:
            True if the connection exists and belongs to the expected workspace.
        
        Raises:
            AirbyteWorkspaceMismatchError: If the connection belongs to a different workspace.
            AirbyteMissingResourceError: If the connection doesn't exist.

    `get_catalog_artifact(self) ‑> dict[str, typing.Any] | None`
    :   Get the configured catalog for this connection.
        
        Returns the full configured catalog (syncCatalog) for this connection,
        including stream schemas, sync modes, cursor fields, and primary keys.
        
        Uses the Config API endpoint: POST /v1/web_backend/connections/get
        
        Returns:
            Dictionary containing the configured catalog, or `None` if not found.

    `get_previous_sync_logs(self, *, limit: int = 20, offset: int | None = None, from_tail: bool = True) ‑> list[airbyte.cloud.sync_results.SyncResult]`
    :   Get previous sync jobs for a connection with pagination support.
        
        Returns SyncResult objects containing job metadata (job_id, status, bytes_synced,
        rows_synced, start_time). Full log text can be fetched lazily via
        `SyncResult.get_full_log_text()`.
        
        Args:
            limit: Maximum number of jobs to return. Defaults to 20.
            offset: Number of jobs to skip from the beginning. Defaults to None (0).
            from_tail: If True, returns jobs ordered newest-first (createdAt DESC).
                If False, returns jobs ordered oldest-first (createdAt ASC).
                Defaults to True.
        
        Returns:
            A list of SyncResult objects representing the sync jobs.

    `get_state_artifacts(self) ‑> list[dict[str, typing.Any]] | None`
    :   Get the connection state artifacts.
        
        Returns the persisted state for this connection, which can be used
        when debugging incremental syncs.
        
        Uses the Config API endpoint: POST /v1/state/get
        
        Returns:
            List of state objects for each stream, or None if no state is set.

    `get_sync_result(self, job_id: int | None = None) ‑> airbyte.cloud.sync_results.SyncResult | None`
    :   Get the sync result for the connection.
        
        If `job_id` is not provided, the most recent sync job will be used.
        
        Returns `None` if job_id is omitted and no previous jobs are found.

    `permanently_delete(self, *, cascade_delete_source: bool = False, cascade_delete_destination: bool = False) ‑> None`
    :   Delete the connection.
        
        Args:
            cascade_delete_source: Whether to also delete the source.
            cascade_delete_destination: Whether to also delete the destination.

    `rename(self, name: str) ‑> airbyte.cloud.connections.CloudConnection`
    :   Rename the connection.
        
        Args:
            name: New name for the connection
        
        Returns:
            Updated CloudConnection object with refreshed info

    `run_sync(self, *, wait: bool = True, wait_timeout: int = 300) ‑> airbyte.cloud.sync_results.SyncResult`
    :   Run a sync.

    `set_enabled(self, *, enabled: bool, ignore_noop: bool = True) ‑> None`
    :   Set the enabled status of the connection.
        
        Args:
            enabled: True to enable (set status to 'active'), False to disable
                (set status to 'inactive').
            ignore_noop: If True (default), silently return if the connection is already
                in the requested state. If False, raise ValueError when the requested
                state matches the current state.
        
        Raises:
            ValueError: If ignore_noop is False and the connection is already in the
                requested state.

    `set_manual_schedule(self) ‑> None`
    :   Set the connection to manual scheduling.
        
        Disables automatic syncs. Syncs will only run when manually triggered.

    `set_schedule(self, cron_expression: str) ‑> None`
    :   Set a cron schedule for the connection.
        
        Args:
            cron_expression: A cron expression defining when syncs should run.
        
        Examples:
                - "0 0 * * *" - Daily at midnight UTC
                - "0 */6 * * *" - Every 6 hours
                - "0 0 * * 0" - Weekly on Sunday at midnight UTC

    `set_selected_streams(self, stream_names: list[str]) ‑> airbyte.cloud.connections.CloudConnection`
    :   Set the selected streams for the connection.
        
        This is a destructive operation that can break existing connections if the
        stream selection is changed incorrectly. Use with caution.
        
        Args:
            stream_names: List of stream names to sync
        
        Returns:
            Updated CloudConnection object with refreshed info

    `set_table_prefix(self, prefix: str) ‑> airbyte.cloud.connections.CloudConnection`
    :   Set the table prefix for the connection.
        
        Args:
            prefix: New table prefix to use when syncing to the destination
        
        Returns:
            Updated CloudConnection object with refreshed info