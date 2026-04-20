---
id: airbyte-cloud-index
title: airbyte.cloud.index
---

Module airbyte.cloud
====================
PyAirbyte classes and methods for interacting with the Airbyte Cloud API.

You can use this module to interact with Airbyte Cloud, OSS, and Enterprise.

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

Sub-modules
-----------
* airbyte.cloud.auth
* airbyte.cloud.client_config
* airbyte.cloud.connections
* airbyte.cloud.connectors
* airbyte.cloud.constants
* airbyte.cloud.sync_results
* airbyte.cloud.workspaces

Classes
-------

`CloudClientConfig(client_id: SecretString | None = None, client_secret: SecretString | None = None, bearer_token: SecretString | None = None, api_root: str = 'https://api.airbyte.com/v1')`
:   Client configuration for Airbyte Cloud API.
    
    This class encapsulates the authentication and API configuration needed to connect
    to Airbyte Cloud, OSS, or Enterprise instances. It supports two mutually
    exclusive authentication methods:
    
    1. OAuth2 client credentials flow (client_id + client_secret)
    2. Bearer token authentication
    
    Exactly one authentication method must be provided. Providing both or neither
    will raise a validation error.
    
    Attributes:
        client_id: OAuth2 client ID for client credentials flow.
        client_secret: OAuth2 client secret for client credentials flow.
        bearer_token: Pre-generated bearer token for direct authentication.
        api_root: The API root URL. Defaults to Airbyte Cloud API.

    ### Static methods

    `from_env(*, api_root: str | None = None) ‑> airbyte.cloud.client_config.CloudClientConfig`
    :   Create CloudClientConfig from environment variables.
        
        This factory method resolves credentials from environment variables,
        providing a convenient way to create credentials without explicitly
        passing secrets.
        
        Environment variables used:
            - `AIRBYTE_CLOUD_CLIENT_ID`: OAuth client ID (for client credentials flow).
            - `AIRBYTE_CLOUD_CLIENT_SECRET`: OAuth client secret (for client credentials flow).
            - `AIRBYTE_CLOUD_BEARER_TOKEN`: Bearer token (alternative to client credentials).
            - `AIRBYTE_CLOUD_API_URL`: Optional. The API root URL (defaults to Airbyte Cloud).
        
        The method will first check for a bearer token. If not found, it will
        attempt to use client credentials.
        
        Args:
            api_root: The API root URL. If not provided, will be resolved from
                the `AIRBYTE_CLOUD_API_URL` environment variable, or default to
                the Airbyte Cloud API.
        
        Returns:
            A CloudClientConfig instance configured with credentials from the environment.
        
        Raises:
            PyAirbyteSecretNotFoundError: If required credentials are not found in
                the environment.

    ### Instance variables

    `api_root: str`
    :   The API root URL. Defaults to Airbyte Cloud API.

    `bearer_token: airbyte.secrets.base.SecretString | None`
    :   Bearer token for direct authentication (alternative to client credentials).

    `client_id: airbyte.secrets.base.SecretString | None`
    :   OAuth2 client ID for client credentials authentication.

    `client_secret: airbyte.secrets.base.SecretString | None`
    :   OAuth2 client secret for client credentials authentication.

    `uses_bearer_token: bool`
    :   Return True if using bearer token authentication.

    `uses_client_credentials: bool`
    :   Return True if using client credentials authentication.

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

`CloudWorkspace(workspace_id: str, client_id: SecretString | None = None, client_secret: SecretString | None = None, api_root: str = 'https://api.airbyte.com/v1', bearer_token: SecretString | None = None)`
:   A remote workspace on the Airbyte Cloud.
    
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

    ### Static methods

    `from_env(workspace_id: str | None = None, *, api_root: str | None = None) ‑> airbyte.cloud.workspaces.CloudWorkspace`
    :   Create a CloudWorkspace using credentials from environment variables.
        
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
        
        Args:
            workspace_id: The workspace ID. If not provided, will be resolved from
                the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable.
            api_root: The API root URL. If not provided, will be resolved from
                the `AIRBYTE_CLOUD_API_URL` environment variable, or default to
                the Airbyte Cloud API.
        
        Returns:
            A CloudWorkspace instance configured with credentials from the environment.
        
        Raises:
            PyAirbyteSecretNotFoundError: If required credentials are not found in
                the environment.
        
        Example:
            ```python
            # With workspace_id from environment
            workspace = CloudWorkspace.from_env()
        
            # With explicit workspace_id
            workspace = CloudWorkspace.from_env(workspace_id="your-workspace-id")
            ```

    ### Instance variables

    `api_root: str`
    :

    `bearer_token: airbyte.secrets.base.SecretString | None`
    :

    `client_id: airbyte.secrets.base.SecretString | None`
    :

    `client_secret: airbyte.secrets.base.SecretString | None`
    :

    `workspace_id: str`
    :

    `workspace_url: str | None`
    :   The web URL of the workspace.

    ### Methods

    `connect(self) ‑> None`
    :   Check that the workspace is reachable and raise an exception otherwise.
        
        Note: It is not necessary to call this method before calling other operations. It
              serves primarily as a simple check to ensure that the workspace is reachable
              and credentials are correct.

    `deploy_connection(self, connection_name: str, *, source: CloudSource | str, selected_streams: list[str], destination: CloudDestination | str, table_prefix: str | None = None) ‑> airbyte.cloud.connections.CloudConnection`
    :   Create a new connection between an already deployed source and destination.
        
        Returns the newly deployed connection object.
        
        Args:
            connection_name: The name of the connection.
            source: The deployed source. You can pass a source ID or a CloudSource object.
            destination: The deployed destination. You can pass a destination ID or a
                CloudDestination object.
            table_prefix: Optional. The table prefix to use when syncing to the destination.
            selected_streams: The selected stream names to sync within the connection.

    `deploy_destination(self, name: str, destination: Destination | dict[str, Any], *, unique: bool = True, random_name_suffix: bool = False) ‑> airbyte.cloud.connectors.CloudDestination`
    :   Deploy a destination to the workspace.
        
        Returns the newly deployed destination ID.
        
        Args:
            name: The name to use when deploying.
            destination: The destination to deploy. Can be a local Airbyte `Destination` object or a
                dictionary of configuration values.
            unique: Whether to require a unique name. If `True`, duplicate names
                are not allowed. Defaults to `True`.
            random_name_suffix: Whether to append a random suffix to the name.

    `deploy_source(self, name: str, source: Source, *, unique: bool = True, random_name_suffix: bool = False) ‑> CloudSource`
    :   Deploy a source to the workspace.
        
        Returns the newly deployed source.
        
        Args:
            name: The name to use when deploying.
            source: The source object to deploy.
            unique: Whether to require a unique name. If `True`, duplicate names
                are not allowed. Defaults to `True`.
            random_name_suffix: Whether to append a random suffix to the name.

    `get_connection(self, connection_id: str) ‑> airbyte.cloud.connections.CloudConnection`
    :   Get a connection by ID.
        
        This method does not fetch data from the API. It returns a `CloudConnection` object,
        which will be loaded lazily as needed.

    `get_custom_source_definition(self, definition_id: str, *, definition_type: "Literal['yaml', 'docker']") ‑> airbyte.cloud.connectors.CustomCloudSourceDefinition`
    :   Get a specific custom source definition by ID.
        
        Args:
            definition_id: The definition ID
            definition_type: Connector type ("yaml" or "docker"). Required.
        
        Returns:
            CustomCloudSourceDefinition object

    `get_destination(self, destination_id: str) ‑> airbyte.cloud.connectors.CloudDestination`
    :   Get a destination by ID.
        
        This method does not fetch data from the API. It returns a `CloudDestination` object,
        which will be loaded lazily as needed.

    `get_organization(self, *, raise_on_error: bool = True) ‑> airbyte.cloud.workspaces.CloudOrganization | None`
    :   Get the organization this workspace belongs to.
        
        Fetching organization info requires ORGANIZATION_READER permissions on the organization,
        which may not be available with workspace-scoped credentials.
        
        Args:
            raise_on_error: If True (default), raises AirbyteError on permission or API errors.
                If False, returns None instead of raising.
        
        Returns:
            CloudOrganization object with organization_id and organization_name,
            or None if raise_on_error=False and an error occurred.
        
        Raises:
            AirbyteError: If raise_on_error=True and the organization info cannot be fetched
                (e.g., due to insufficient permissions or missing data).

    `get_source(self, source_id: str) ‑> airbyte.cloud.connectors.CloudSource`
    :   Get a source by ID.
        
        This method does not fetch data from the API. It returns a `CloudSource` object,
        which will be loaded lazily as needed.

    `list_connections(self, name: str | None = None, *, name_filter: Callable | None = None) ‑> list[CloudConnection]`
    :   List connections by name in the workspace.
        
        TODO: Add pagination support

    `list_custom_source_definitions(self, *, definition_type: "Literal['yaml', 'docker']") ‑> list[airbyte.cloud.connectors.CustomCloudSourceDefinition]`
    :   List custom source connector definitions.
        
        Args:
            definition_type: Connector type to list ("yaml" or "docker"). Required.
        
        Returns:
            List of CustomCloudSourceDefinition objects matching the specified type

    `list_destinations(self, name: str | None = None, *, name_filter: Callable | None = None) ‑> list[CloudDestination]`
    :   List all destinations in the workspace.
        
        TODO: Add pagination support

    `list_sources(self, name: str | None = None, *, name_filter: Callable | None = None) ‑> list[CloudSource]`
    :   List all sources in the workspace.
        
        TODO: Add pagination support

    `permanently_delete_connection(self, connection: str | CloudConnection, *, cascade_delete_source: bool = False, cascade_delete_destination: bool = False, safe_mode: bool = True) ‑> None`
    :   Delete a deployed connection from the workspace.
        
        Args:
            connection: The connection ID or CloudConnection object to delete
            cascade_delete_source: If True, also delete the source after deleting the connection
            cascade_delete_destination: If True, also delete the destination after deleting
                the connection
            safe_mode: If True, requires the connection name to contain "delete-me" or "deleteme"
                (case insensitive) to prevent accidental deletion. Defaults to True. Also applies
                to cascade deletes.

    `permanently_delete_destination(self, destination: str | CloudDestination, *, safe_mode: bool = True) ‑> None`
    :   Delete a deployed destination from the workspace.
        
        You can pass either the `Cache` class or the deployed destination ID as a `str`.
        
        Args:
            destination: The destination ID or CloudDestination object to delete
            safe_mode: If True, requires the destination name to contain "delete-me" or "deleteme"
                (case insensitive) to prevent accidental deletion. Defaults to True.

    `permanently_delete_source(self, source: str | CloudSource, *, safe_mode: bool = True) ‑> None`
    :   Delete a source from the workspace.
        
        You can pass either the source ID `str` or a deployed `Source` object.
        
        Args:
            source: The source ID or CloudSource object to delete
            safe_mode: If True, requires the source name to contain "delete-me" or "deleteme"
                (case insensitive) to prevent accidental deletion. Defaults to True.

    `publish_custom_source_definition(self, name: str, *, manifest_yaml: dict[str, Any] | Path | str | None = None, docker_image: str | None = None, docker_tag: str | None = None, unique: bool = True, pre_validate: bool = True, testing_values: dict[str, Any] | None = None) ‑> airbyte.cloud.connectors.CustomCloudSourceDefinition`
    :   Publish a custom source connector definition.
        
        You must specify EITHER manifest_yaml (for YAML connectors) OR both docker_image
        and docker_tag (for Docker connectors), but not both.
        
        Args:
            name: Display name for the connector definition
            manifest_yaml: Low-code CDK manifest (dict, Path to YAML file, or YAML string)
            docker_image: Docker repository (e.g., 'airbyte/source-custom')
            docker_tag: Docker image tag (e.g., '1.0.0')
            unique: Whether to enforce name uniqueness
            pre_validate: Whether to validate manifest client-side (YAML only)
            testing_values: Optional configuration values to use for testing in the
                Connector Builder UI. If provided, these values are stored as the complete
                testing values object for the connector builder project (replaces any existing
                values), allowing immediate test read operations.
        
        Returns:
            CustomCloudSourceDefinition object representing the created definition
        
        Raises:
            PyAirbyteInputError: If both or neither of manifest_yaml and docker_image provided
            AirbyteDuplicateResourcesError: If unique=True and name already exists

`JobStatusEnum(*args, **kwds)`
:   str(object='') -> str
    str(bytes_or_buffer[, encoding[, errors]]) -> str
    
    Create a new string object from the given object. If encoding or
    errors is specified, then the object must expose a data buffer
    that will be decoded using the given encoding and error handler.
    Otherwise, returns the result of object.__str__() (if defined)
    or repr(object).
    encoding defaults to sys.getdefaultencoding().
    errors defaults to 'strict'.

    ### Ancestors (in MRO)

    * builtins.str
    * enum.Enum

    ### Class variables

    `CANCELLED`
    :

    `FAILED`
    :

    `INCOMPLETE`
    :

    `PENDING`
    :

    `RUNNING`
    :

    `SUCCEEDED`
    :

`SyncResult(workspace: CloudWorkspace, connection: CloudConnection, job_id: int, table_name_prefix: str = '', table_name_suffix: str = '')`
:   The result of a sync operation.
    
    **This class is not meant to be instantiated directly.** Instead, obtain a `SyncResult` by
    interacting with the `.CloudWorkspace` and `.CloudConnection` objects.

    ### Instance variables

    `bytes_synced: int`
    :   Return the number of records processed.

    `connection: CloudConnection`
    :

    `job_id: int`
    :

    `job_url: str`
    :   Return the URL of the sync job.
        
        Note: This currently returns the connection's job history URL, as there is no direct URL
        to a specific job in the Airbyte Cloud web app.
        
        TODO: Implement a direct job logs URL on top of the event-id of the specific attempt number.
              E.g. \{self.connection.job_history_url\}?eventId=\{event-guid\}&openLogs=true

    `records_synced: int`
    :   Return the number of records processed.

    `start_time: datetime`
    :   Return the start time of the sync job in UTC.

    `stream_names: list[str]`
    :   Return the set of stream names.

    `streams: _SyncResultStreams`
    :   Return a mapping of stream names to `airbyte.CachedDataset` objects.
        
        This is a convenience wrapper around the `stream_names`
        property and `get_dataset()` method.

    `table_name_prefix: str`
    :

    `table_name_suffix: str`
    :

    `workspace: CloudWorkspace`
    :

    ### Methods

    `get_attempts(self) ‑> list[airbyte.cloud.sync_results.SyncAttempt]`
    :   Return a list of attempts for this sync job.

    `get_dataset(self, stream_name: str) ‑> airbyte.datasets._sql.CachedDataset`
    :   Retrieve an `airbyte.datasets.CachedDataset` object for a given stream name.
        
        This can be used to read and analyze the data in a SQL-based destination.
        
        TODO: In a future iteration, we can consider providing stream configuration information
              (catalog information) to the `CachedDataset` object via the "Get stream properties"
              API: https://reference.airbyte.com/reference/getstreamproperties

    `get_job_status(self) ‑> JobStatusEnum`
    :   Check if the sync job is still running.

    `get_sql_cache(self) ‑> CacheBase`
    :   Return a SQL Cache object for working with the data in a SQL-based destination's.

    `get_sql_database_name(self) ‑> str`
    :   Return the SQL database name.

    `get_sql_engine(self) ‑> sqlalchemy.engine.Engine`
    :   Return a SQL Engine for querying a SQL-based destination.

    `get_sql_schema_name(self) ‑> str`
    :   Return the SQL schema name.

    `get_sql_table(self, stream_name: str) ‑> sqlalchemy.Table`
    :   Return a SQLAlchemy table object for the named stream.

    `get_sql_table_name(self, stream_name: str) ‑> str`
    :   Return the SQL table name of the named stream.

    `is_job_complete(self) ‑> bool`
    :   Check if the sync job is complete.

    `raise_failure_status(self, *, refresh_status: bool = False) ‑> None`
    :   Raise an exception if the sync job failed.
        
        By default, this method will use the latest status available. If you want to refresh the
        status before checking for failure, set `refresh_status=True`. If the job has failed, this
        method will raise a `AirbyteConnectionSyncError`.
        
        Otherwise, do nothing.

    `wait_for_completion(self, *, wait_timeout: int = 1800, raise_timeout: bool = True, raise_failure: bool = False) ‑> JobStatusEnum`
    :   Wait for a job to finish running.