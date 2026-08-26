---
id: airbyte-cloud-connections
title: airbyte.cloud.connections
---

Cloud Connections.

### `CloudConnection` {#airbyte.cloud.connections.CloudConnection}

<ApiMember kind="class">

<ApiSignature>

```python
class CloudConnection(
    workspace: CloudWorkspace,
    connection_id: str,
    source: str | None = None,
    destination: str | None = None,
)
```

</ApiSignature>

A connection is an extract-load (EL) pairing of a source and destination in Airbyte Cloud.

You can use a connection object to run sync jobs, retrieve logs, and manage the connection.

It is not recommended to create a `CloudConnection` object directly.

Instead, use `CloudWorkspace.get_connection()` to create a connection object.

#### Attributes {#airbyte.cloud.connections.CloudConnection--attributes}

- **`connection_id`** — The ID of the connection.

- **`connection_url`**&nbsp;(`str | None`) — The web URL to the connection.

- **`destination`**&nbsp;(`CloudDestination`) — Get the destination object.

- **`destination_id`**&nbsp;(`str`) — The ID of the destination.

- **`enabled`**&nbsp;(`bool`) — Get the current enabled status of the connection.  This property always fetches fresh data from the API to ensure accuracy, as another process or user may have toggled the setting.   **Returns:**  True if the connection status is 'active', False otherwise. 

- **`job_history_url`**&nbsp;(`str | None`) — The URL to the job history for the connection.

- **`name`**&nbsp;(`str | None`) — Get the display name of the connection, if available.  E.g. "My Postgres to Snowflake", not the connection ID.

- **`source`**&nbsp;(`CloudSource`) — Get the source object.

- **`source_id`**&nbsp;(`str`) — The ID of the source.

- **`stream_names`**&nbsp;(`list[str]`) — The stream names.

- **`table_prefix`**&nbsp;(`str`) — The table prefix.

- **`workspace`** — The workspace that the connection belongs to.

#### `cancel_sync` {#airbyte.cloud.connections.CloudConnection.cancel_sync}

<ApiMember kind="method">

<ApiSignature>

```python
def cancel_sync(
    self,
    job_id: int | None = None,
) -> airbyte.cloud.sync_results.SyncResult
```

</ApiSignature>

Cancel a running sync job.

Defaults to the connection's most recent sync job. Other job types must be
targeted with an explicit `job_id`.

</ApiMember>

#### `check_is_valid` {#airbyte.cloud.connections.CloudConnection.check_is_valid}

<ApiMember kind="method">

<ApiSignature>

```python
def check_is_valid(self) -> bool
```

</ApiSignature>

Check if this connection exists and belongs to the expected workspace.

This method fetches connection info from the API (if not already cached) and
verifies that the connection's workspace_id matches the workspace associated
with this CloudConnection object.

**Returns:**

True if the connection exists and belongs to the expected workspace.

**Raises:**

- **`AirbyteWorkspaceMismatchError`**: If the connection belongs to a different workspace.
- **`AirbyteMissingResourceError`**: If the connection doesn't exist.

</ApiMember>

#### `dump_raw_catalog` {#airbyte.cloud.connections.CloudConnection.dump_raw_catalog}

<ApiMember kind="method">

<ApiSignature>

```python
def dump_raw_catalog(
    self,
    *,
    normalize: bool = True,
) -> dict[str, typing.Any] | None
```

</ApiSignature>

Dump the configured catalog for this connection.

By default, returns the catalog in Airbyte protocol format
(`ConfiguredAirbyteCatalog` with snake_case keys), suitable for passing
to a connector's `--catalog` flag.

When `normalize` is `False`, returns the raw `syncCatalog` dict from the
Config API (camelCase keys, nested `config` block). This raw format can be
passed directly to `import_raw_catalog()` for backup/restore workflows.

**Args:**

- **`normalize`**: If `True` (default), convert to Airbyte protocol format. If `False`, return the raw Config API catalog.

**Returns:**

The configured catalog dict, or `None` if not found.

</ApiMember>

#### `dump_raw_state` {#airbyte.cloud.connections.CloudConnection.dump_raw_state}

<ApiMember kind="method">

<ApiSignature>

```python
def dump_raw_state(
    self,
    *,
    normalize: bool = True,
) -> dict[str, typing.Any] | list[dict[str, typing.Any]]
```

</ApiSignature>

Dump the state for this connection.

By default, returns a list of Airbyte protocol `AirbyteStateMessage` dicts
with snake_case keys, suitable for passing to a connector's `--state` flag.

When `normalize` is `False`, returns the raw Config API dict (camelCase keys,
includes `stateType` and `connectionId`). This raw format can be passed
directly to `import_raw_state()` for backup/restore workflows.

**Args:**

- **`normalize`**: If `True` (default), convert to Airbyte protocol format. If `False`, return the raw Config API response.

**Returns:**

- **`Normalized`**: list of protocol-format state message dicts (empty list if no state). Raw: the full Config API state dict.

</ApiMember>

#### `get_catalog_artifact` {#airbyte.cloud.connections.CloudConnection.get_catalog_artifact}

<ApiMember kind="method">

<ApiSignature>

```python
def get_catalog_artifact(self) -> dict[str, typing.Any] | None
```

</ApiSignature>

Get the configured catalog for this connection.

Returns the full configured catalog (syncCatalog) for this connection,
including stream schemas, sync modes, cursor fields, and primary keys.

Uses the Config API endpoint: POST /v1/web_backend/connections/get

**Returns:**

Dictionary containing the configured catalog, or `None` if not found.

</ApiMember>

#### `get_previous_sync_logs` {#airbyte.cloud.connections.CloudConnection.get_previous_sync_logs}

<ApiMember kind="method">

<ApiSignature>

```python
def get_previous_sync_logs(
    self,
    *,
    limit: int = 20,
    offset: int | None = None,
    from_tail: bool = True,
    job_type: str | JobTypeEnum | None = None,
) -> list[airbyte.cloud.sync_results.SyncResult]
```

</ApiSignature>

Get previous sync jobs for a connection with pagination support.

Returns SyncResult objects containing job metadata (job_id, status, bytes_synced,
rows_synced, start_time). Full log text can be fetched lazily via
`SyncResult.get_full_log_text()`.

**Args:**

- **`limit`**: Maximum number of jobs to return. Defaults to 20.
- **`offset`**: Number of jobs to skip from the beginning. Defaults to None (0).
- **`from_tail`**: If True, returns jobs ordered newest-first (createdAt DESC). If False, returns jobs ordered oldest-first (createdAt ASC). Defaults to True.
- **`job_type`**: Filter by job type (e.g., `sync`, `refresh`). If not specified, defaults to sync and reset jobs only (API default behavior).

**Returns:**

A list of SyncResult objects representing the sync jobs.

</ApiMember>

#### `get_state_artifacts` {#airbyte.cloud.connections.CloudConnection.get_state_artifacts}

<ApiMember kind="method">

<ApiSignature>

```python
def get_state_artifacts(self) -> list[dict[str, typing.Any]] | None
```

</ApiSignature>

Deprecated. Use `dump_raw_state()` instead.

</ApiMember>

#### `get_stream_state` {#airbyte.cloud.connections.CloudConnection.get_stream_state}

<ApiMember kind="method">

<ApiSignature>

```python
def get_stream_state(
    self,
    stream_name: str,
    stream_namespace: str | None = None,
) -> dict[str, typing.Any] | None
```

</ApiSignature>

Get the state blob for a single stream within this connection.

Returns just the stream's state dictionary (e.g., \{"cursor": "2024-01-01"\}),
not the full connection state envelope.

This is compatible with `stream`-type state and stream-level entries
within a `global`-type state. It is not compatible with `legacy` state.
To get or set the entire connection-level state artifact, use
`dump_raw_state` and `import_raw_state` instead.

**Args:**

- **`stream_name`**: The name of the stream to get state for.
- **`stream_namespace`**: The source-side stream namespace. This refers to the namespace from the source (e.g., database schema), not any destination namespace override set in connection advanced settings.

**Returns:**

The stream's state blob as a dictionary, or None if the stream is not found.

</ApiMember>

#### `get_sync_result` {#airbyte.cloud.connections.CloudConnection.get_sync_result}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sync_result(
    self,
    job_id: int | None = None,
) -> airbyte.cloud.sync_results.SyncResult | None
```

</ApiSignature>

Get the sync result for the connection.

If `job_id` is not provided, the most recent sync job will be used.

Returns `None` if job_id is omitted and no previous jobs are found.

</ApiMember>

#### `import_raw_catalog` {#airbyte.cloud.connections.CloudConnection.import_raw_catalog}

<ApiMember kind="method">

<ApiSignature>

```python
def import_raw_catalog(self, catalog: dict[str, Any]) -> None
```

</ApiSignature>

Replace the configured catalog for this connection.

> ⚠️ **WARNING:** Modifying the catalog directly is not recommended and
> could result in broken connections, and/or incorrect sync behavior.

Accepts a configured catalog dict and replaces the connection's entire
catalog with it. All other connection settings remain unchanged.

Accepts either format:

- **Config API format** (`syncCatalog` with camelCase keys and nested `config`):
  passed through directly.
- **Airbyte protocol format** (`ConfiguredAirbyteCatalog` with snake_case keys):
  automatically converted to Config API format before sending.

**Args:**

- **`catalog`**: The configured catalog dict in either format.

</ApiMember>

#### `import_raw_state` {#airbyte.cloud.connections.CloudConnection.import_raw_state}

<ApiMember kind="method">

<ApiSignature>

```python
def import_raw_state(
    self,
    connection_state: dict[str, Any] | list[dict[str, Any]],
) -> dict[str, typing.Any]
```

</ApiSignature>

Import (restore) the full state for this connection.

> ⚠️ **WARNING:** Modifying the state directly is not recommended and
> could result in broken connections, and/or incorrect sync behavior.

Replaces the entire connection state with the provided state blob.
Uses the safe variant that prevents updates while a sync is running (HTTP 423).

This is the counterpart to `dump_raw_state()` for backup/restore workflows.
The `connectionId` in the blob is always overridden with this connection's
ID, making state blobs portable across connections.

Accepts either format:

- **Config API format** (dict with `stateType`): passed through directly.
- **Airbyte protocol format** (list of `AirbyteStateMessage` dicts): automatically
  converted to Config API format before sending.

**Args:**

- **`connection_state`**: Connection state in either Config API or Airbyte protocol format.

**Returns:**

The updated connection state as a dictionary.

**Raises:**

- **`AirbyteConnectionSyncActiveError`**: If a sync is currently running on this connection (HTTP 423). Wait for the sync to complete before retrying.

</ApiMember>

#### `permanently_delete` {#airbyte.cloud.connections.CloudConnection.permanently_delete}

<ApiMember kind="method">

<ApiSignature>

```python
def permanently_delete(
    self,
    *,
    cascade_delete_source: bool = False,
    cascade_delete_destination: bool = False,
) -> None
```

</ApiSignature>

Delete the connection.

**Args:**

- **`cascade_delete_source`**: Whether to also delete the source.
- **`cascade_delete_destination`**: Whether to also delete the destination.

</ApiMember>

#### `rename` {#airbyte.cloud.connections.CloudConnection.rename}

<ApiMember kind="method">

<ApiSignature>

```python
def rename(self, name: str) -> airbyte.cloud.connections.CloudConnection
```

</ApiSignature>

Rename the connection.

**Args:**

- **`name`**: New name for the connection

**Returns:**

Updated CloudConnection object with refreshed info

</ApiMember>

#### `run_sync` {#airbyte.cloud.connections.CloudConnection.run_sync}

<ApiMember kind="method">

<ApiSignature>

```python
def run_sync(
    self,
    *,
    wait: bool = True,
    wait_timeout: int = 300,
) -> airbyte.cloud.sync_results.SyncResult
```

</ApiSignature>

Run a sync.

</ApiMember>

#### `set_enabled` {#airbyte.cloud.connections.CloudConnection.set_enabled}

<ApiMember kind="method">

<ApiSignature>

```python
def set_enabled(self, *, enabled: bool, ignore_noop: bool = True) -> None
```

</ApiSignature>

Set the enabled status of the connection.

**Args:**

- **`enabled`**: True to enable (set status to 'active'), False to disable (set status to 'inactive').
- **`ignore_noop`**: If True (default), silently return if the connection is already in the requested state. If False, raise ValueError when the requested state matches the current state.

**Raises:**

- **`ValueError`**: If ignore_noop is False and the connection is already in the requested state.

</ApiMember>

#### `set_manual_schedule` {#airbyte.cloud.connections.CloudConnection.set_manual_schedule}

<ApiMember kind="method">

<ApiSignature>

```python
def set_manual_schedule(self) -> None
```

</ApiSignature>

Set the connection to manual scheduling.

Disables automatic syncs. Syncs will only run when manually triggered.

</ApiMember>

#### `set_schedule` {#airbyte.cloud.connections.CloudConnection.set_schedule}

<ApiMember kind="method">

<ApiSignature>

```python
def set_schedule(self, cron_expression: str) -> None
```

</ApiSignature>

Set a cron schedule for the connection.

**Args:**

- **`cron_expression`**: A cron expression defining when syncs should run.

**Examples:**

- "0 0 * * *"  # Daily at midnight UTC
- "0 */6 * * *"  # Every 6 hours
- "0 0 * * 0"  # Weekly on Sunday at midnight UTC

</ApiMember>

#### `set_selected_streams` {#airbyte.cloud.connections.CloudConnection.set_selected_streams}

<ApiMember kind="method">

<ApiSignature>

```python
def set_selected_streams(
    self,
    stream_names: list[str],
) -> airbyte.cloud.connections.CloudConnection
```

</ApiSignature>

Set the selected streams for the connection.

This is a destructive operation that can break existing connections if the
stream selection is changed incorrectly. Use with caution.

**Args:**

- **`stream_names`**: List of stream names to sync

**Returns:**

Updated CloudConnection object with refreshed info

</ApiMember>

#### `set_stream_state` {#airbyte.cloud.connections.CloudConnection.set_stream_state}

<ApiMember kind="method">

<ApiSignature>

```python
def set_stream_state(
    self,
    stream_name: str,
    state_blob_dict: dict[str, Any],
    stream_namespace: str | None = None,
) -> None
```

</ApiSignature>

Set the state for a single stream within this connection.

Fetches the current full state, replaces only the specified stream's state,
then sends the full updated state back to the API. If the stream does not
exist in the current state, it is appended.

This is compatible with `stream`-type state and stream-level entries
within a `global`-type state. It is not compatible with `legacy` state.
To get or set the entire connection-level state artifact, use
`dump_raw_state` and `import_raw_state` instead.

Uses the safe variant that prevents updates while a sync is running (HTTP 423).

**Args:**

- **`stream_name`**: The name of the stream to update state for.
- **`state_blob_dict`**: The state blob dict for this stream (e.g., \{"cursor": "2024-01-01"\}).
- **`stream_namespace`**: The source-side stream namespace. This refers to the namespace from the source (e.g., database schema), not any destination namespace override set in connection advanced settings.

**Raises:**

- **`PyAirbyteInputError`**: If the connection state type is not supported for stream-level operations (not_set, legacy).
- **`AirbyteConnectionSyncActiveError`**: If a sync is currently running on this connection (HTTP 423). Wait for the sync to complete before retrying.

</ApiMember>

#### `set_table_prefix` {#airbyte.cloud.connections.CloudConnection.set_table_prefix}

<ApiMember kind="method">

<ApiSignature>

```python
def set_table_prefix(
    self,
    prefix: str,
) -> airbyte.cloud.connections.CloudConnection
```

</ApiSignature>

Set the table prefix for the connection.

**Args:**

- **`prefix`**: New table prefix to use when syncing to the destination

**Returns:**

Updated CloudConnection object with refreshed info

</ApiMember>

</ApiMember>