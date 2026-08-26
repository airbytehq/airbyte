---
id: airbyte-cloud-workspaces
title: airbyte.cloud.workspaces
---

PyAirbyte classes and methods for interacting with the Airbyte Cloud API.

By overriding `api_root`, you can use this module to interact with self-managed Airbyte instances,
both OSS and Enterprise.

## Usage Examples

Get a new workspace object and deploy a source to it:

```python
import airbyte as ab
from airbyte import cloud

workspace = cloud.CloudWorkspace(
    workspace_id="...",
    client_id="...",
    client_secret="...",
)

# Deploy a source to the workspace
source = ab.get_source("source-faker", config={"count": 100})
deployed_source = workspace.deploy_source(
    name="test-source",
    source=source,
)

# Run a check on the deployed source and raise an exception if the check fails
check_result = deployed_source.check(raise_on_error=True)

# Permanently delete the newly-created source
workspace.permanently_delete_source(deployed_source)
```

### `CloudWorkspace` {#airbyte.cloud.workspaces.CloudWorkspace}

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

#### Attributes {#airbyte.cloud.workspaces.CloudWorkspace--attributes}

- **`api_root`**&nbsp;(`str`)

- **`bearer_token`**&nbsp;(`SecretString | None`)

- **`client_id`**&nbsp;(`SecretString | None`)

- **`client_secret`**&nbsp;(`SecretString | None`)

- **`config_api_root`**&nbsp;(`str | None`)

  The Config API root URL.

- **`workspace_id`**&nbsp;(`str`)

- **`workspace_url`**&nbsp;(`str | None`)

  The web URL of the workspace.

#### `from_env` {#airbyte.cloud.workspaces.CloudWorkspace.from_env}

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

#### `connect` {#airbyte.cloud.workspaces.CloudWorkspace.connect}

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

#### `deploy_connection` {#airbyte.cloud.workspaces.CloudWorkspace.deploy_connection}

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

#### `deploy_destination` {#airbyte.cloud.workspaces.CloudWorkspace.deploy_destination}

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

#### `deploy_source` {#airbyte.cloud.workspaces.CloudWorkspace.deploy_source}

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

#### `get_connection` {#airbyte.cloud.workspaces.CloudWorkspace.get_connection}

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

#### `get_custom_source_definition` {#airbyte.cloud.workspaces.CloudWorkspace.get_custom_source_definition}

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

#### `get_destination` {#airbyte.cloud.workspaces.CloudWorkspace.get_destination}

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

#### `get_organization` {#airbyte.cloud.workspaces.CloudWorkspace.get_organization}

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

#### `get_source` {#airbyte.cloud.workspaces.CloudWorkspace.get_source}

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

#### `list_connections` {#airbyte.cloud.workspaces.CloudWorkspace.list_connections}

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

#### `list_custom_source_definitions` {#airbyte.cloud.workspaces.CloudWorkspace.list_custom_source_definitions}

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

#### `list_destinations` {#airbyte.cloud.workspaces.CloudWorkspace.list_destinations}

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

#### `list_sources` {#airbyte.cloud.workspaces.CloudWorkspace.list_sources}

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

#### `list_workspaces` {#airbyte.cloud.workspaces.CloudWorkspace.list_workspaces}

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

#### `permanently_delete` {#airbyte.cloud.workspaces.CloudWorkspace.permanently_delete}

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

#### `permanently_delete_connection` {#airbyte.cloud.workspaces.CloudWorkspace.permanently_delete_connection}

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

#### `permanently_delete_destination` {#airbyte.cloud.workspaces.CloudWorkspace.permanently_delete_destination}

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

#### `permanently_delete_source` {#airbyte.cloud.workspaces.CloudWorkspace.permanently_delete_source}

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

#### `publish_custom_source_definition` {#airbyte.cloud.workspaces.CloudWorkspace.publish_custom_source_definition}

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

#### `rename` {#airbyte.cloud.workspaces.CloudWorkspace.rename}

<ApiMember kind="method">

<ApiSignature>

```python
def rename(self, name: str) -> airbyte.cloud.workspaces.CloudWorkspace
```

</ApiSignature>

Rename this workspace.

</ApiMember>

</ApiMember>