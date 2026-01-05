---
sidebar_label: connections
title: airbyte.cloud.connections
---

Cloud Connections.

## annotations

## TYPE\_CHECKING

## Any

## api\_util

## CloudDestination

## CloudSource

## SyncResult

## AirbyteWorkspaceMismatchError

## CloudConnection Objects

```python
class CloudConnection()
```

A connection is an extract-load (EL) pairing of a source and destination in Airbyte Cloud.

You can use a connection object to run sync jobs, retrieve logs, and manage the connection.

#### \_\_init\_\_

```python
def __init__(workspace: CloudWorkspace,
             connection_id: str,
             source: str | None = None,
             destination: str | None = None) -> None
```

It is not recommended to create a `CloudConnection` object directly.

Instead, use `CloudWorkspace.get_connection()` to create a connection object.

#### \_fetch\_connection\_info

```python
def _fetch_connection_info(*,
                           force_refresh: bool = False,
                           verify: bool = True) -> ConnectionResponse
```

Fetch and cache connection info from the API.

By default, this method will only fetch from the API if connection info is not
already cached. It also verifies that the connection belongs to the expected
workspace unless verification is explicitly disabled.

**Arguments**:

- `force_refresh` - If True, always fetch from the API even if cached.
  If False (default), only fetch if not already cached.
- `verify` - If True (default), verify that the connection is valid (e.g., that
  the workspace_id matches this object&#x27;s workspace). Raises an error if
  validation fails.
  

**Returns**:

  The ConnectionResponse from the API.
  

**Raises**:

- `AirbyteWorkspaceMismatchError` - If verify is True and the connection&#x27;s
  workspace_id doesn&#x27;t match the expected workspace.
- `AirbyteMissingResourceError` - If the connection doesn&#x27;t exist.

#### \_verify\_workspace\_match

```python
def _verify_workspace_match(connection_info: ConnectionResponse) -> None
```

Verify that the connection belongs to the expected workspace.

**Raises**:

- `AirbyteWorkspaceMismatchError` - If the workspace IDs don&#x27;t match.

#### check\_is\_valid

```python
def check_is_valid() -> bool
```

Check if this connection exists and belongs to the expected workspace.

This method fetches connection info from the API (if not already cached) and
verifies that the connection&#x27;s workspace_id matches the workspace associated
with this CloudConnection object.

**Returns**:

  True if the connection exists and belongs to the expected workspace.
  

**Raises**:

- `AirbyteWorkspaceMismatchError` - If the connection belongs to a different workspace.
- `AirbyteMissingResourceError` - If the connection doesn&#x27;t exist.

#### \_from\_connection\_response

```python
@classmethod
def _from_connection_response(
        cls, workspace: CloudWorkspace,
        connection_response: ConnectionResponse) -> CloudConnection
```

Create a CloudConnection from a ConnectionResponse.

#### name

```python
@property
def name() -> str | None
```

Get the display name of the connection, if available.

E.g. &quot;My Postgres to Snowflake&quot;, not the connection ID.

#### source\_id

```python
@property
def source_id() -> str
```

The ID of the source.

#### source

```python
@property
def source() -> CloudSource
```

Get the source object.

#### destination\_id

```python
@property
def destination_id() -> str
```

The ID of the destination.

#### destination

```python
@property
def destination() -> CloudDestination
```

Get the destination object.

#### stream\_names

```python
@property
def stream_names() -> list[str]
```

The stream names.

#### table\_prefix

```python
@property
def table_prefix() -> str
```

The table prefix.

#### connection\_url

```python
@property
def connection_url() -> str | None
```

The web URL to the connection.

#### job\_history\_url

```python
@property
def job_history_url() -> str | None
```

The URL to the job history for the connection.

#### run\_sync

```python
def run_sync(*, wait: bool = True, wait_timeout: int = 300) -> SyncResult
```

Run a sync.

#### \_\_repr\_\_

```python
def __repr__() -> str
```

String representation of the connection.

#### get\_previous\_sync\_logs

```python
def get_previous_sync_logs(*,
                           limit: int = 20,
                           offset: int | None = None,
                           from_tail: bool = True) -> list[SyncResult]
```

Get previous sync jobs for a connection with pagination support.

Returns SyncResult objects containing job metadata (job_id, status, bytes_synced,
rows_synced, start_time). Full log text can be fetched lazily via
`SyncResult.get_full_log_text()`.

**Arguments**:

- `limit` - Maximum number of jobs to return. Defaults to 20.
- `offset` - Number of jobs to skip from the beginning. Defaults to None (0).
- `from_tail` - If True, returns jobs ordered newest-first (createdAt DESC).
  If False, returns jobs ordered oldest-first (createdAt ASC).
  Defaults to True.
  

**Returns**:

  A list of SyncResult objects representing the sync jobs.

#### get\_sync\_result

```python
def get_sync_result(job_id: int | None = None) -> SyncResult | None
```

Get the sync result for the connection.

If `job_id` is not provided, the most recent sync job will be used.

Returns `None` if job_id is omitted and no previous jobs are found.

#### get\_state\_artifacts

```python
def get_state_artifacts() -> list[dict[str, Any]] | None
```

Get the connection state artifacts.

Returns the persisted state for this connection, which can be used
when debugging incremental syncs.

Uses the Config API endpoint: POST /v1/state/get

**Returns**:

  List of state objects for each stream, or None if no state is set.

#### get\_catalog\_artifact

```python
def get_catalog_artifact() -> dict[str, Any] | None
```

Get the configured catalog for this connection.

Returns the full configured catalog (syncCatalog) for this connection,
including stream schemas, sync modes, cursor fields, and primary keys.

Uses the Config API endpoint: POST /v1/web_backend/connections/get

**Returns**:

  Dictionary containing the configured catalog, or `None` if not found.

#### rename

```python
def rename(name: str) -> CloudConnection
```

Rename the connection.

**Arguments**:

- `name` - New name for the connection
  

**Returns**:

  Updated CloudConnection object with refreshed info

#### set\_table\_prefix

```python
def set_table_prefix(prefix: str) -> CloudConnection
```

Set the table prefix for the connection.

**Arguments**:

- `prefix` - New table prefix to use when syncing to the destination
  

**Returns**:

  Updated CloudConnection object with refreshed info

#### set\_selected\_streams

```python
def set_selected_streams(stream_names: list[str]) -> CloudConnection
```

Set the selected streams for the connection.

This is a destructive operation that can break existing connections if the
stream selection is changed incorrectly. Use with caution.

**Arguments**:

- `stream_names` - List of stream names to sync
  

**Returns**:

  Updated CloudConnection object with refreshed info

#### enabled

```python
@property
def enabled() -> bool
```

Get the current enabled status of the connection.

This property always fetches fresh data from the API to ensure accuracy,
as another process or user may have toggled the setting.

**Returns**:

  True if the connection status is &#x27;active&#x27;, False otherwise.

#### enabled

```python
@enabled.setter
def enabled(value: bool) -> None
```

Set the enabled status of the connection.

**Arguments**:

- `value` - True to enable (set status to &#x27;active&#x27;), False to disable
  (set status to &#x27;inactive&#x27;).

#### set\_enabled

```python
def set_enabled(*, enabled: bool, ignore_noop: bool = True) -> None
```

Set the enabled status of the connection.

**Arguments**:

- `enabled` - True to enable (set status to &#x27;active&#x27;), False to disable
  (set status to &#x27;inactive&#x27;).
- `ignore_noop` - If True (default), silently return if the connection is already
  in the requested state. If False, raise ValueError when the requested
  state matches the current state.
  

**Raises**:

- `ValueError` - If ignore_noop is False and the connection is already in the
  requested state.

#### set\_schedule

```python
def set_schedule(cron_expression: str) -> None
```

Set a cron schedule for the connection.

**Arguments**:

- `cron_expression` - A cron expression defining when syncs should run.
  

**Examples**:

  - &quot;0 0 * * *&quot; - Daily at midnight UTC
  - &quot;0 */6 * * *&quot; - Every 6 hours
  - &quot;0 0 * * 0&quot; - Weekly on Sunday at midnight UTC

#### set\_manual\_schedule

```python
def set_manual_schedule() -> None
```

Set the connection to manual scheduling.

Disables automatic syncs. Syncs will only run when manually triggered.

#### permanently\_delete

```python
def permanently_delete(*,
                       cascade_delete_source: bool = False,
                       cascade_delete_destination: bool = False) -> None
```

Delete the connection.

**Arguments**:

- `cascade_delete_source` - Whether to also delete the source.
- `cascade_delete_destination` - Whether to also delete the destination.

