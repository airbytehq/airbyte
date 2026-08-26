---
id: airbyte-cloud-connectors
title: "airbyte.cloud.connectors Module"
sidebar_label: "airbyte.cloud.connectors"
---

# `airbyte.cloud.connectors` Module

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

### `CheckResult` {#airbyte.cloud.connectors.CheckResult}

<ApiMember kind="class">

<ApiSignature>

```python
class CheckResult(
    success: bool,
    error_message: str | None = None,
    internal_error: str | None = None,
)
```

</ApiSignature>

A cloud check result object.

#### Attributes {#airbyte.cloud.connectors.CheckResult--attributes}

- **`error_message`**&nbsp;(`str | None`)

  None if the check was successful. Otherwise the failure message from the check result.

- **`internal_error`**&nbsp;(`str | None`)

  None if the check was able to be run. Otherwise, this will describe the internal failure.

- **`success`**&nbsp;(`bool`)

  Whether the check result is valid.

</ApiMember>

### `CloudConnector` {#airbyte.cloud.connectors.CloudConnector}

<ApiMember kind="class">

<ApiSignature>

```python
class CloudConnector(workspace: CloudWorkspace, connector_id: str)
```

</ApiSignature>

A cloud connector is a deployed source or destination on Airbyte Cloud.

You can use a connector object to manage the connector.

Initialize a cloud connector object.

**Bases:** `abc.ABC`

**Subclasses:** `airbyte.cloud.connectors.CloudDestination`, `airbyte.cloud.connectors.CloudSource`

#### Attributes {#airbyte.cloud.connectors.CloudConnector--attributes}

- **`connector_type`**&nbsp;(`ClassVar[Literal['source', 'destination']]`)

  The type of the connector.

- **`connector_id`**

  The ID of the connector.

- **`connector_url`**&nbsp;(`str`)

  Get the web URL of the source connector.

- **`definition_id`**&nbsp;(`str`)

  Get the connector definition ID.

  E.g. the definition ID for `source-postgres`, not the ID of this deployed connector.

- **`name`**&nbsp;(`str | None`)

  Get the display name of the connector, if available.

  E.g. "My Postgres Source", not the canonical connector name ("source-postgres").

- **`workspace`**

  The workspace that the connector belongs to.

#### `check` {#airbyte.cloud.connectors.CloudConnector.check}

<ApiMember kind="method">

<ApiSignature>

```python
def check(
    self,
    *,
    raise_on_error: bool = True,
) -> airbyte.cloud.connectors.CheckResult
```

</ApiSignature>

Check the connector.

**Returns:**

A `CheckResult` object containing the result. The object is truthy if the check was
successful and falsy otherwise. The error message is available in the `error_message`
or by converting the object to a string.

</ApiMember>

#### `permanently_delete` {#airbyte.cloud.connectors.CloudConnector.permanently_delete}

<ApiMember kind="method">

<ApiSignature>

```python
def permanently_delete(self) -> None
```

</ApiSignature>

Permanently delete the connector.

</ApiMember>

</ApiMember>

### `CloudDestination` {#airbyte.cloud.connectors.CloudDestination}

<ApiMember kind="class">

<ApiSignature>

```python
class CloudDestination(workspace: CloudWorkspace, connector_id: str)
```

</ApiSignature>

A cloud destination is a destination that is deployed on Airbyte Cloud.

Initialize a cloud connector object.

**Bases:** `airbyte.cloud.connectors.CloudConnector`, `abc.ABC`

#### Attributes {#airbyte.cloud.connectors.CloudDestination--attributes}

- **`destination_id`**&nbsp;(`str`)

  Get the ID of the destination.

  This is an alias for `connector_id`.

#### `rename` {#airbyte.cloud.connectors.CloudDestination.rename}

<ApiMember kind="method">

<ApiSignature>

```python
def rename(self, name: str) -> airbyte.cloud.connectors.CloudDestination
```

</ApiSignature>

Rename the destination.

**Args:**

- **`name`**: New name for the destination

**Returns:**

Updated CloudDestination object with refreshed info

</ApiMember>

#### `update_config` {#airbyte.cloud.connectors.CloudDestination.update_config}

<ApiMember kind="method">

<ApiSignature>

```python
def update_config(
    self,
    config: dict[str, Any],
) -> airbyte.cloud.connectors.CloudDestination
```

</ApiSignature>

Update the destination configuration.

This is a destructive operation that can break existing connections if the
configuration is changed incorrectly. Use with caution.

**Args:**

- **`config`**: New configuration for the destination

**Returns:**

Updated CloudDestination object with refreshed info

</ApiMember>

</ApiMember>

### `CloudSource` {#airbyte.cloud.connectors.CloudSource}

<ApiMember kind="class">

<ApiSignature>

```python
class CloudSource(workspace: CloudWorkspace, connector_id: str)
```

</ApiSignature>

A cloud source is a source that is deployed on Airbyte Cloud.

Initialize a cloud connector object.

**Bases:** `airbyte.cloud.connectors.CloudConnector`, `abc.ABC`

#### Attributes {#airbyte.cloud.connectors.CloudSource--attributes}

- **`source_id`**&nbsp;(`str`)

  Get the ID of the source.

  This is an alias for `connector_id`.

#### `rename` {#airbyte.cloud.connectors.CloudSource.rename}

<ApiMember kind="method">

<ApiSignature>

```python
def rename(self, name: str) -> airbyte.cloud.connectors.CloudSource
```

</ApiSignature>

Rename the source.

**Args:**

- **`name`**: New name for the source

**Returns:**

Updated CloudSource object with refreshed info

</ApiMember>

#### `update_config` {#airbyte.cloud.connectors.CloudSource.update_config}

<ApiMember kind="method">

<ApiSignature>

```python
def update_config(
    self,
    config: dict[str, Any],
) -> airbyte.cloud.connectors.CloudSource
```

</ApiSignature>

Update the source configuration.

This is a destructive operation that can break existing connections if the
configuration is changed incorrectly. Use with caution.

**Args:**

- **`config`**: New configuration for the source

**Returns:**

Updated CloudSource object with refreshed info

</ApiMember>

</ApiMember>

### `CustomCloudSourceDefinition` {#airbyte.cloud.connectors.CustomCloudSourceDefinition}

<ApiMember kind="class">

<ApiSignature>

```python
class CustomCloudSourceDefinition(
    workspace: CloudWorkspace,
    definition_id: str,
    definition_type: "Literal['yaml', 'docker']",
)
```

</ApiSignature>

A custom source connector definition in Airbyte Cloud.

This represents either a YAML (declarative) or Docker-based custom source definition.

Initialize a custom source definition object.

Note: Only YAML connectors are currently supported. Docker connectors
will raise NotImplementedError.

#### Attributes {#airbyte.cloud.connectors.CustomCloudSourceDefinition--attributes}

- **`connector_type`**&nbsp;(`ClassVar[Literal['source', 'destination']]`)

  The type of the connector: 'source' or 'destination'.

- **`connector_builder_project_id`**&nbsp;(`str | None`)

  Get the connector builder project ID. Only present for YAML connectors.

- **`connector_builder_project_url`**&nbsp;(`str | None`)

  Get the connector builder project URL. Only present for YAML connectors.

- **`definition_url`**&nbsp;(`str`)

  Get the web URL of the custom source definition.

  For YAML connectors, this is the connector builder 'edit' URL.
  For Docker connectors, this is the custom connectors page.

- **`docker_image_tag`**&nbsp;(`str | None`)

  Get the Docker image tag. Only present for Docker connectors.

  Note: Docker connectors are not yet supported and will raise NotImplementedError.

- **`docker_repository`**&nbsp;(`str | None`)

  Get the Docker repository. Only present for Docker connectors.

  Note: Docker connectors are not yet supported and will raise NotImplementedError.

- **`documentation_url`**&nbsp;(`str | None`)

  Get the documentation URL. Only present for Docker connectors.

  Note: Docker connectors are not yet supported and will raise NotImplementedError.

- **`draft_manifest`**&nbsp;(`dict[str, Any] | None`)

  Get the draft (unpublished) manifest from the Connector Builder, if one exists.

  This reads the working draft that has been saved in the Connector Builder UI
  but not yet published. Returns None if no draft exists or if this is not a
  YAML connector.

  **Returns:**

  The draft manifest as a dictionary, or None if no draft exists.

- **`has_draft`**&nbsp;(`bool | None`)

  Check whether this definition has an unpublished draft in Connector Builder.

  **Returns:**

  True if a draft exists, False if no draft exists,
  or None if this is not a YAML connector or the project ID is unavailable.

- **`manifest`**&nbsp;(`dict[str, Any] | None`)

  Get the Low-code CDK manifest. Only present for YAML connectors.

- **`name`**&nbsp;(`str`)

  Get the display name of the custom connector definition.

- **`version`**&nbsp;(`str | None`)

  Get the manifest version. Only present for YAML connectors.

#### `deploy_source` {#airbyte.cloud.connectors.CustomCloudSourceDefinition.deploy_source}

<ApiMember kind="method">

<ApiSignature>

```python
def deploy_source(
    self,
    name: str,
    config: dict[str, Any],
    *,
    unique: bool = True,
    random_name_suffix: bool = False,
) -> airbyte.cloud.connectors.CloudSource
```

</ApiSignature>

Deploy a new cloud source using this custom source definition.

**Args:**

- **`name`**: The name for the new source.
- **`config`**: A dictionary containing the connection configuration for the new source.
- **`unique`**: If True, raises an error if a source with the same name already exists in the workspace. Default is True.
- **`random_name_suffix`**: If True, appends a random suffix to the name to ensure uniqueness. Default is False.

**Returns:**

A `CloudSource` object representing the newly created source.

</ApiMember>

#### `get_builder_project_data` {#airbyte.cloud.connectors.CustomCloudSourceDefinition.get_builder_project_data}

<ApiMember kind="method">

<ApiSignature>

```python
def get_builder_project_data(
    self,
    *,
    use_cache: bool = True,
) -> dict[str, typing.Any]
```

</ApiSignature>

Fetch the full connector builder project data, including draft manifest if present.

This calls the `/v1/connector_builder_projects/get_with_manifest` endpoint which returns
the project metadata and draft manifest (if one exists).

**Args:**

- **`use_cache`**: If True, return cached data from a previous call if available. Set to False to force a fresh API request. Defaults to True.

**Returns:**

- **`A dictionary containing the builder project details. Key fields include`**: - builderProject: The project metadata (name, hasDraft, activeDeclarativeManifestVersion, etc.) - declarativeManifest: The draft manifest data (if hasDraft is True), which contains a 'manifest' field with the actual YAML manifest dict.

**Raises:**

- **`NotImplementedError`**: If this is not a YAML custom source definition.
- **`PyAirbyteInputError`**: If the connector builder project ID cannot be found.

</ApiMember>

#### `permanently_delete` {#airbyte.cloud.connectors.CustomCloudSourceDefinition.permanently_delete}

<ApiMember kind="method">

<ApiSignature>

```python
def permanently_delete(self, *, safe_mode: bool = True) -> None
```

</ApiSignature>

Permanently delete this custom source definition.

**Args:**

- **`safe_mode`**: If True, requires the connector name to contain "delete-me" or "deleteme" (case insensitive) to prevent accidental deletion. Defaults to True.

</ApiMember>

#### `rename` {#airbyte.cloud.connectors.CustomCloudSourceDefinition.rename}

<ApiMember kind="method">

<ApiSignature>

```python
def rename(
    self,
    new_name: str,
) -> airbyte.cloud.connectors.CustomCloudSourceDefinition
```

</ApiSignature>

Rename this custom source definition.

Note: Only Docker custom sources can be renamed. YAML custom sources
cannot be renamed as their names are derived from the manifest.

**Args:**

- **`new_name`**: New display name for the connector

**Returns:**

Updated CustomCloudSourceDefinition object

**Raises:**

- **`PyAirbyteInputError`**: If attempting to rename a YAML connector
- **`NotImplementedError`**: If attempting to rename a Docker connector (not yet supported)

</ApiMember>

#### `set_testing_values` {#airbyte.cloud.connectors.CustomCloudSourceDefinition.set_testing_values}

<ApiMember kind="method">

<ApiSignature>

```python
def set_testing_values(
    self,
    testing_values: dict[str, Any],
) -> airbyte.cloud.connectors.CustomCloudSourceDefinition
```

</ApiSignature>

Set the testing values for this custom source definition's connector builder project.

Testing values are the input configuration values used when testing the connector
in the Connector Builder UI. Setting these values allows users to immediately
run test read operations after deploying a custom source to the Builder UI.

This method replaces any existing testing values with the provided dictionary.
Pass the full set of values you want to persist, not just the fields you're changing.

**Args:**

- **`testing_values`**: A dictionary containing the configuration values to use for testing. This should match the connector's spec schema. Replaces any existing values.

**Returns:**

This `CustomCloudSourceDefinition` object (for method chaining).

**Raises:**

- **`NotImplementedError`**: If this is not a YAML custom source definition.
- **`PyAirbyteInputError`**: If the connector builder project ID cannot be found.

</ApiMember>

#### `update_definition` {#airbyte.cloud.connectors.CustomCloudSourceDefinition.update_definition}

<ApiMember kind="method">

<ApiSignature>

```python
def update_definition(
    self,
    *,
    manifest_yaml: dict[str, Any] | Path | str | None = None,
    docker_tag: str | None = None,
    pre_validate: bool = True,
) -> airbyte.cloud.connectors.CustomCloudSourceDefinition
```

</ApiSignature>

Update this custom source definition.

You must specify EXACTLY ONE of manifest_yaml (for YAML connectors) OR
docker_tag (for Docker connectors), but not both.

For YAML connectors: updates the manifest
For Docker connectors: Not yet supported (raises NotImplementedError)

**Args:**

- **`manifest_yaml`**: New manifest (YAML connectors only)
- **`docker_tag`**: New Docker tag (Docker connectors only, not yet supported)
- **`pre_validate`**: Whether to validate manifest (YAML only)

**Returns:**

Updated CustomCloudSourceDefinition object

**Raises:**

- **`PyAirbyteInputError`**: If both or neither parameters are provided
- **`NotImplementedError`**: If docker_tag is provided (Docker not yet supported)

</ApiMember>

</ApiMember>