---
id: airbyte-cloud-index
title: airbyte.cloud.index
---

PyAirbyte classes and methods for interacting with the Airbyte Cloud API.

You can use this module to interact with Airbyte Cloud, OSS, and Enterprise.

## Self-managed Airbyte instances

For self-managed Airbyte instances, set `api_root` to the Public API root for your
deployment. For the default self-managed route, that usually ends in `/api/public/v1`.
PyAirbyte uses the Public API for workspace and organization discovery.

Some Cloud module methods also call the Config API, including methods such as
`CloudConnection.dump_raw_catalog()`, which reads the configured catalog directly
from Airbyte. For documented self-managed deployments where the Public API root ends in
`/api/public/v1`, PyAirbyte infers the Config API root by replacing that suffix with
`/api/v1`.

If your deployment uses custom ingress or a nonstandard reverse proxy, pass
`config_api_root` explicitly or set the `AIRBYTE_CLOUD_CONFIG_API_URL` environment
variable.

```python
from airbyte import cloud

workspace = cloud.CloudWorkspace(
    workspace_id="...",
    client_id="...",
    client_secret="...",
    api_root="https://airbyte.example.com/api/public/v1",
    config_api_root="https://airbyte.example.com/api/v1",
)

connection = workspace.get_connection(connection_id="...")
raw_catalog = connection.dump_raw_catalog()
```

## Examples

### Basic Sync Example:

```python
import airbyte as ab
from airbyte import cloud

# Initialize an Airbyte Cloud workspace object
workspace = cloud.CloudWorkspace(
    workspace_id="123",
    api_key=ab.get_secret("AIRBYTE_CLOUD_API_KEY"),
)

# Run a sync job on Airbyte Cloud
connection = workspace.get_connection(connection_id="456")
sync_result = connection.run_sync()
print(sync_result.get_job_status())
```

### Example Read From Cloud Destination:

If your destination is supported, you can read records directly from the
`SyncResult` object. Currently this is supported in Snowflake and BigQuery only.

```python
# Assuming we've already created a `connection` object...

# Get the latest job result and print the stream names
sync_result = connection.get_sync_result()
print(sync_result.stream_names)

# Get a dataset from the sync result
dataset: CachedDataset = sync_result.get_dataset("users")

# Get a SQLAlchemy table to use in SQL queries...
users_table = dataset.to_sql_table()
print(f"Table name: {users_table.name}")

# Or iterate over the dataset directly
for record in dataset:
    print(record)
```

- `airbyte.cloud.auth`
- `airbyte.cloud.client`
- `airbyte.cloud.client_config`
- `airbyte.cloud.connections`
- `airbyte.cloud.connectors`
- `airbyte.cloud.constants`
- `airbyte.cloud.models`
- `airbyte.cloud.organizations`
- `airbyte.cloud.sync_results`
- `airbyte.cloud.workspaces`

### `CloudClient` {#airbyte.cloud.CloudClient}

<ApiMember kind="class">

<ApiSignature>

```python
class CloudClient(
    *,
    client_id: str | SecretString | None = None,
    client_secret: str | SecretString | None = None,
    bearer_token: str | SecretString | None = None,
    public_api_root: str | None = None,
    config_api_root: str | None = None,
    workspace_id: str | None = None,
    organization_id: str | None = None,
)
```

</ApiSignature>

Authenticated client for Airbyte Cloud and self-managed Airbyte APIs.

Initialize a `CloudClient` from explicit auth values.

#### Attributes {#airbyte.cloud.CloudClient--attributes}

- **`bearer_token`**&nbsp;(`SecretString | None`) — Bearer token used for authentication.

- **`client_id`**&nbsp;(`SecretString | None`) — OAuth client ID used for authentication.

- **`client_secret`**&nbsp;(`SecretString | None`) — OAuth client secret used for authentication.

- **`config_api_root`**&nbsp;(`str | None`) — Airbyte Config API root.

- **`organization_id`**&nbsp;(`str | None`) — Default organization ID for organization-scoped operations.

- **`public_api_root`**&nbsp;(`str`) — Airbyte Public API root.

#### `from_auth` {#airbyte.cloud.CloudClient.from_auth}

<ApiMember kind="method">

<ApiSignature>

```python
def from_auth(
    *,
    env_vars: bool = False,
    organization_id: str | None = None,
    client_id: str | SecretString | None = None,
    client_secret: str | SecretString | None = None,
    bearer_token: str | SecretString | None = None,
    public_api_root: str | None = None,
    config_api_root: str | None = None,
)
```

</ApiSignature>

Create a client from explicit inputs and optionally environment variables.

When `env_vars` is True, environment variables are checked as a fallback
after any explicitly provided values.

</ApiMember>

#### `create_workspace` {#airbyte.cloud.CloudClient.create_workspace}

<ApiMember kind="method">

<ApiSignature>

```python
def create_workspace(
    self,
    *,
    name: str,
    organization_id: str | None = None,
    region_id: str | None = None,
) -> airbyte.cloud.models.CloudWorkspaceInfo
```

</ApiSignature>

Create an Airbyte workspace.

</ApiMember>

#### `get_organization` {#airbyte.cloud.CloudClient.get_organization}

<ApiMember kind="method">

<ApiSignature>

```python
def get_organization(
    self,
    organization_id: str | None = None,
    *,
    organization_name: str | None = None,
) -> airbyte.cloud.organizations.CloudOrganization
```

</ApiSignature>

Resolve an organization by ID or exact name.

</ApiMember>

#### `get_workspace` {#airbyte.cloud.CloudClient.get_workspace}

<ApiMember kind="method">

<ApiSignature>

```python
def get_workspace(
    self,
    workspace_id: str | None = None,
) -> airbyte.cloud.workspaces.CloudWorkspace
```

</ApiSignature>

Create a `CloudWorkspace` using this client's credentials.

</ApiMember>

#### `list_organizations` {#airbyte.cloud.CloudClient.list_organizations}

<ApiMember kind="method">

<ApiSignature>

```python
def list_organizations(
    self,
) -> list[airbyte.cloud.organizations.CloudOrganization]
```

</ApiSignature>

List all organizations available to this client.

</ApiMember>

#### `list_workspaces` {#airbyte.cloud.CloudClient.list_workspaces}

<ApiMember kind="method">

<ApiSignature>

```python
def list_workspaces(
    self,
    name: str | None = None,
    *,
    organization_id: str | None = None,
    name_contains: str | None = None,
    name_filter: Callable[[str], bool] | None = None,
    limit: int | None = None,
) -> list[CloudWorkspaceInfo]
```

</ApiSignature>

List workspaces available to this client.

</ApiMember>

#### `permanently_delete_workspace` {#airbyte.cloud.CloudClient.permanently_delete_workspace}

<ApiMember kind="method">

<ApiSignature>

```python
def permanently_delete_workspace(
    self,
    workspace_id: str,
    *,
    workspace_name: str | None = None,
    safe_mode: bool = True,
) -> None
```

</ApiSignature>

Permanently delete an Airbyte workspace if it has no connections.

When `safe_mode` is enabled, the workspace name must contain `delete-me`
or `deleteme`. This also checks for existing connections before deleting
and raises `AirbyteWorkspaceNotEmptyError` if the workspace is not empty.

</ApiMember>

#### `rename_workspace` {#airbyte.cloud.CloudClient.rename_workspace}

<ApiMember kind="method">

<ApiSignature>

```python
def rename_workspace(
    self,
    workspace_id: str,
    *,
    name: str,
) -> airbyte.cloud.models.CloudWorkspaceInfo
```

</ApiSignature>

Rename an Airbyte workspace.

</ApiMember>

</ApiMember>

### `CloudClientConfig` {#airbyte.cloud.CloudClientConfig}

<ApiMember kind="class">

<ApiSignature>

```python
class CloudClientConfig(
    client_id: SecretString | None = None,
    client_secret: SecretString | None = None,
    bearer_token: SecretString | None = None,
    api_root: str = 'https://api.airbyte.com/v1',
    config_api_root: str | None = None,
)
```

</ApiSignature>

Client configuration for Airbyte Cloud API.

This class encapsulates the authentication and API configuration needed to connect
to Airbyte Cloud, OSS, or Enterprise instances. It supports two mutually
exclusive authentication methods:

1. OAuth2 client credentials flow (client_id + client_secret)
2. Bearer token authentication

Exactly one authentication method must be provided. Providing both or neither
will raise a validation error.

**Attributes:**

- **`client_id`**: OAuth2 client ID for client credentials flow.
- **`client_secret`**: OAuth2 client secret for client credentials flow.
- **`bearer_token`**: Pre-generated bearer token for direct authentication.
- **`api_root`**: The API root URL. Defaults to Airbyte Cloud API.
- **`config_api_root`**: The Config API root URL.

#### Attributes {#airbyte.cloud.CloudClientConfig--attributes}

- **`api_root`**&nbsp;(`str`) — The API root URL. Defaults to Airbyte Cloud API.

- **`bearer_token`**&nbsp;(`airbyte.secrets.base.SecretString | None`) — Bearer token for direct authentication (alternative to client credentials).

- **`client_id`**&nbsp;(`airbyte.secrets.base.SecretString | None`) — OAuth2 client ID for client credentials authentication.

- **`client_secret`**&nbsp;(`airbyte.secrets.base.SecretString | None`) — OAuth2 client secret for client credentials authentication.

- **`config_api_root`**&nbsp;(`str | None`) — The Config API root URL.

- **`uses_bearer_token`**&nbsp;(`bool`) — Return True if using bearer token authentication.

- **`uses_client_credentials`**&nbsp;(`bool`) — Return True if using client credentials authentication.

#### `from_env` {#airbyte.cloud.CloudClientConfig.from_env}

<ApiMember kind="method">

<ApiSignature>

```python
def from_env(
    *,
    api_root: str | None = None,
    config_api_root: str | None = None,
) -> airbyte.cloud.client_config.CloudClientConfig
```

</ApiSignature>

Create CloudClientConfig from environment variables.

This factory method resolves credentials from environment variables,
providing a convenient way to create credentials without explicitly
passing secrets.

Environment variables used:
    - `AIRBYTE_CLOUD_CLIENT_ID`: OAuth client ID (for client credentials flow).
    - `AIRBYTE_CLOUD_CLIENT_SECRET`: OAuth client secret (for client credentials flow).
    - `AIRBYTE_CLOUD_BEARER_TOKEN`: Bearer token (alternative to client credentials).
    - `AIRBYTE_CLOUD_API_URL`: Optional. The API root URL (defaults to Airbyte Cloud).
    - `AIRBYTE_CLOUD_CONFIG_API_URL`: Optional. The Config API root URL.

The method will first check for a bearer token. If not found, it will
attempt to use client credentials.

**Args:**

- **`api_root`**: The API root URL. If not provided, will be resolved from the `AIRBYTE_CLOUD_API_URL` environment variable, or default to the Airbyte Cloud API.
- **`config_api_root`**: The Config API root URL. If not provided, will be resolved from the `AIRBYTE_CLOUD_CONFIG_API_URL` environment variable.

**Returns:**

A CloudClientConfig instance configured with credentials from the environment.

**Raises:**

- **`PyAirbyteSecretNotFoundError`**: If required credentials are not found in the environment.

</ApiMember>

</ApiMember>

### `CloudConnection` {#airbyte.cloud.CloudConnection}

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

#### Attributes {#airbyte.cloud.CloudConnection--attributes}

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

#### `cancel_sync` {#airbyte.cloud.CloudConnection.cancel_sync}

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

#### `check_is_valid` {#airbyte.cloud.CloudConnection.check_is_valid}

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

#### `dump_raw_catalog` {#airbyte.cloud.CloudConnection.dump_raw_catalog}

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

#### `dump_raw_state` {#airbyte.cloud.CloudConnection.dump_raw_state}

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

#### `get_catalog_artifact` {#airbyte.cloud.CloudConnection.get_catalog_artifact}

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

#### `get_previous_sync_logs` {#airbyte.cloud.CloudConnection.get_previous_sync_logs}

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

#### `get_state_artifacts` {#airbyte.cloud.CloudConnection.get_state_artifacts}

<ApiMember kind="method">

<ApiSignature>

```python
def get_state_artifacts(self) -> list[dict[str, typing.Any]] | None
```

</ApiSignature>

Deprecated. Use `dump_raw_state()` instead.

</ApiMember>

#### `get_stream_state` {#airbyte.cloud.CloudConnection.get_stream_state}

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

#### `get_sync_result` {#airbyte.cloud.CloudConnection.get_sync_result}

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

#### `import_raw_catalog` {#airbyte.cloud.CloudConnection.import_raw_catalog}

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

#### `import_raw_state` {#airbyte.cloud.CloudConnection.import_raw_state}

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

#### `permanently_delete` {#airbyte.cloud.CloudConnection.permanently_delete}

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

#### `rename` {#airbyte.cloud.CloudConnection.rename}

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

#### `run_sync` {#airbyte.cloud.CloudConnection.run_sync}

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

#### `set_enabled` {#airbyte.cloud.CloudConnection.set_enabled}

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

#### `set_manual_schedule` {#airbyte.cloud.CloudConnection.set_manual_schedule}

<ApiMember kind="method">

<ApiSignature>

```python
def set_manual_schedule(self) -> None
```

</ApiSignature>

Set the connection to manual scheduling.

Disables automatic syncs. Syncs will only run when manually triggered.

</ApiMember>

#### `set_schedule` {#airbyte.cloud.CloudConnection.set_schedule}

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

#### `set_selected_streams` {#airbyte.cloud.CloudConnection.set_selected_streams}

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

#### `set_stream_state` {#airbyte.cloud.CloudConnection.set_stream_state}

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

#### `set_table_prefix` {#airbyte.cloud.CloudConnection.set_table_prefix}

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

### `CloudOrganization` {#airbyte.cloud.CloudOrganization}

<ApiMember kind="class">

<ApiSignature>

```python
class CloudOrganization(
    organization_id: str,
    organization_name: str | None = None,
    email: str | None = None,
    *,
    client_id: str | SecretString | None = None,
    client_secret: str | SecretString | None = None,
    bearer_token: str | SecretString | None = None,
    public_api_root: str | None = None,
    config_api_root: str | None = None,
)
```

</ApiSignature>

Information about an organization in Airbyte Cloud.

This class provides lazy loading of organization attributes including billing status.
It is typically created via `CloudWorkspace.get_organization()`.

Initialize a `CloudOrganization`.

#### Attributes {#airbyte.cloud.CloudOrganization--attributes}

- **`email`**&nbsp;(`str | None`) — Email associated with the organization.

- **`is_account_locked`**&nbsp;(`bool`) — Whether the account is locked due to billing issues.

- **`organization_id`** — The organization ID.

- **`organization_name`**&nbsp;(`str | None`) — Display name of the organization.

- **`payment_status`**&nbsp;(`str | None`) — Payment status of the organization.

- **`subscription_status`**&nbsp;(`str | None`) — Subscription status of the organization.

</ApiMember>

### `CloudWorkspace` {#airbyte.cloud.CloudWorkspace}

<ApiMember kind="class">

<ApiSignature>

```python
class CloudWorkspace(
    *,
    workspace_id: str | None = None,
    client_id: str | SecretString | None = None,
    client_secret: str | SecretString | None = None,
    api_root: str | None = None,
    config_api_root: str | None = None,
    bearer_token: str | SecretString | None = None,
)
```

</ApiSignature>

A remote workspace on the Airbyte Cloud.

By overriding `api_root`, you can use this class to interact with self-managed Airbyte
instances, both OSS and Enterprise.

Two authentication methods are supported (mutually exclusive):
1. OAuth2 client credentials (client_id + client_secret)
2. Bearer token authentication

Example with client credentials:
    ```python
    workspace = CloudWorkspace(
        workspace_id="...",
        client_id="...",
        client_secret="...",
    )
    ```

Example with bearer token:
    ```python
    workspace = CloudWorkspace(
        workspace_id="...",
        bearer_token="...",
    )
    ```

Validate and initialize credentials.

#### Attributes {#airbyte.cloud.CloudWorkspace--attributes}

- **`api_root`**&nbsp;(`str`)

- **`bearer_token`**&nbsp;(`SecretString | None`)

- **`client_id`**&nbsp;(`SecretString | None`)

- **`client_secret`**&nbsp;(`SecretString | None`)

- **`config_api_root`**&nbsp;(`str | None`) — The Config API root URL.

- **`workspace_id`**&nbsp;(`str`)

- **`workspace_url`**&nbsp;(`str | None`) — The web URL of the workspace.

#### `from_env` {#airbyte.cloud.CloudWorkspace.from_env}

<ApiMember kind="method">

<ApiSignature>

```python
def from_env(
    workspace_id: str | None = None,
    *,
    api_root: str | None = None,
    config_api_root: str | None = None,
) -> airbyte.cloud.workspaces.CloudWorkspace
```

</ApiSignature>

Create a CloudWorkspace using credentials from environment variables.

This factory method resolves credentials from environment variables,
providing a convenient way to create a workspace without explicitly
passing credentials.

Two authentication methods are supported (mutually exclusive):
1. Bearer token (checked first)
2. OAuth2 client credentials (fallback)

Environment variables used:
    - `AIRBYTE_CLOUD_BEARER_TOKEN`: Bearer token (alternative to client credentials).
    - `AIRBYTE_CLOUD_CLIENT_ID`: OAuth client ID (for client credentials flow).
    - `AIRBYTE_CLOUD_CLIENT_SECRET`: OAuth client secret (for client credentials flow).
    - `AIRBYTE_CLOUD_WORKSPACE_ID`: The workspace ID (if not passed as argument).
    - `AIRBYTE_CLOUD_API_URL`: Optional. The API root URL (defaults to Airbyte Cloud).
    - `AIRBYTE_CLOUD_CONFIG_API_URL`: Optional. The Config API root URL.

**Args:**

- **`workspace_id`**: The workspace ID. If not provided, will be resolved from the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable.
- **`api_root`**: The API root URL. If not provided, will be resolved from the `AIRBYTE_CLOUD_API_URL` environment variable, or default to the Airbyte Cloud API.
- **`config_api_root`**: The Config API root URL. If not provided, will be resolved from the `AIRBYTE_CLOUD_CONFIG_API_URL` environment variable.

**Returns:**

A CloudWorkspace instance configured with credentials from the environment.

**Raises:**

- **`PyAirbyteInputError`**: If required credentials are not found in the environment or are incomplete.

**Example:**

```python
# With workspace_id from environment
workspace = CloudWorkspace.from_env()

# With explicit workspace_id
workspace = CloudWorkspace.from_env(workspace_id="your-workspace-id")
```

</ApiMember>

#### `connect` {#airbyte.cloud.CloudWorkspace.connect}

<ApiMember kind="method">

<ApiSignature>

```python
def connect(self) -> None
```

</ApiSignature>

Check that the workspace is reachable and raise an exception otherwise.

Note: It is not necessary to call this method before calling other operations. It
      serves primarily as a simple check to ensure that the workspace is reachable
      and credentials are correct.

</ApiMember>

#### `deploy_connection` {#airbyte.cloud.CloudWorkspace.deploy_connection}

<ApiMember kind="method">

<ApiSignature>

```python
def deploy_connection(
    self,
    connection_name: str,
    *,
    source: CloudSource | str,
    selected_streams: list[str],
    destination: CloudDestination | str,
    table_prefix: str | None = None,
) -> airbyte.cloud.connections.CloudConnection
```

</ApiSignature>

Create a new connection between an already deployed source and destination.

Returns the newly deployed connection object.

**Args:**

- **`connection_name`**: The name of the connection.
- **`source`**: The deployed source. You can pass a source ID or a CloudSource object.
- **`destination`**: The deployed destination. You can pass a destination ID or a CloudDestination object.
- **`table_prefix`**: Optional. The table prefix to use when syncing to the destination.
- **`selected_streams`**: The selected stream names to sync within the connection.

</ApiMember>

#### `deploy_destination` {#airbyte.cloud.CloudWorkspace.deploy_destination}

<ApiMember kind="method">

<ApiSignature>

```python
def deploy_destination(
    self,
    name: str,
    destination: Destination | dict[str, Any],
    *,
    unique: bool = True,
    random_name_suffix: bool = False,
) -> airbyte.cloud.connectors.CloudDestination
```

</ApiSignature>

Deploy a destination to the workspace.

Returns the newly deployed destination ID.

**Args:**

- **`name`**: The name to use when deploying.
- **`destination`**: The destination to deploy. Can be a local Airbyte `Destination` object or a dictionary of configuration values.
- **`unique`**: Whether to require a unique name. If `True`, duplicate names are not allowed. Defaults to `True`.
- **`random_name_suffix`**: Whether to append a random suffix to the name.

</ApiMember>

#### `deploy_source` {#airbyte.cloud.CloudWorkspace.deploy_source}

<ApiMember kind="method">

<ApiSignature>

```python
def deploy_source(
    self,
    name: str,
    source: Source,
    *,
    unique: bool = True,
    random_name_suffix: bool = False,
) -> CloudSource
```

</ApiSignature>

Deploy a source to the workspace.

Returns the newly deployed source.

**Args:**

- **`name`**: The name to use when deploying.
- **`source`**: The source object to deploy.
- **`unique`**: Whether to require a unique name. If `True`, duplicate names are not allowed. Defaults to `True`.
- **`random_name_suffix`**: Whether to append a random suffix to the name.

</ApiMember>

#### `get_connection` {#airbyte.cloud.CloudWorkspace.get_connection}

<ApiMember kind="method">

<ApiSignature>

```python
def get_connection(
    self,
    connection_id: str,
) -> airbyte.cloud.connections.CloudConnection
```

</ApiSignature>

Get a connection by ID.

This method does not fetch data from the API. It returns a `CloudConnection` object,
which will be loaded lazily as needed.

</ApiMember>

#### `get_custom_source_definition` {#airbyte.cloud.CloudWorkspace.get_custom_source_definition}

<ApiMember kind="method">

<ApiSignature>

```python
def get_custom_source_definition(
    self,
    definition_id: str,
    *,
    definition_type: "Literal['yaml', 'docker']",
) -> airbyte.cloud.connectors.CustomCloudSourceDefinition
```

</ApiSignature>

Get a specific custom source definition by ID.

**Args:**

- **`definition_id`**: The definition ID
- **`definition_type`**: Connector type ("yaml" or "docker"). Required.

**Returns:**

CustomCloudSourceDefinition object

</ApiMember>

#### `get_destination` {#airbyte.cloud.CloudWorkspace.get_destination}

<ApiMember kind="method">

<ApiSignature>

```python
def get_destination(
    self,
    destination_id: str,
) -> airbyte.cloud.connectors.CloudDestination
```

</ApiSignature>

Get a destination by ID.

This method does not fetch data from the API. It returns a `CloudDestination` object,
which will be loaded lazily as needed.

</ApiMember>

#### `get_organization` {#airbyte.cloud.CloudWorkspace.get_organization}

<ApiMember kind="method">

<ApiSignature>

```python
def get_organization(
    self,
    *,
    raise_on_error: bool = True,
) -> airbyte.cloud.organizations.CloudOrganization | None
```

</ApiSignature>

Get the organization this workspace belongs to.

Fetching organization info requires ORGANIZATION_READER permissions on the organization,
which may not be available with workspace-scoped credentials.

**Args:**

- **`raise_on_error`**: If True (default), raises AirbyteError on permission or API errors. If False, returns None instead of raising.

**Returns:**

CloudOrganization object with organization_id and organization_name,
or None if raise_on_error=False and an error occurred.

**Raises:**

- **`AirbyteError`**: If raise_on_error=True and the organization info cannot be fetched (e.g., due to insufficient permissions or missing data).

</ApiMember>

#### `get_source` {#airbyte.cloud.CloudWorkspace.get_source}

<ApiMember kind="method">

<ApiSignature>

```python
def get_source(self, source_id: str) -> airbyte.cloud.connectors.CloudSource
```

</ApiSignature>

Get a source by ID.

This method does not fetch data from the API. It returns a `CloudSource` object,
which will be loaded lazily as needed.

</ApiMember>

#### `list_connections` {#airbyte.cloud.CloudWorkspace.list_connections}

<ApiMember kind="method">

<ApiSignature>

```python
def list_connections(
    self,
    name: str | None = None,
    *,
    name_filter: Callable | None = None,
    limit: int | None = None,
) -> list[CloudConnection]
```

</ApiSignature>

List connections by name in the workspace, with an optional limit.

</ApiMember>

#### `list_custom_source_definitions` {#airbyte.cloud.CloudWorkspace.list_custom_source_definitions}

<ApiMember kind="method">

<ApiSignature>

```python
def list_custom_source_definitions(
    self,
    *,
    definition_type: "Literal['yaml', 'docker']",
) -> list[airbyte.cloud.connectors.CustomCloudSourceDefinition]
```

</ApiSignature>

List custom source connector definitions.

**Args:**

- **`definition_type`**: Connector type to list ("yaml" or "docker"). Required.

**Returns:**

List of CustomCloudSourceDefinition objects matching the specified type

</ApiMember>

#### `list_destinations` {#airbyte.cloud.CloudWorkspace.list_destinations}

<ApiMember kind="method">

<ApiSignature>

```python
def list_destinations(
    self,
    name: str | None = None,
    *,
    name_filter: Callable | None = None,
    limit: int | None = None,
) -> list[CloudDestination]
```

</ApiSignature>

List all destinations in the workspace, with an optional limit.

</ApiMember>

#### `list_sources` {#airbyte.cloud.CloudWorkspace.list_sources}

<ApiMember kind="method">

<ApiSignature>

```python
def list_sources(
    self,
    name: str | None = None,
    *,
    name_filter: Callable | None = None,
    limit: int | None = None,
) -> list[CloudSource]
```

</ApiSignature>

List all sources in the workspace, with an optional limit.

</ApiMember>

#### `list_workspaces` {#airbyte.cloud.CloudWorkspace.list_workspaces}

<ApiMember kind="method">

<ApiSignature>

```python
def list_workspaces(
    self,
    name: str | None = None,
    *,
    name_filter: Callable | None = None,
    limit: int | None = None,
) -> list[CloudWorkspaceInfo]
```

</ApiSignature>

List workspaces available to the current credentials, with an optional limit.

</ApiMember>

#### `permanently_delete` {#airbyte.cloud.CloudWorkspace.permanently_delete}

<ApiMember kind="method">

<ApiSignature>

```python
def permanently_delete(
    self,
    *,
    workspace_name: str | None = None,
    safe_mode: bool = True,
) -> None
```

</ApiSignature>

Permanently delete this workspace if it has no connections.

When `safe_mode` is enabled, the workspace name must contain `delete-me`
or `deleteme`. This also checks for existing connections before deleting
and raises `AirbyteWorkspaceNotEmptyError` if the workspace is not empty.

</ApiMember>

#### `permanently_delete_connection` {#airbyte.cloud.CloudWorkspace.permanently_delete_connection}

<ApiMember kind="method">

<ApiSignature>

```python
def permanently_delete_connection(
    self,
    connection: str | CloudConnection,
    *,
    cascade_delete_source: bool = False,
    cascade_delete_destination: bool = False,
    safe_mode: bool = True,
) -> None
```

</ApiSignature>

Delete a deployed connection from the workspace.

**Args:**

- **`connection`**: The connection ID or CloudConnection object to delete
- **`cascade_delete_source`**: If True, also delete the source after deleting the connection
- **`cascade_delete_destination`**: If True, also delete the destination after deleting the connection
- **`safe_mode`**: If True, requires the connection name to contain "delete-me" or "deleteme" (case insensitive) to prevent accidental deletion. Defaults to True. Also applies to cascade deletes.

</ApiMember>

#### `permanently_delete_destination` {#airbyte.cloud.CloudWorkspace.permanently_delete_destination}

<ApiMember kind="method">

<ApiSignature>

```python
def permanently_delete_destination(
    self,
    destination: str | CloudDestination,
    *,
    safe_mode: bool = True,
) -> None
```

</ApiSignature>

Delete a deployed destination from the workspace.

You can pass either the `Cache` class or the deployed destination ID as a `str`.

**Args:**

- **`destination`**: The destination ID or CloudDestination object to delete
- **`safe_mode`**: If True, requires the destination name to contain "delete-me" or "deleteme" (case insensitive) to prevent accidental deletion. Defaults to True.

</ApiMember>

#### `permanently_delete_source` {#airbyte.cloud.CloudWorkspace.permanently_delete_source}

<ApiMember kind="method">

<ApiSignature>

```python
def permanently_delete_source(
    self,
    source: str | CloudSource,
    *,
    safe_mode: bool = True,
) -> None
```

</ApiSignature>

Delete a source from the workspace.

You can pass either the source ID `str` or a deployed `Source` object.

**Args:**

- **`source`**: The source ID or CloudSource object to delete
- **`safe_mode`**: If True, requires the source name to contain "delete-me" or "deleteme" (case insensitive) to prevent accidental deletion. Defaults to True.

</ApiMember>

#### `publish_custom_source_definition` {#airbyte.cloud.CloudWorkspace.publish_custom_source_definition}

<ApiMember kind="method">

<ApiSignature>

```python
def publish_custom_source_definition(
    self,
    name: str,
    *,
    manifest_yaml: dict[str, Any] | Path | str | None = None,
    docker_image: str | None = None,
    docker_tag: str | None = None,
    unique: bool = True,
    pre_validate: bool = True,
    testing_values: dict[str, Any] | None = None,
) -> airbyte.cloud.connectors.CustomCloudSourceDefinition
```

</ApiSignature>

Publish a custom source connector definition.

You must specify EITHER manifest_yaml (for YAML connectors) OR both docker_image
and docker_tag (for Docker connectors), but not both.

**Args:**

- **`name`**: Display name for the connector definition
- **`manifest_yaml`**: Low-code CDK manifest (dict, Path to YAML file, or YAML string)
- **`docker_image`**: Docker repository (e.g., 'airbyte/source-custom')
- **`docker_tag`**: Docker image tag (e.g., '1.0.0')
- **`unique`**: Whether to enforce name uniqueness
- **`pre_validate`**: Whether to validate manifest client-side (YAML only)
- **`testing_values`**: Optional configuration values to use for testing in the Connector Builder UI. If provided, these values are stored as the complete testing values object for the connector builder project (replaces any existing values), allowing immediate test read operations.

**Returns:**

CustomCloudSourceDefinition object representing the created definition

**Raises:**

- **`PyAirbyteInputError`**: If both or neither of manifest_yaml and docker_image provided
- **`AirbyteDuplicateResourcesError`**: If unique=True and name already exists

</ApiMember>

#### `rename` {#airbyte.cloud.CloudWorkspace.rename}

<ApiMember kind="method">

<ApiSignature>

```python
def rename(self, name: str) -> airbyte.cloud.workspaces.CloudWorkspace
```

</ApiSignature>

Rename this workspace.

</ApiMember>

</ApiMember>

### `CloudWorkspaceInfo` {#airbyte.cloud.CloudWorkspaceInfo}

<ApiMember kind="class">

<ApiSignature>

```python
class CloudWorkspaceInfo(**data: Any)
```

</ApiSignature>

Information about an Airbyte workspace.

Raises ``ValidationError`` if the input data cannot be
validated to form a valid model.

`self` is explicitly positional-only to allow `self` as a field name.

#### Attributes {#airbyte.cloud.CloudWorkspaceInfo--attributes}

- **`data_residency`**&nbsp;(`str | None`) — The data residency setting for the workspace, if available.

- **`name`**&nbsp;(`str`) — The workspace name.

- **`notifications`**&nbsp;(`dict[str, object | None] | list[dict[str, object | None]]`) — Workspace notification settings.

- **`organization_id`**&nbsp;(`str | None`) — The organization ID for the workspace, if available.

- **`workspace_id`**&nbsp;(`str`) — The workspace ID.

#### `from_api_response` {#airbyte.cloud.CloudWorkspaceInfo.from_api_response}

<ApiMember kind="method">

<ApiSignature>

```python
def from_api_response(
    workspace: _WorkspaceResponseLike,
) -> airbyte.cloud.models.CloudWorkspaceInfo
```

</ApiSignature>

Create a public model from an internal API workspace response.

</ApiMember>

#### `from_mapping` {#airbyte.cloud.CloudWorkspaceInfo.from_mapping}

<ApiMember kind="method">

<ApiSignature>

```python
def from_mapping(
    workspace: Mapping[str, object],
) -> airbyte.cloud.models.CloudWorkspaceInfo
```

</ApiSignature>

Create a public model from a workspace mapping.

</ApiMember>

#### `to_dict` {#airbyte.cloud.CloudWorkspaceInfo.to_dict}

<ApiMember kind="method">

<ApiSignature>

```python
def to_dict(self) -> dict[str, object]
```

</ApiSignature>

Return a JSON-serializable dictionary.

</ApiMember>

</ApiMember>

### `JobStatusEnum` {#airbyte.cloud.JobStatusEnum}

<ApiMember kind="class">

<ApiSignature>

```python
class JobStatusEnum(
    value,
    names=None,
    *,
    module=None,
    qualname=None,
    type=None,
    start=1,
)
```

</ApiSignature>

Status values for an Airbyte Cloud job.

**Bases:** `builtins.str`, `enum.Enum`

#### Attributes {#airbyte.cloud.JobStatusEnum--attributes}

- **`CANCELLED`**

- **`FAILED`**

- **`INCOMPLETE`**

- **`PENDING`**

- **`RUNNING`**

- **`SUCCEEDED`**

</ApiMember>

### `JobTypeEnum` {#airbyte.cloud.JobTypeEnum}

<ApiMember kind="class">

<ApiSignature>

```python
class JobTypeEnum(
    value,
    names=None,
    *,
    module=None,
    qualname=None,
    type=None,
    start=1,
)
```

</ApiSignature>

Job type values for Airbyte Cloud jobs.

**Bases:** `builtins.str`, `enum.Enum`

#### Attributes {#airbyte.cloud.JobTypeEnum--attributes}

- **`CLEAR`**

- **`REFRESH`**

- **`RESET`**

- **`SYNC`**

</ApiMember>

### `SyncResult` {#airbyte.cloud.SyncResult}

<ApiMember kind="class">

<ApiSignature>

```python
class SyncResult(
    workspace: CloudWorkspace,
    connection: CloudConnection,
    job_id: int,
    table_name_prefix: str = '',
    table_name_suffix: str = '',
)
```

</ApiSignature>

The result of a sync operation.

**This class is not meant to be instantiated directly.** Instead, obtain a `SyncResult` by
interacting with the `.CloudWorkspace` and `.CloudConnection` objects.

#### Attributes {#airbyte.cloud.SyncResult--attributes}

- **`bytes_synced`**&nbsp;(`int`) — Return the number of records processed.

- **`connection`**&nbsp;(`CloudConnection`)

- **`job_id`**&nbsp;(`int`)

- **`job_url`**&nbsp;(`str`) — Return the URL of the sync job.  Note: This currently returns the connection's job history URL, as there is no direct URL to a specific job in the Airbyte Cloud web app.  TODO: Implement a direct job logs URL on top of the event-id of the specific attempt number.       E.g. \{self.connection.job_history_url\}?eventId=\{event-guid\}&openLogs=true

- **`records_synced`**&nbsp;(`int`) — Return the number of records processed.

- **`start_time`**&nbsp;(`datetime`) — Return the start time of the sync job in UTC.

- **`stream_names`**&nbsp;(`list[str]`) — Return the set of stream names.

- **`streams`**&nbsp;(`_SyncResultStreams`) — Return a mapping of stream names to `airbyte.CachedDataset` objects.  This is a convenience wrapper around the `stream_names` property and `get_dataset()` method.

- **`table_name_prefix`**&nbsp;(`str`)

- **`table_name_suffix`**&nbsp;(`str`)

- **`workspace`**&nbsp;(`CloudWorkspace`)

#### `get_attempts` {#airbyte.cloud.SyncResult.get_attempts}

<ApiMember kind="method">

<ApiSignature>

```python
def get_attempts(self) -> list[airbyte.cloud.sync_results.SyncAttempt]
```

</ApiSignature>

Return a list of attempts for this sync job.

</ApiMember>

#### `get_dataset` {#airbyte.cloud.SyncResult.get_dataset}

<ApiMember kind="method">

<ApiSignature>

```python
def get_dataset(self, stream_name: str) -> airbyte.datasets._sql.CachedDataset
```

</ApiSignature>

Retrieve an `airbyte.datasets.CachedDataset` object for a given stream name.

This can be used to read and analyze the data in a SQL-based destination.

TODO: In a future iteration, we can consider providing stream configuration information
      (catalog information) to the `CachedDataset` object via the "Get stream properties"
      API: https://reference.airbyte.com/reference/getstreamproperties

</ApiMember>

#### `get_job_status` {#airbyte.cloud.SyncResult.get_job_status}

<ApiMember kind="method">

<ApiSignature>

```python
def get_job_status(self) -> airbyte.cloud.models.JobStatusEnum
```

</ApiSignature>

Check if the sync job is still running.

</ApiMember>

#### `get_sql_cache` {#airbyte.cloud.SyncResult.get_sql_cache}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_cache(self) -> CacheBase
```

</ApiSignature>

Return a SQL Cache object for working with the data in a SQL-based destination's.

</ApiMember>

#### `get_sql_database_name` {#airbyte.cloud.SyncResult.get_sql_database_name}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_database_name(self) -> str
```

</ApiSignature>

Return the SQL database name.

</ApiMember>

#### `get_sql_engine` {#airbyte.cloud.SyncResult.get_sql_engine}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_engine(self) -> sqlalchemy.engine.Engine
```

</ApiSignature>

Return a SQL Engine for querying a SQL-based destination.

</ApiMember>

#### `get_sql_schema_name` {#airbyte.cloud.SyncResult.get_sql_schema_name}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_schema_name(self) -> str
```

</ApiSignature>

Return the SQL schema name.

</ApiMember>

#### `get_sql_table` {#airbyte.cloud.SyncResult.get_sql_table}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_table(self, stream_name: str) -> sqlalchemy.Table
```

</ApiSignature>

Return a SQLAlchemy table object for the named stream.

</ApiMember>

#### `get_sql_table_name` {#airbyte.cloud.SyncResult.get_sql_table_name}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_table_name(self, stream_name: str) -> str
```

</ApiSignature>

Return the SQL table name of the named stream.

</ApiMember>

#### `is_job_complete` {#airbyte.cloud.SyncResult.is_job_complete}

<ApiMember kind="method">

<ApiSignature>

```python
def is_job_complete(self) -> bool
```

</ApiSignature>

Check if the sync job is complete.

</ApiMember>

#### `raise_failure_status` {#airbyte.cloud.SyncResult.raise_failure_status}

<ApiMember kind="method">

<ApiSignature>

```python
def raise_failure_status(self, *, refresh_status: bool = False) -> None
```

</ApiSignature>

Raise an exception if the sync job failed.

By default, this method will use the latest status available. If you want to refresh the
status before checking for failure, set `refresh_status=True`. If the job has failed, this
method will raise a `AirbyteConnectionSyncError`.

Otherwise, do nothing.

</ApiMember>

#### `wait_for_completion` {#airbyte.cloud.SyncResult.wait_for_completion}

<ApiMember kind="method">

<ApiSignature>

```python
def wait_for_completion(
    self,
    *,
    wait_timeout: int = 1800,
    raise_timeout: bool = True,
    raise_failure: bool = False,
) -> airbyte.cloud.models.JobStatusEnum
```

</ApiSignature>

Wait for a job to finish running.

</ApiMember>

</ApiMember>