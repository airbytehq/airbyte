---
sidebar_label: api_util
title: airbyte._util.api_util
---

These internal functions are used to interact with the Airbyte API (module named `airbyte`).

In order to insulate users from breaking changes and to avoid general confusion around naming
and design inconsistencies, we do not expose these functions or other Airbyte API classes within
PyAirbyte. Classes and functions from the Airbyte API external library should always be wrapped in
PyAirbyte classes - unless there&#x27;s a very compelling reason to surface these models intentionally.

Similarly, modules outside of this file should try to avoid interfacing with `airbyte_api` library
directly. This will ensure a single source of truth when mapping between the `airbyte` and
`airbyte_api` libraries.

## annotations

## json

## HTTPStatus

## TYPE\_CHECKING

## Any

## Literal

## airbyte\_api

## requests

## api

## models

## SDKError

## CLOUD\_API\_ROOT

## CLOUD\_CONFIG\_API\_ROOT

## CLOUD\_CONFIG\_API\_ROOT\_ENV\_VAR

## AirbyteConnectionSyncError

## AirbyteError

## AirbyteMissingResourceError

## AirbyteMultipleResourcesError

## PyAirbyteInputError

## SecretString

## try\_get\_secret

#### JOB\_WAIT\_INTERVAL\_SECS

#### JOB\_WAIT\_TIMEOUT\_SECS\_DEFAULT

1 hour

#### JOB\_ORDER\_BY\_CREATED\_AT\_DESC

#### JOB\_ORDER\_BY\_CREATED\_AT\_ASC

#### status\_ok

```python
def status_ok(status_code: int) -> bool
```

Check if a status code is OK.

#### \_get\_sdk\_error\_context

```python
def _get_sdk_error_context(error: SDKError) -> dict[str, Any]
```

Extract context information from an SDKError for debugging.

This helper extracts the actual request URL and other useful debugging
information from the Speakeasy SDK&#x27;s SDKError exception. The SDK stores
the raw response object which contains the request details.

#### \_wrap\_sdk\_error

```python
def _wrap_sdk_error(
        error: SDKError,
        base_context: dict[str, Any] | None = None) -> AirbyteError
```

Wrap an SDKError with additional context for debugging.

This function converts a Speakeasy SDK error into an AirbyteError with
full URL context, making it easier to debug API issues like 404 errors.

#### get\_config\_api\_root

```python
def get_config_api_root(api_root: str) -> str
```

Get the configuration API root from the main API root.

Resolution order:
1. If `AIRBYTE_CLOUD_CONFIG_API_URL` environment variable is set, use that value.
2. If `api_root` matches the default Cloud API root, return the default Config API root.
3. Otherwise, raise NotImplementedError (cannot derive Config API from custom API root).

**Arguments**:

- `api_root` - The main API root URL being used.
  

**Returns**:

  The configuration API root URL.
  

**Raises**:

- `NotImplementedError` - If the Config API root cannot be determined.

#### get\_web\_url\_root

```python
def get_web_url_root(api_root: str) -> str
```

Get the web URL root from the main API root.

__TODO: This does not return a valid URL for self-managed instances, due to not knowing the__

__web URL root. Logged here:__

__- https://github.com/airbytehq/PyAirbyte/issues/563__


#### get\_airbyte\_server\_instance

```python
def get_airbyte_server_instance(
        *, api_root: str, client_id: SecretString | None,
        client_secret: SecretString | None,
        bearer_token: SecretString | None) -> airbyte_api.AirbyteAPI
```

Get an Airbyte API instance.

Supports two authentication methods (mutually exclusive):
1. OAuth2 client credentials (client_id + client_secret)
2. Bearer token authentication

**Arguments**:

- `api_root` - The API root URL.
- `client_id` - OAuth2 client ID (required if not using bearer_token).
- `client_secret` - OAuth2 client secret (required if not using bearer_token).
- `bearer_token` - Pre-generated bearer token (alternative to client credentials).
  

**Returns**:

  An authenticated AirbyteAPI instance.
  

**Raises**:

- `PyAirbyteInputError` - If authentication parameters are invalid.

#### get\_workspace

```python
def get_workspace(
        workspace_id: str, *, api_root: str, client_id: SecretString | None,
        client_secret: SecretString | None,
        bearer_token: SecretString | None) -> models.WorkspaceResponse
```

Get a workspace object.

#### list\_connections

```python
def list_connections(
    workspace_id: str,
    *,
    api_root: str,
    client_id: SecretString | None,
    client_secret: SecretString | None,
    bearer_token: SecretString | None,
    name: str | None = None,
    name_filter: Callable[[str], bool] | None = None
) -> list[models.ConnectionResponse]
```

List connections.

#### list\_workspaces

```python
def list_workspaces(
    workspace_id: str,
    *,
    api_root: str,
    client_id: SecretString | None,
    client_secret: SecretString | None,
    bearer_token: SecretString | None,
    name: str | None = None,
    name_filter: Callable[[str], bool] | None = None
) -> list[models.WorkspaceResponse]
```

List workspaces.

#### list\_sources

```python
def list_sources(
    workspace_id: str,
    *,
    api_root: str,
    client_id: SecretString | None,
    client_secret: SecretString | None,
    bearer_token: SecretString | None,
    name: str | None = None,
    name_filter: Callable[[str], bool] | None = None
) -> list[models.SourceResponse]
```

List sources.

#### list\_destinations

```python
def list_destinations(
    workspace_id: str,
    *,
    api_root: str,
    client_id: SecretString | None,
    client_secret: SecretString | None,
    bearer_token: SecretString | None,
    name: str | None = None,
    name_filter: Callable[[str], bool] | None = None
) -> list[models.DestinationResponse]
```

List destinations.

#### get\_connection

```python
def get_connection(
        workspace_id: str, connection_id: str, *, api_root: str,
        client_id: SecretString | None, client_secret: SecretString | None,
        bearer_token: SecretString | None) -> models.ConnectionResponse
```

Get a connection.

#### run\_connection

```python
def run_connection(workspace_id: str, connection_id: str, *, api_root: str,
                   client_id: SecretString | None,
                   client_secret: SecretString | None,
                   bearer_token: SecretString | None) -> models.JobResponse
```

Get a connection.

If block is True, this will block until the connection is finished running.

If raise_on_failure is True, this will raise an exception if the connection fails.

#### get\_job\_logs

```python
def get_job_logs(workspace_id: str,
                 connection_id: str,
                 limit: int = 100,
                 *,
                 api_root: str,
                 client_id: SecretString | None,
                 client_secret: SecretString | None,
                 bearer_token: SecretString | None,
                 offset: int | None = None,
                 order_by: str | None = None) -> list[models.JobResponse]
```

Get a list of jobs for a connection.

**Arguments**:

- `workspace_id` - The workspace ID.
- `connection_id` - The connection ID.
- `limit` - Maximum number of jobs to return. Defaults to 100.
- `api_root` - The API root URL.
- `client_id` - The client ID for authentication.
- `client_secret` - The client secret for authentication.
- `bearer_token` - Bearer token for authentication (alternative to client credentials).
- `offset` - Number of jobs to skip from the beginning. Defaults to None (0).
- `order_by` - Field and direction to order by (e.g., &quot;createdAt|DESC&quot;). Defaults to None.
  

**Returns**:

  A list of JobResponse objects.

#### get\_job\_info

```python
def get_job_info(job_id: int, *, api_root: str, client_id: SecretString | None,
                 client_secret: SecretString | None,
                 bearer_token: SecretString | None) -> models.JobResponse
```

Get a job.

#### create\_source

```python
def create_source(name: str,
                  *,
                  workspace_id: str,
                  config: models.SourceConfiguration | dict[str, Any],
                  definition_id: str | None = None,
                  api_root: str,
                  client_id: SecretString | None,
                  client_secret: SecretString | None,
                  bearer_token: SecretString | None) -> models.SourceResponse
```

Create a source connector instance.

Either `definition_id` or `config[sourceType]` must be provided.

#### get\_source

```python
def get_source(source_id: str, *, api_root: str,
               client_id: SecretString | None,
               client_secret: SecretString | None,
               bearer_token: SecretString | None) -> models.SourceResponse
```

Get a connection.

#### delete\_source

```python
def delete_source(source_id: str,
                  *,
                  source_name: str | None = None,
                  api_root: str,
                  client_id: SecretString | None,
                  client_secret: SecretString | None,
                  bearer_token: SecretString | None,
                  workspace_id: str | None = None,
                  safe_mode: bool = True) -> None
```

Delete a source.

**Arguments**:

- `source_id` - The source ID to delete
- `source_name` - Optional source name. If not provided and safe_mode is enabled,
  the source name will be fetched from the API to perform safety checks.
- `api_root` - The API root URL
- `client_id` - OAuth client ID
- `client_secret` - OAuth client secret
- `bearer_token` - Bearer token for authentication (alternative to client credentials).
- `workspace_id` - The workspace ID (not currently used)
- `safe_mode` - If True, requires the source name to contain &quot;delete-me&quot; or &quot;deleteme&quot;
  (case insensitive) to prevent accidental deletion. Defaults to True.
  

**Raises**:

- `PyAirbyteInputError` - If safe_mode is True and the source name does not meet
  the safety requirements.

#### patch\_source

```python
def patch_source(
    source_id: str,
    *,
    api_root: str,
    client_id: SecretString | None,
    client_secret: SecretString | None,
    bearer_token: SecretString | None,
    name: str | None = None,
    config: models.SourceConfiguration | dict[str, Any] | None = None
) -> models.SourceResponse
```

Update/patch a source configuration.

This is a destructive operation that can break existing connections if the
configuration is changed incorrectly.

**Arguments**:

- `source_id` - The ID of the source to update
- `api_root` - The API root URL
- `client_id` - Client ID for authentication
- `client_secret` - Client secret for authentication
- `bearer_token` - Bearer token for authentication (alternative to client credentials).
- `name` - Optional new name for the source
- `config` - Optional new configuration for the source
  

**Returns**:

  Updated SourceResponse object

#### \_get\_destination\_type\_str

```python
def _get_destination_type_str(
        destination: DestinationConfiguration | dict[str, Any]) -> str
```

#### create\_destination

```python
def create_destination(
        name: str, *, workspace_id: str,
        config: DestinationConfiguration | dict[str, Any], api_root: str,
        client_id: SecretString | None, client_secret: SecretString | None,
        bearer_token: SecretString | None) -> models.DestinationResponse
```

Get a connection.

#### get\_destination

```python
def get_destination(
        destination_id: str, *, api_root: str, client_id: SecretString | None,
        client_secret: SecretString | None,
        bearer_token: SecretString | None) -> models.DestinationResponse
```

Get a connection.

#### delete\_destination

```python
def delete_destination(destination_id: str,
                       *,
                       destination_name: str | None = None,
                       api_root: str,
                       client_id: SecretString | None,
                       client_secret: SecretString | None,
                       bearer_token: SecretString | None,
                       workspace_id: str | None = None,
                       safe_mode: bool = True) -> None
```

Delete a destination.

**Arguments**:

- `destination_id` - The destination ID to delete
- `destination_name` - Optional destination name. If not provided and safe_mode is enabled,
  the destination name will be fetched from the API to perform safety checks.
- `api_root` - The API root URL
- `client_id` - OAuth client ID
- `client_secret` - OAuth client secret
- `bearer_token` - Bearer token for authentication (alternative to client credentials).
- `workspace_id` - The workspace ID (not currently used)
- `safe_mode` - If True, requires the destination name to contain &quot;delete-me&quot; or &quot;deleteme&quot;
  (case insensitive) to prevent accidental deletion. Defaults to True.
  

**Raises**:

- `PyAirbyteInputError` - If safe_mode is True and the destination name does not meet
  the safety requirements.

#### patch\_destination

```python
def patch_destination(
    destination_id: str,
    *,
    api_root: str,
    client_id: SecretString | None,
    client_secret: SecretString | None,
    bearer_token: SecretString | None,
    name: str | None = None,
    config: DestinationConfiguration | dict[str, Any] | None = None
) -> models.DestinationResponse
```

Update/patch a destination configuration.

This is a destructive operation that can break existing connections if the
configuration is changed incorrectly.

**Arguments**:

- `destination_id` - The ID of the destination to update
- `api_root` - The API root URL
- `client_id` - Client ID for authentication
- `client_secret` - Client secret for authentication
- `bearer_token` - Bearer token for authentication (alternative to client credentials).
- `name` - Optional new name for the destination
- `config` - Optional new configuration for the destination
  

**Returns**:

  Updated DestinationResponse object

#### build\_stream\_configurations

```python
def build_stream_configurations(
        stream_names: list[str]) -> models.StreamConfigurations
```

Build a StreamConfigurations object from a list of stream names.

This helper creates the proper API model structure for stream configurations.
Used by both connection creation and updates.

**Arguments**:

- `stream_names` - List of stream names to include in the configuration
  

**Returns**:

  StreamConfigurations object ready for API submission

#### create\_connection

```python
def create_connection(
        name: str,
        *,
        source_id: str,
        destination_id: str,
        api_root: str,
        client_id: SecretString | None,
        client_secret: SecretString | None,
        bearer_token: SecretString | None,
        workspace_id: str | None = None,
        prefix: str,
        selected_stream_names: list[str]) -> models.ConnectionResponse
```

#### get\_connection\_by\_name

```python
def get_connection_by_name(
        workspace_id: str, connection_name: str, *, api_root: str,
        client_id: SecretString | None, client_secret: SecretString | None,
        bearer_token: SecretString | None) -> models.ConnectionResponse
```

Get a connection.

#### \_is\_safe\_name\_to\_delete

```python
def _is_safe_name_to_delete(name: str) -> bool
```

Check if a name is safe to delete.

Requires the name to contain either &quot;delete-me&quot; or &quot;deleteme&quot; (case insensitive).

#### delete\_connection

```python
def delete_connection(connection_id: str,
                      connection_name: str | None = None,
                      *,
                      api_root: str,
                      workspace_id: str,
                      client_id: SecretString | None,
                      client_secret: SecretString | None,
                      bearer_token: SecretString | None,
                      safe_mode: bool = True) -> None
```

Delete a connection.

**Arguments**:

- `connection_id` - The connection ID to delete
- `connection_name` - Optional connection name. If not provided and safe_mode is enabled,
  the connection name will be fetched from the API to perform safety checks.
- `api_root` - The API root URL
- `workspace_id` - The workspace ID
- `client_id` - OAuth client ID
- `client_secret` - OAuth client secret
- `bearer_token` - Bearer token for authentication (alternative to client credentials).
- `safe_mode` - If True, requires the connection name to contain &quot;delete-me&quot; or &quot;deleteme&quot;
  (case insensitive) to prevent accidental deletion. Defaults to True.
  

**Raises**:

- `PyAirbyteInputError` - If safe_mode is True and the connection name does not meet
  the safety requirements.

#### patch\_connection

```python
def patch_connection(
    connection_id: str,
    *,
    api_root: str,
    client_id: SecretString | None,
    client_secret: SecretString | None,
    bearer_token: SecretString | None,
    name: str | None = None,
    configurations: models.StreamConfigurationsInput | None = None,
    schedule: models.AirbyteAPIConnectionSchedule | None = None,
    prefix: str | None = None,
    status: models.ConnectionStatusEnum | None = None
) -> models.ConnectionResponse
```

Update/patch a connection configuration.

This is a destructive operation that can break existing connections if the
configuration is changed incorrectly.

**Arguments**:

- `connection_id` - The ID of the connection to update
- `api_root` - The API root URL
- `client_id` - Client ID for authentication
- `client_secret` - Client secret for authentication
- `bearer_token` - Bearer token for authentication (alternative to client credentials).
- `name` - Optional new name for the connection
- `configurations` - Optional new stream configurations
- `schedule` - Optional new sync schedule
- `prefix` - Optional new table prefix
- `status` - Optional new connection status
  

**Returns**:

  Updated ConnectionResponse object

#### get\_bearer\_token

```python
def get_bearer_token(*,
                     client_id: SecretString,
                     client_secret: SecretString,
                     api_root: str = CLOUD_API_ROOT) -> SecretString
```

Get a bearer token.

https://reference.airbyte.com/reference/createaccesstoken

#### \_make\_config\_api\_request

```python
def _make_config_api_request(
        *, api_root: str, path: str, json: dict[str, Any],
        client_id: SecretString | None, client_secret: SecretString | None,
        bearer_token: SecretString | None) -> dict[str, Any]
```

#### check\_connector

```python
def check_connector(*,
                    actor_id: str,
                    connector_type: Literal["source", "destination"],
                    client_id: SecretString | None,
                    client_secret: SecretString | None,
                    bearer_token: SecretString | None,
                    workspace_id: str | None = None,
                    api_root: str = CLOUD_API_ROOT) -> tuple[bool, str | None]
```

Check a source.

Raises an exception if the check fails. Uses one of these endpoints:

- /v1/sources/check_connection: https://github.com/airbytehq/airbyte-platform-internal/blob/10bb92e1745a282e785eedfcbed1ba72654c4e4e/oss/airbyte-api/server-api/src/main/openapi/config.yaml#L1409
- /v1/destinations/check_connection: https://github.com/airbytehq/airbyte-platform-internal/blob/10bb92e1745a282e785eedfcbed1ba72654c4e4e/oss/airbyte-api/server-api/src/main/openapi/config.yaml#L1995

#### validate\_yaml\_manifest

```python
def validate_yaml_manifest(
        manifest: Any,
        *,
        raise_on_error: bool = True) -> tuple[bool, str | None]
```

Validate a YAML connector manifest structure.

Performs basic client-side validation before sending to API.

**Arguments**:

- `manifest` - The manifest to validate (should be a dictionary).
- `raise_on_error` - Whether to raise an exception on validation failure.
  

**Returns**:

  Tuple of (is_valid, error_message)

#### create\_custom\_yaml\_source\_definition

```python
def create_custom_yaml_source_definition(
    name: str, *, workspace_id: str, manifest: dict[str, Any], api_root: str,
    client_id: SecretString | None, client_secret: SecretString | None,
    bearer_token: SecretString | None
) -> models.DeclarativeSourceDefinitionResponse
```

Create a custom YAML source definition.

#### list\_custom\_yaml\_source\_definitions

```python
def list_custom_yaml_source_definitions(
    workspace_id: str, *, api_root: str, client_id: SecretString | None,
    client_secret: SecretString | None, bearer_token: SecretString | None
) -> list[models.DeclarativeSourceDefinitionResponse]
```

List all custom YAML source definitions in a workspace.

#### get\_custom\_yaml\_source\_definition

```python
def get_custom_yaml_source_definition(
    workspace_id: str, definition_id: str, *, api_root: str,
    client_id: SecretString | None, client_secret: SecretString | None,
    bearer_token: SecretString | None
) -> models.DeclarativeSourceDefinitionResponse
```

Get a specific custom YAML source definition.

#### update\_custom\_yaml\_source\_definition

```python
def update_custom_yaml_source_definition(
    workspace_id: str, definition_id: str, *, manifest: dict[str, Any],
    api_root: str, client_id: SecretString | None,
    client_secret: SecretString | None, bearer_token: SecretString | None
) -> models.DeclarativeSourceDefinitionResponse
```

Update a custom YAML source definition.

#### delete\_custom\_yaml\_source\_definition

```python
def delete_custom_yaml_source_definition(workspace_id: str,
                                         definition_id: str,
                                         *,
                                         api_root: str,
                                         client_id: SecretString | None,
                                         client_secret: SecretString | None,
                                         bearer_token: SecretString | None,
                                         safe_mode: bool = True) -> None
```

Delete a custom YAML source definition.

**Arguments**:

- `workspace_id` - The workspace ID
- `definition_id` - The definition ID to delete
- `api_root` - The API root URL
- `client_id` - OAuth client ID
- `client_secret` - OAuth client secret
- `bearer_token` - Bearer token for authentication (alternative to client credentials).
- `safe_mode` - If True, requires the connector name to contain &quot;delete-me&quot; or &quot;deleteme&quot;
  (case insensitive) to prevent accidental deletion. Defaults to True.
  

**Raises**:

- `PyAirbyteInputError` - If safe_mode is True and the connector name does not meet
  the safety requirements.

#### get\_connector\_builder\_project\_for\_definition\_id

```python
def get_connector_builder_project_for_definition_id(
        *, workspace_id: str, definition_id: str, api_root: str,
        client_id: SecretString | None, client_secret: SecretString | None,
        bearer_token: SecretString | None) -> str | None
```

Get the connector builder project ID for a declarative source definition.

Uses the Config API endpoint:
/v1/connector_builder_projects/get_for_definition_id

See: https://github.com/airbytehq/airbyte-platform-internal/blob/master/oss/airbyte-api/server-api/src/main/openapi/config.yaml#L1268

**Arguments**:

- `workspace_id` - The workspace ID
- `definition_id` - The declarative source definition ID (actorDefinitionId)
- `api_root` - The API root URL
- `client_id` - OAuth client ID
- `client_secret` - OAuth client secret
- `bearer_token` - Bearer token for authentication (alternative to client credentials).
  

**Returns**:

  The builder project ID if found, None otherwise (can be null in API response)

#### update\_connector\_builder\_project\_testing\_values

```python
def update_connector_builder_project_testing_values(
        *, workspace_id: str, builder_project_id: str,
        testing_values: dict[str, Any], spec: dict[str, Any], api_root: str,
        client_id: SecretString | None, client_secret: SecretString | None,
        bearer_token: SecretString | None) -> dict[str, Any]
```

Update the testing values for a connector builder project.

This call replaces the entire testing values object stored for the project.
Any keys not included in `testing_values` will be removed.

Uses the Config API endpoint:
/v1/connector_builder_projects/update_testing_values

**Arguments**:

- `workspace_id` - The workspace ID
- `builder_project_id` - The connector builder project ID
- `testing_values` - The testing values (config blob) to persist. This replaces
  any existing testing values entirely.
- `spec` - The source definition specification (connector spec)
- `api_root` - The API root URL
- `client_id` - OAuth client ID
- `client_secret` - OAuth client secret
- `bearer_token` - Bearer token for authentication (alternative to client credentials).
  

**Returns**:

  The updated testing values from the API response

#### list\_organizations\_for\_user

```python
def list_organizations_for_user(
        *, api_root: str, client_id: SecretString | None,
        client_secret: SecretString | None, bearer_token: SecretString | None
) -> list[models.OrganizationResponse]
```

List all organizations accessible to the current user.

Uses the public API endpoint: GET /organizations

**Arguments**:

- `api_root` - The API root URL
- `client_id` - OAuth client ID
- `client_secret` - OAuth client secret
- `bearer_token` - Bearer token for authentication (alternative to client credentials).
  

**Returns**:

  List of OrganizationResponse objects containing organization_id, organization_name, email

#### list\_workspaces\_in\_organization

```python
def list_workspaces_in_organization(
        organization_id: str,
        *,
        api_root: str,
        client_id: SecretString | None,
        client_secret: SecretString | None,
        bearer_token: SecretString | None,
        name_contains: str | None = None,
        max_items_limit: int | None = None) -> list[dict[str, Any]]
```

List workspaces within a specific organization.

Uses the Config API endpoint: POST /v1/workspaces/list_by_organization_id

**Arguments**:

- `organization_id` - The organization ID to list workspaces for
- `api_root` - The API root URL
- `client_id` - OAuth client ID
- `client_secret` - OAuth client secret
- `bearer_token` - Bearer token for authentication (alternative to client credentials).
- `name_contains` - Optional substring filter for workspace names (server-side)
- `max_items_limit` - Optional maximum number of workspaces to return
  

**Returns**:

  List of workspace dictionaries containing workspaceId, organizationId, name, slug, etc.

#### get\_workspace\_organization\_info

```python
def get_workspace_organization_info(
        workspace_id: str, *, api_root: str, client_id: SecretString | None,
        client_secret: SecretString | None,
        bearer_token: SecretString | None) -> dict[str, Any]
```

Get organization info for a workspace.

Uses the Config API endpoint: POST /v1/workspaces/get_organization_info

This is an efficient O(1) lookup that directly retrieves the organization
info for a workspace without needing to iterate through all organizations.

**Arguments**:

- `workspace_id` - The workspace ID to look up
- `api_root` - The API root URL
- `client_id` - OAuth client ID
- `client_secret` - OAuth client secret
- `bearer_token` - Bearer token for authentication (alternative to client credentials).
  

**Returns**:

  Dictionary containing organization info:
  - organizationId: The organization ID
  - organizationName: The organization name
  - sso: Whether SSO is enabled
  - billing: Billing information (optional)

#### get\_connection\_state

```python
def get_connection_state(connection_id: str, *, api_root: str,
                         client_id: SecretString | None,
                         client_secret: SecretString | None,
                         bearer_token: SecretString | None) -> dict[str, Any]
```

Get the state for a connection.

Uses the Config API endpoint: POST /v1/state/get

**Arguments**:

- `connection_id` - The connection ID to get state for
- `api_root` - The API root URL
- `client_id` - OAuth client ID
- `client_secret` - OAuth client secret
- `bearer_token` - Bearer token for authentication (alternative to client credentials).
  

**Returns**:

  Dictionary containing the connection state.

#### get\_connection\_catalog

```python
def get_connection_catalog(
        connection_id: str, *, api_root: str, client_id: SecretString | None,
        client_secret: SecretString | None,
        bearer_token: SecretString | None) -> dict[str, Any]
```

Get the configured catalog for a connection.

Uses the Config API endpoint: POST /v1/web_backend/connections/get

This returns the full connection info including the syncCatalog field,
which contains the configured catalog with full stream schemas.

**Arguments**:

- `connection_id` - The connection ID to get catalog for
- `api_root` - The API root URL
- `client_id` - OAuth client ID
- `client_secret` - OAuth client secret
- `bearer_token` - Bearer token for authentication (alternative to client credentials).
  

**Returns**:

  Dictionary containing the connection info with syncCatalog.

