---
id: airbyte-cloud-connectors
title: airbyte.cloud.connectors
---

Module airbyte.cloud.connectors
===============================
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

Classes
-------

`CheckResult(success: bool, error_message: str | None = None, internal_error: str | None = None)`
:   A cloud check result object.

    ### Instance variables

    `error_message: str | None`
    :   None if the check was successful. Otherwise the failure message from the check result.

    `internal_error: str | None`
    :   None if the check was able to be run. Otherwise, this will describe the internal failure.

    `success: bool`
    :   Whether the check result is valid.

`CloudConnector(workspace: CloudWorkspace, connector_id: str)`
:   A cloud connector is a deployed source or destination on Airbyte Cloud.
    
    You can use a connector object to manage the connector.
    
    Initialize a cloud connector object.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * airbyte.cloud.connectors.CloudDestination
    * airbyte.cloud.connectors.CloudSource

    ### Class variables

    `connector_type: ClassVar[Literal['source', 'destination']]`
    :   The type of the connector.

    ### Instance variables

    `connector_id`
    :   The ID of the connector.

    `connector_url: str`
    :   Get the web URL of the source connector.

    `name: str | None`
    :   Get the display name of the connector, if available.
        
        E.g. "My Postgres Source", not the canonical connector name ("source-postgres").

    `workspace`
    :   The workspace that the connector belongs to.

    ### Methods

    `check(self, *, raise_on_error: bool = True) ‑> airbyte.cloud.connectors.CheckResult`
    :   Check the connector.
        
        Returns:
            A `CheckResult` object containing the result. The object is truthy if the check was
            successful and falsy otherwise. The error message is available in the `error_message`
            or by converting the object to a string.

    `permanently_delete(self) ‑> None`
    :   Permanently delete the connector.

`CloudDestination(workspace: CloudWorkspace, connector_id: str)`
:   A cloud destination is a destination that is deployed on Airbyte Cloud.
    
    Initialize a cloud connector object.

    ### Ancestors (in MRO)

    * airbyte.cloud.connectors.CloudConnector
    * abc.ABC

    ### Instance variables

    `destination_id: str`
    :   Get the ID of the destination.
        
        This is an alias for `connector_id`.

    ### Methods

    `rename(self, name: str) ‑> airbyte.cloud.connectors.CloudDestination`
    :   Rename the destination.
        
        Args:
            name: New name for the destination
        
        Returns:
            Updated CloudDestination object with refreshed info

    `update_config(self, config: dict[str, Any]) ‑> airbyte.cloud.connectors.CloudDestination`
    :   Update the destination configuration.
        
        This is a destructive operation that can break existing connections if the
        configuration is changed incorrectly. Use with caution.
        
        Args:
            config: New configuration for the destination
        
        Returns:
            Updated CloudDestination object with refreshed info

`CloudSource(workspace: CloudWorkspace, connector_id: str)`
:   A cloud source is a source that is deployed on Airbyte Cloud.
    
    Initialize a cloud connector object.

    ### Ancestors (in MRO)

    * airbyte.cloud.connectors.CloudConnector
    * abc.ABC

    ### Instance variables

    `source_id: str`
    :   Get the ID of the source.
        
        This is an alias for `connector_id`.

    ### Methods

    `rename(self, name: str) ‑> airbyte.cloud.connectors.CloudSource`
    :   Rename the source.
        
        Args:
            name: New name for the source
        
        Returns:
            Updated CloudSource object with refreshed info

    `update_config(self, config: dict[str, Any]) ‑> airbyte.cloud.connectors.CloudSource`
    :   Update the source configuration.
        
        This is a destructive operation that can break existing connections if the
        configuration is changed incorrectly. Use with caution.
        
        Args:
            config: New configuration for the source
        
        Returns:
            Updated CloudSource object with refreshed info

`CustomCloudSourceDefinition(workspace: CloudWorkspace, definition_id: str, definition_type: "Literal['yaml', 'docker']")`
:   A custom source connector definition in Airbyte Cloud.
    
    This represents either a YAML (declarative) or Docker-based custom source definition.
    
    Initialize a custom source definition object.
    
    Note: Only YAML connectors are currently supported. Docker connectors
    will raise NotImplementedError.

    ### Class variables

    `connector_type: ClassVar[Literal['source', 'destination']]`
    :   The type of the connector: 'source' or 'destination'.

    ### Instance variables

    `connector_builder_project_id: str | None`
    :   Get the connector builder project ID. Only present for YAML connectors.

    `connector_builder_project_url: str | None`
    :   Get the connector builder project URL. Only present for YAML connectors.

    `definition_url: str`
    :   Get the web URL of the custom source definition.
        
        For YAML connectors, this is the connector builder 'edit' URL.
        For Docker connectors, this is the custom connectors page.

    `docker_image_tag: str | None`
    :   Get the Docker image tag. Only present for Docker connectors.
        
        Note: Docker connectors are not yet supported and will raise NotImplementedError.

    `docker_repository: str | None`
    :   Get the Docker repository. Only present for Docker connectors.
        
        Note: Docker connectors are not yet supported and will raise NotImplementedError.

    `documentation_url: str | None`
    :   Get the documentation URL. Only present for Docker connectors.
        
        Note: Docker connectors are not yet supported and will raise NotImplementedError.

    `manifest: dict[str, Any] | None`
    :   Get the Low-code CDK manifest. Only present for YAML connectors.

    `name: str`
    :   Get the display name of the custom connector definition.

    `version: str | None`
    :   Get the manifest version. Only present for YAML connectors.

    ### Methods

    `deploy_source(self, name: str, config: dict[str, Any], *, unique: bool = True, random_name_suffix: bool = False) ‑> airbyte.cloud.connectors.CloudSource`
    :   Deploy a new cloud source using this custom source definition.
        
        Args:
            name: The name for the new source.
            config: A dictionary containing the connection configuration for the new source.
            unique: If True, raises an error if a source with the same name already exists
                in the workspace. Default is True.
            random_name_suffix: If True, appends a random suffix to the name to ensure uniqueness.
                Default is False.
        
        Returns:
            A `CloudSource` object representing the newly created source.

    `permanently_delete(self, *, safe_mode: bool = True) ‑> None`
    :   Permanently delete this custom source definition.
        
        Args:
            safe_mode: If True, requires the connector name to contain "delete-me" or "deleteme"
                (case insensitive) to prevent accidental deletion. Defaults to True.

    `rename(self, new_name: str) ‑> airbyte.cloud.connectors.CustomCloudSourceDefinition`
    :   Rename this custom source definition.
        
        Note: Only Docker custom sources can be renamed. YAML custom sources
        cannot be renamed as their names are derived from the manifest.
        
        Args:
            new_name: New display name for the connector
        
        Returns:
            Updated CustomCloudSourceDefinition object
        
        Raises:
            PyAirbyteInputError: If attempting to rename a YAML connector
            NotImplementedError: If attempting to rename a Docker connector (not yet supported)

    `set_testing_values(self, testing_values: dict[str, Any]) ‑> airbyte.cloud.connectors.CustomCloudSourceDefinition`
    :   Set the testing values for this custom source definition's connector builder project.
        
        Testing values are the input configuration values used when testing the connector
        in the Connector Builder UI. Setting these values allows users to immediately
        run test read operations after deploying a custom source to the Builder UI.
        
        This method replaces any existing testing values with the provided dictionary.
        Pass the full set of values you want to persist, not just the fields you're changing.
        
        Args:
            testing_values: A dictionary containing the configuration values to use for testing.
                This should match the connector's spec schema. Replaces any existing values.
        
        Returns:
            This `CustomCloudSourceDefinition` object (for method chaining).
        
        Raises:
            NotImplementedError: If this is not a YAML custom source definition.
            PyAirbyteInputError: If the connector builder project ID cannot be found.

    `update_definition(self, *, manifest_yaml: dict[str, Any] | Path | str | None = None, docker_tag: str | None = None, pre_validate: bool = True) ‑> airbyte.cloud.connectors.CustomCloudSourceDefinition`
    :   Update this custom source definition.
        
        You must specify EXACTLY ONE of manifest_yaml (for YAML connectors) OR
        docker_tag (for Docker connectors), but not both.
        
        For YAML connectors: updates the manifest
        For Docker connectors: Not yet supported (raises NotImplementedError)
        
        Args:
            manifest_yaml: New manifest (YAML connectors only)
            docker_tag: New Docker tag (Docker connectors only, not yet supported)
            pre_validate: Whether to validate manifest (YAML only)
        
        Returns:
            Updated CustomCloudSourceDefinition object
        
        Raises:
            PyAirbyteInputError: If both or neither parameters are provided
            NotImplementedError: If docker_tag is provided (Docker not yet supported)