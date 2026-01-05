---
sidebar_label: connectors
title: airbyte.cloud.connectors
---

Cloud connectors module for working with Cloud sources and destinations.

This module provides classes for working with Cloud sources and destinations. Rather
than creating `CloudConnector` objects directly, it is recommended to use the
`airbyte.cloud.workspaces` module to create and manage cloud connector objects.

Classes:
  - `CloudConnector`: A cloud connector object.
  - `CloudSource`: A cloud source object.
  - `CloudDestination`: A cloud destination object.

## Usage Examples

Obtain a cloud source object and run a `check` on it:

```python
from airbyte.cloud import CloudWorkspace

workspace = CloudWorkspace(
    workspace_id="...",
    client_id="...",
    client_secret="...",
)

# Get the cloud source object
cloud_source = workspace.get_source("...")

# Check the source configuration and credentials
check_result = cloud_source.check()
if check_result:
    # Truthy if the check was successful
    print("Check successful")
else:
    # Stringify the check result to get the error message
    print(f"Check failed: {check_result}")
```

## annotations

## abc

## dataclass

## Path

## TYPE\_CHECKING

## Any

## ClassVar

## Literal

## yaml

## api\_models

## exc

## api\_util

## text\_util

## CheckResult Objects

```python
@dataclass
class CheckResult()
```

A cloud check result object.

#### success

Whether the check result is valid.

#### error\_message

None if the check was successful. Otherwise the failure message from the check result.

#### internal\_error

None if the check was able to be run. Otherwise, this will describe the internal failure.

#### \_\_bool\_\_

```python
def __bool__() -> bool
```

Truthy when check was successful.

#### \_\_str\_\_

```python
def __str__() -> str
```

Get a string representation of the check result.

#### \_\_repr\_\_

```python
def __repr__() -> str
```

Get a string representation of the check result.

## CloudConnector Objects

```python
class CloudConnector(abc.ABC)
```

A cloud connector is a deployed source or destination on Airbyte Cloud.

You can use a connector object to manage the connector.

#### connector\_type

The type of the connector.

#### \_\_init\_\_

```python
def __init__(workspace: CloudWorkspace, connector_id: str) -> None
```

Initialize a cloud connector object.

#### name

```python
@property
def name() -> str | None
```

Get the display name of the connector, if available.

E.g. &quot;My Postgres Source&quot;, not the canonical connector name (&quot;source-postgres&quot;).

#### \_fetch\_connector\_info

```python
@abc.abstractmethod
def _fetch_connector_info(
) -> api_models.SourceResponse | api_models.DestinationResponse
```

Populate the connector with data from the API.

#### connector\_url

```python
@property
def connector_url() -> str
```

Get the web URL of the source connector.

#### \_\_repr\_\_

```python
def __repr__() -> str
```

String representation of the connector.

#### permanently\_delete

```python
def permanently_delete() -> None
```

Permanently delete the connector.

#### check

```python
def check(*, raise_on_error: bool = True) -> CheckResult
```

Check the connector.

**Returns**:

  A `CheckResult` object containing the result. The object is truthy if the check was
  successful and falsy otherwise. The error message is available in the `error_message`
  or by converting the object to a string.

## CloudSource Objects

```python
class CloudSource(CloudConnector)
```

A cloud source is a source that is deployed on Airbyte Cloud.

#### connector\_type

The type of the connector.

#### source\_id

```python
@property
def source_id() -> str
```

Get the ID of the source.

This is an alias for `connector_id`.

#### \_fetch\_connector\_info

```python
def _fetch_connector_info() -> api_models.SourceResponse
```

Populate the source with data from the API.

#### rename

```python
def rename(name: str) -> CloudSource
```

Rename the source.

**Arguments**:

- `name` - New name for the source
  

**Returns**:

  Updated CloudSource object with refreshed info

#### update\_config

```python
def update_config(config: dict[str, Any]) -> CloudSource
```

Update the source configuration.

This is a destructive operation that can break existing connections if the
configuration is changed incorrectly. Use with caution.

**Arguments**:

- `config` - New configuration for the source
  

**Returns**:

  Updated CloudSource object with refreshed info

#### \_from\_source\_response

```python
@classmethod
def _from_source_response(
        cls, workspace: CloudWorkspace,
        source_response: api_models.SourceResponse) -> CloudSource
```

Internal factory method.

Creates a CloudSource object from a REST API SourceResponse object.

## CloudDestination Objects

```python
class CloudDestination(CloudConnector)
```

A cloud destination is a destination that is deployed on Airbyte Cloud.

#### connector\_type

The type of the connector.

#### destination\_id

```python
@property
def destination_id() -> str
```

Get the ID of the destination.

This is an alias for `connector_id`.

#### \_fetch\_connector\_info

```python
def _fetch_connector_info() -> api_models.DestinationResponse
```

Populate the destination with data from the API.

#### rename

```python
def rename(name: str) -> CloudDestination
```

Rename the destination.

**Arguments**:

- `name` - New name for the destination
  

**Returns**:

  Updated CloudDestination object with refreshed info

#### update\_config

```python
def update_config(config: dict[str, Any]) -> CloudDestination
```

Update the destination configuration.

This is a destructive operation that can break existing connections if the
configuration is changed incorrectly. Use with caution.

**Arguments**:

- `config` - New configuration for the destination
  

**Returns**:

  Updated CloudDestination object with refreshed info

#### \_from\_destination\_response

```python
@classmethod
def _from_destination_response(
        cls, workspace: CloudWorkspace,
        destination_response: api_models.DestinationResponse
) -> CloudDestination
```

Internal factory method.

Creates a CloudDestination object from a REST API DestinationResponse object.

## CustomCloudSourceDefinition Objects

```python
class CustomCloudSourceDefinition()
```

A custom source connector definition in Airbyte Cloud.

This represents either a YAML (declarative) or Docker-based custom source definition.

#### connector\_type

The type of the connector: &#x27;source&#x27; or &#x27;destination&#x27;.

#### \_\_init\_\_

```python
def __init__(workspace: CloudWorkspace, definition_id: str,
             definition_type: Literal["yaml", "docker"]) -> None
```

Initialize a custom source definition object.

Note: Only YAML connectors are currently supported. Docker connectors
will raise NotImplementedError.

#### \_fetch\_definition\_info

```python
def _fetch_definition_info() -> api_models.DeclarativeSourceDefinitionResponse
```

Fetch definition info from the API.

#### name

```python
@property
def name() -> str
```

Get the display name of the custom connector definition.

#### manifest

```python
@property
def manifest() -> dict[str, Any] | None
```

Get the Low-code CDK manifest. Only present for YAML connectors.

#### version

```python
@property
def version() -> str | None
```

Get the manifest version. Only present for YAML connectors.

#### docker\_repository

```python
@property
def docker_repository() -> str | None
```

Get the Docker repository. Only present for Docker connectors.

Note: Docker connectors are not yet supported and will raise NotImplementedError.

#### docker\_image\_tag

```python
@property
def docker_image_tag() -> str | None
```

Get the Docker image tag. Only present for Docker connectors.

Note: Docker connectors are not yet supported and will raise NotImplementedError.

#### documentation\_url

```python
@property
def documentation_url() -> str | None
```

Get the documentation URL. Only present for Docker connectors.

Note: Docker connectors are not yet supported and will raise NotImplementedError.

#### connector\_builder\_project\_id

```python
@property
def connector_builder_project_id() -> str | None
```

Get the connector builder project ID. Only present for YAML connectors.

#### connector\_builder\_project\_url

```python
@property
def connector_builder_project_url() -> str | None
```

Get the connector builder project URL. Only present for YAML connectors.

#### definition\_url

```python
@property
def definition_url() -> str
```

Get the web URL of the custom source definition.

For YAML connectors, this is the connector builder &#x27;edit&#x27; URL.
For Docker connectors, this is the custom connectors page.

#### permanently\_delete

```python
def permanently_delete(*, safe_mode: bool = True) -> None
```

Permanently delete this custom source definition.

**Arguments**:

- `safe_mode` - If True, requires the connector name to contain &quot;delete-me&quot; or &quot;deleteme&quot;
  (case insensitive) to prevent accidental deletion. Defaults to True.

#### update\_definition

```python
def update_definition(
        *,
        manifest_yaml: dict[str, Any] | Path | str | None = None,
        docker_tag: str | None = None,
        pre_validate: bool = True) -> CustomCloudSourceDefinition
```

Update this custom source definition.

You must specify EXACTLY ONE of manifest_yaml (for YAML connectors) OR
docker_tag (for Docker connectors), but not both.

For YAML connectors: updates the manifest
For Docker connectors: Not yet supported (raises NotImplementedError)

**Arguments**:

- `manifest_yaml` - New manifest (YAML connectors only)
- `docker_tag` - New Docker tag (Docker connectors only, not yet supported)
- `pre_validate` - Whether to validate manifest (YAML only)
  

**Returns**:

  Updated CustomCloudSourceDefinition object
  

**Raises**:

- `PyAirbyteInputError` - If both or neither parameters are provided
- `NotImplementedError` - If docker_tag is provided (Docker not yet supported)

#### rename

```python
def rename(new_name: str) -> CustomCloudSourceDefinition
```

Rename this custom source definition.

Note: Only Docker custom sources can be renamed. YAML custom sources
cannot be renamed as their names are derived from the manifest.

**Arguments**:

- `new_name` - New display name for the connector
  

**Returns**:

  Updated CustomCloudSourceDefinition object
  

**Raises**:

- `PyAirbyteInputError` - If attempting to rename a YAML connector
- `NotImplementedError` - If attempting to rename a Docker connector (not yet supported)

#### \_\_repr\_\_

```python
def __repr__() -> str
```

String representation.

#### \_from\_yaml\_response

```python
@classmethod
def _from_yaml_response(
    cls, workspace: CloudWorkspace,
    response: api_models.DeclarativeSourceDefinitionResponse
) -> CustomCloudSourceDefinition
```

Internal factory method for YAML connectors.

#### deploy\_source

```python
def deploy_source(name: str,
                  config: dict[str, Any],
                  *,
                  unique: bool = True,
                  random_name_suffix: bool = False) -> CloudSource
```

Deploy a new cloud source using this custom source definition.

**Arguments**:

- `name` - The name for the new source.
- `config` - A dictionary containing the connection configuration for the new source.
- `unique` - If True, raises an error if a source with the same name already exists
  in the workspace. Default is True.
- `random_name_suffix` - If True, appends a random suffix to the name to ensure uniqueness.
  Default is False.
  

**Returns**:

  A `CloudSource` object representing the newly created source.

#### set\_testing\_values

```python
def set_testing_values(
        testing_values: dict[str, Any]) -> CustomCloudSourceDefinition
```

Set the testing values for this custom source definition&#x27;s connector builder project.

Testing values are the input configuration values used when testing the connector
in the Connector Builder UI. Setting these values allows users to immediately
run test read operations after deploying a custom source to the Builder UI.

This method replaces any existing testing values with the provided dictionary.
Pass the full set of values you want to persist, not just the fields you&#x27;re changing.

**Arguments**:

- `testing_values` - A dictionary containing the configuration values to use for testing.
  This should match the connector&#x27;s spec schema. Replaces any existing values.
  

**Returns**:

  This `CustomCloudSourceDefinition` object (for method chaining).
  

**Raises**:

- `NotImplementedError` - If this is not a YAML custom source definition.
- `PyAirbyteInputError` - If the connector builder project ID cannot be found.

