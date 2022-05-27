#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import abc
import os
import time
from copy import deepcopy
from pathlib import Path
from typing import Callable, Optional, Set, Union

import airbyte_api_client
import yaml
from airbyte_api_client.api import connection_api, destination_api, source_api
from airbyte_api_client.model.airbyte_catalog import AirbyteCatalog
from airbyte_api_client.model.airbyte_stream import AirbyteStream
from airbyte_api_client.model.airbyte_stream_and_configuration import AirbyteStreamAndConfiguration
from airbyte_api_client.model.airbyte_stream_configuration import AirbyteStreamConfiguration
from airbyte_api_client.model.connection_create import ConnectionCreate
from airbyte_api_client.model.connection_id_request_body import ConnectionIdRequestBody
from airbyte_api_client.model.connection_read import ConnectionRead
from airbyte_api_client.model.connection_schedule import ConnectionSchedule
from airbyte_api_client.model.connection_status import ConnectionStatus
from airbyte_api_client.model.connection_update import ConnectionUpdate
from airbyte_api_client.model.destination_create import DestinationCreate
from airbyte_api_client.model.destination_id_request_body import DestinationIdRequestBody
from airbyte_api_client.model.destination_read import DestinationRead
from airbyte_api_client.model.destination_sync_mode import DestinationSyncMode
from airbyte_api_client.model.destination_update import DestinationUpdate
from airbyte_api_client.model.namespace_definition_type import NamespaceDefinitionType
from airbyte_api_client.model.resource_requirements import ResourceRequirements
from airbyte_api_client.model.source_create import SourceCreate
from airbyte_api_client.model.source_discover_schema_request_body import SourceDiscoverSchemaRequestBody
from airbyte_api_client.model.source_id_request_body import SourceIdRequestBody
from airbyte_api_client.model.source_read import SourceRead
from airbyte_api_client.model.source_update import SourceUpdate
from airbyte_api_client.model.sync_mode import SyncMode
from click import ClickException

from .diff_helpers import compute_diff, hash_config
from .yaml_loaders import EnvVarLoader


class DuplicateResourceError(ClickException):
    pass


class NonExistingResourceError(ClickException):
    pass


class InvalidConfigurationError(ClickException):
    pass


class ResourceState:
    def __init__(self, configuration_path: str, resource_id: str, generation_timestamp: int, configuration_hash: str):
        """This constructor is meant to be private. Construction shall be made with create or from_file class methods.

        Args:
            configuration_path (str): Path to the configuration this state relates to.
            resource_id (str): Id of the resource the state relates to.
            generation_timestamp (int): State generation timestamp.
            configuration_hash (str): Hash of the loaded configuration file.
        """
        self.configuration_path = configuration_path
        self.resource_id = resource_id
        self.generation_timestamp = generation_timestamp
        self.configuration_hash = configuration_hash
        self.path = os.path.join(os.path.dirname(self.configuration_path), "state.yaml")

    def as_dict(self):
        return {
            "resource_id": self.resource_id,
            "generation_timestamp": self.generation_timestamp,
            "configuration_path": self.configuration_path,
            "configuration_hash": self.configuration_hash,
        }

    def _save(self) -> None:
        """Save the state as a YAML file."""
        with open(self.path, "w") as state_file:
            yaml.dump(self.as_dict(), state_file)

    @classmethod
    def create(cls, configuration_path: str, configuration_hash: str, resource_id: str) -> "ResourceState":
        """Create a state for a resource configuration.

        Args:
            configuration_path (str): Path to the YAML file defining the resource.
            configuration_hash (str): Hash of the loaded configuration fie.
            resource_id (str): UUID of the resource.

        Returns:
            ResourceState: state representing the resource.
        """
        generation_timestamp = int(time.time())
        state = ResourceState(configuration_path, resource_id, generation_timestamp, configuration_hash)
        state._save()
        return state

    @classmethod
    def from_file(cls, file_path: str) -> "ResourceState":
        """Deserialize a state from a YAML path.

        Args:
            file_path (str): Path to the YAML state.

        Returns:
            ResourceState: state deserialized from YAML.
        """
        with open(file_path, "r") as f:
            raw_state = yaml.safe_load(f)
        return ResourceState(
            raw_state["configuration_path"],
            raw_state["resource_id"],
            raw_state["generation_timestamp"],
            raw_state["configuration_hash"],
        )


class BaseResource(abc.ABC):
    APPLY_PRIORITY = 0  # Priority of the resource during the apply. 0 means the resource is top priority.

    @property
    @abc.abstractmethod
    def api(
        self,
    ):  # pragma: no cover
        pass

    @property
    @abc.abstractmethod
    def create_function_name(
        self,
    ):  # pragma: no cover
        pass

    @property
    @abc.abstractmethod
    def create_payload(
        self,
    ):  # pragma: no cover
        pass

    @property
    @abc.abstractmethod
    def update_payload(
        self,
    ):  # pragma: no cover
        pass

    @property
    @abc.abstractmethod
    def update_function_name(
        self,
    ):  # pragma: no cover
        pass

    @property
    @abc.abstractmethod
    def get_function_name(
        self,
    ):  # pragma: no cover
        pass

    @property
    @abc.abstractmethod
    def get_payload(
        self,
    ):  # pragma: no cover
        pass

    @property
    @abc.abstractmethod
    def resource_id_field(
        self,
    ):  # pragma: no cover
        pass

    @property
    @abc.abstractmethod
    def ResourceIdRequestBody(
        self,
    ):  # pragma: no cover
        pass

    @property
    @abc.abstractmethod
    def resource_type(
        self,
    ):  # pragma: no cover
        pass

    def __init__(
        self, api_client: airbyte_api_client.ApiClient, workspace_id: str, raw_configuration: dict, configuration_path: str
    ) -> None:
        """Create a BaseResource object.

        Args:
            api_client (airbyte_api_client.ApiClient): the Airbyte API client.
            workspace_id (str): the workspace id.
            raw_configuration (dict): The local configuration describing the resource.
            configuration_path (str): The path to the local configuration describing the resource with YAML.
        """
        self._create_fn = getattr(self.api, self.create_function_name)
        self._update_fn = getattr(self.api, self.update_function_name)
        self._get_fn = getattr(self.api, self.get_function_name)

        self.configuration_path = configuration_path
        self.state = self._get_state_from_file(configuration_path)
        self.configuration_hash = hash_config(
            raw_configuration
        )  # Hash as early as possible to limit risks of raw_configuration downstream mutations.

        self.local_file_changed = True if self.state is None else self.configuration_hash != self.state.configuration_hash

        self.raw_configuration = raw_configuration
        self.configuration = self._deserialize_raw_configuration()
        self.api_instance = self.api(api_client)
        self.workspace_id = workspace_id
        self.resource_name = raw_configuration["resource_name"]

    def _deserialize_raw_configuration(self):
        """Deserialize a raw configuration into another object and perform extra validation if needed.
        The base implementation does nothing except extracting the configuration field and returning a copy of it.

        Returns:
            dict: Deserialized configuration
        """
        return deepcopy(self.raw_configuration["configuration"])

    @staticmethod
    def _check_for_invalid_configuration_keys(dict_to_check: dict, invalid_keys: Set[str], error_message: str):
        """Utils function to check if a configuration dictionnary has legacy keys that were removed/renamed after an octavia update.

        Args:
            dict_to_check (dict): The dictionnary for which keys should be checked
            invalid_keys (Set[str]): The set of invalid keys we want to check the existence
            error_message (str): The error message to display to the user

        Raises:
            InvalidConfigurationError: Raised if an invalid key was found in the dict_to_check
        """
        invalid_keys = list(set(dict_to_check.keys()) & invalid_keys)
        if invalid_keys:
            raise InvalidConfigurationError(f"{error_message}: {', '.join(invalid_keys)}")

    @property
    def remote_resource(self):
        return self._get_remote_resource() if self.state else None

    def _get_local_comparable_configuration(self) -> dict:
        return self.raw_configuration["configuration"]

    @abc.abstractmethod
    def _get_remote_comparable_configuration(
        self,
    ) -> dict:  # pragma: no cover
        raise NotImplementedError

    @property
    def was_created(self):
        return True if self.remote_resource else False

    def _get_remote_resource(self) -> Union[SourceRead, DestinationRead, ConnectionRead]:
        """Retrieve a resources on the remote Airbyte instance.

        Returns:
            Union[SourceReadList, DestinationReadList, ConnectionReadList]: Search results
        """
        return self._get_fn(self.api_instance, self.get_payload)

    @staticmethod
    def _get_state_from_file(configuration_file: str) -> Optional[ResourceState]:
        """Retrieve a state object from a local YAML file if it exists.

        Returns:
            Optional[ResourceState]: the deserialized resource state if YAML file found.
        """
        expected_state_path = Path(os.path.join(os.path.dirname(configuration_file), "state.yaml"))
        if expected_state_path.is_file():
            return ResourceState.from_file(expected_state_path)

    def get_diff_with_remote_resource(self) -> str:
        """Compute the diff between current resource and the remote resource.

        Raises:
            NonExistingResourceError: Raised if the remote resource does not exist.

        Returns:
            str: The prettyfied diff.
        """
        if not self.was_created:
            raise NonExistingResourceError("Cannot compute diff with a non existing remote resource.")
        local_config = self._get_local_comparable_configuration()
        remote_config = self._get_remote_comparable_configuration()
        diff = compute_diff(remote_config, local_config)
        return diff.pretty()

    def _create_or_update(
        self,
        operation_fn: Callable,
        payload: Union[SourceCreate, SourceUpdate, DestinationCreate, DestinationUpdate, ConnectionCreate, ConnectionUpdate],
    ) -> Union[SourceRead, DestinationRead]:
        """Wrapper to trigger create or update of remote resource.

                Args:
                    operation_fn (Callable): The API function to run.
                    payload (Union[SourceCreate, SourceUpdate, DestinationCreate, DestinationUpdate]): The payload to send to create or update the resource.
        .
                Raises:
                    InvalidConfigurationError: Raised if the create or update payload is invalid.
                    ApiException: Raised in case of other API errors.

                Returns:
                    Union[SourceRead, DestinationRead, ConnectionRead]: The created or updated resource.
        """
        try:
            result = operation_fn(self.api_instance, payload)
            return result, ResourceState.create(self.configuration_path, self.configuration_hash, result[self.resource_id_field])
        except airbyte_api_client.ApiException as api_error:
            if api_error.status == 422:
                # This  API response error is really verbose, but it embodies all the details about why the config is not valid.
                # TODO alafanechere: try to parse it and display it in a more readable way.
                raise InvalidConfigurationError(api_error.body)
            else:
                raise api_error

    def create(self) -> Union[SourceRead, DestinationRead, ConnectionRead]:
        """Public function to create the resource on the remote Airbyte instance.

        Returns:
            Union[SourceRead, DestinationRead, ConnectionRead]: The created resource.
        """
        return self._create_or_update(self._create_fn, self.create_payload)

    def update(self) -> Union[SourceRead, DestinationRead, ConnectionRead]:
        """Public function to update the resource on the remote Airbyte instance.

        Returns:
            Union[SourceRead, DestinationRead, ConnectionRead]: The updated resource.
        """
        return self._create_or_update(self._update_fn, self.update_payload)

    @property
    def resource_id(self) -> Optional[str]:
        """Exposes the resource UUID of the remote resource

        Returns:
            str: Remote resource's UUID
        """
        return self.state.resource_id if self.state is not None else None

    @property
    def resource_id_request_body(self) -> Union[SourceIdRequestBody, DestinationIdRequestBody]:
        """Creates SourceIdRequestBody or DestinationIdRequestBody from resource id.

        Raises:
            NonExistingResourceError: raised if the resource id is None.

        Returns:
            Union[SourceIdRequestBody, DestinationIdRequestBody]: The model instance.
        """
        if self.resource_id is None:
            raise NonExistingResourceError("The resource id could not be retrieved, the remote resource is not existing.")
        return self.ResourceIdRequestBody(self.resource_id)


class SourceAndDestination(BaseResource):
    @property
    def definition_id(self):
        return self.raw_configuration["definition_id"]

    @property
    def definition_image(self):
        return self.raw_configuration["definition_image"]

    @property
    def definition_version(self):
        return self.raw_configuration["definition_version"]

    def _get_remote_comparable_configuration(self) -> dict:
        return self.remote_resource.connection_configuration


class Source(SourceAndDestination):

    api = source_api.SourceApi
    create_function_name = "create_source"
    resource_id_field = "source_id"
    ResourceIdRequestBody = SourceIdRequestBody
    get_function_name = "get_source"
    update_function_name = "update_source"
    resource_type = "source"

    @property
    def create_payload(self):
        return SourceCreate(self.definition_id, self.configuration, self.workspace_id, self.resource_name)

    @property
    def get_payload(self) -> Optional[SourceIdRequestBody]:
        """Defines the payload to retrieve the remote source if a state exists.
        Returns:
            SourceIdRequestBody: The SourceIdRequestBody payload.
        """
        if self.state is not None:
            return SourceIdRequestBody(self.state.resource_id)

    @property
    def update_payload(self):
        return SourceUpdate(
            source_id=self.resource_id,
            connection_configuration=self.configuration,
            name=self.resource_name,
        )

    @property
    def source_discover_schema_request_body(self) -> SourceDiscoverSchemaRequestBody:
        """Creates SourceDiscoverSchemaRequestBody from resource id.

        Raises:
            NonExistingResourceError: raised if the resource id is None.

        Returns:
            SourceDiscoverSchemaRequestBody: The SourceDiscoverSchemaRequestBody model instance.
        """
        if self.resource_id is None:
            raise NonExistingResourceError("The resource id could not be retrieved, the remote resource is not existing.")
        return SourceDiscoverSchemaRequestBody(self.resource_id)

    @property
    def catalog(self) -> AirbyteCatalog:
        """Retrieves the source's Airbyte catalog.

        Returns:
            AirbyteCatalog: The catalog issued by schema discovery.
        """
        schema = self.api_instance.discover_schema_for_source(self.source_discover_schema_request_body)
        return schema.catalog


class Destination(SourceAndDestination):
    api = destination_api.DestinationApi
    create_function_name = "create_destination"
    resource_id_field = "destination_id"
    ResourceIdRequestBody = DestinationIdRequestBody
    get_function_name = "get_destination"
    update_function_name = "update_destination"
    resource_type = "destination"

    @property
    def create_payload(self) -> DestinationCreate:
        """Defines the payload to create the remote resource.

        Returns:
            DestinationCreate: The DestinationCreate model instance
        """
        return DestinationCreate(self.workspace_id, self.resource_name, self.definition_id, self.configuration)

    @property
    def get_payload(self) -> Optional[DestinationRead]:
        """Defines the payload to retrieve the remote destination if a state exists.
        Returns:
            DestinationRead: The DestinationRead model instance
        """
        if self.state is not None:
            return DestinationIdRequestBody(self.state.resource_id)

    @property
    def update_payload(self) -> DestinationUpdate:
        """Defines the payload to update a remote resource.

        Returns:
            DestinationUpdate: The DestinationUpdate model instance.
        """
        return DestinationUpdate(
            destination_id=self.resource_id,
            connection_configuration=self.configuration,
            name=self.resource_name,
        )


class Connection(BaseResource):
    APPLY_PRIORITY = 1  # Set to 1 to create connection after source or destination.
    api = connection_api.ConnectionApi
    create_function_name = "create_connection"
    resource_id_field = "connection_id"
    ResourceIdRequestBody = ConnectionIdRequestBody
    get_function_name = "get_connection"
    update_function_name = "update_connection"
    resource_type = "connection"

    def _deserialize_raw_configuration(self):
        """Deserialize a raw configuration into another dict and perform serialization if needed.
        In this implementation we cast raw types to Airbyte API client models types for validation.
        Args:
            raw_configuration (dict): The raw configuration

        Returns:
            dict: Deserialized connection configuration
        """
        configuration = super()._deserialize_raw_configuration()
        self._check_for_legacy_connection_configuration_keys(configuration)
        configuration["sync_catalog"] = self._create_configured_catalog(configuration["sync_catalog"])
        configuration["namespace_definition"] = NamespaceDefinitionType(configuration["namespace_definition"])
        if "schedule" in configuration:
            configuration["schedule"] = ConnectionSchedule(**configuration["schedule"])
        configuration["resource_requirements"] = ResourceRequirements(**configuration["resource_requirements"])
        configuration["status"] = ConnectionStatus(configuration["status"])
        return configuration

    @property
    def source_id(self):
        return self.raw_configuration["source_id"]

    @property
    def destination_id(self):
        return self.raw_configuration["destination_id"]

    @property
    def create_payload(self) -> ConnectionCreate:
        """Defines the payload to create the remote connection.

        Returns:
            ConnectionCreate: The ConnectionCreate model instance
        """
        return ConnectionCreate(name=self.resource_name, source_id=self.source_id, destination_id=self.destination_id, **self.configuration)

    @property
    def get_payload(self) -> Optional[ConnectionIdRequestBody]:
        """Defines the payload to retrieve the remote connection if a state exists.
        Returns:
            ConnectionIdRequestBody: The ConnectionIdRequestBody payload.
        """
        if self.state is not None:
            return ConnectionIdRequestBody(self.state.resource_id)

    @property
    def update_payload(self) -> ConnectionUpdate:
        """Defines the payload to update a remote connection.

        Returns:
            ConnectionUpdate: The DestinationUpdate model instance.
        """
        return ConnectionUpdate(connection_id=self.resource_id, **self.configuration)

    def create(self) -> dict:
        return self._create_or_update(self._create_fn, self.create_payload)

    def update(self) -> dict:
        return self._create_or_update(self._update_fn, self.update_payload)

    @staticmethod
    def _create_configured_catalog(sync_catalog: dict) -> AirbyteCatalog:
        """Deserialize a sync_catalog represented as dict to an AirbyteCatalog.

        Args:
            sync_catalog (dict): The sync catalog represented as a dict.

        Returns:
            AirbyteCatalog: The configured catalog.
        """
        streams_and_configurations = []
        for stream in sync_catalog["streams"]:
            stream["stream"]["supported_sync_modes"] = [SyncMode(sm) for sm in stream["stream"]["supported_sync_modes"]]
            stream["config"]["sync_mode"] = SyncMode(stream["config"]["sync_mode"])
            stream["config"]["destination_sync_mode"] = DestinationSyncMode(stream["config"]["destination_sync_mode"])

            streams_and_configurations.append(
                AirbyteStreamAndConfiguration(
                    stream=AirbyteStream(**stream["stream"]), config=AirbyteStreamConfiguration(**stream["config"])
                )
            )
        return AirbyteCatalog(streams_and_configurations)

    # TODO this check can be removed when all our active user are on >= 0.36.11
    def _check_for_legacy_connection_configuration_keys(self, configuration_to_check):
        """We changed connection configuration keys from camelCase to snake_case in 0.36.11.
        This function check if the connection configuration has some camelCase keys and display a meaningful error message.

        Args:
            configuration_to_check (dict): Configuration to validate
        """
        error_message = (
            "The following keys should be in snake_case since version 0.36.10, please edit or regenerate your connection configuration"
        )
        self._check_for_invalid_configuration_keys(
            configuration_to_check, {"syncCatalog", "namespaceDefinition", "namespaceFormat", "resourceRequirements"}, error_message
        )
        self._check_for_invalid_configuration_keys(configuration_to_check.get("schedule", {}), {"timeUnit"}, error_message)
        for stream in configuration_to_check["sync_catalog"]["streams"]:
            self._check_for_invalid_configuration_keys(
                stream["stream"],
                {"defaultCursorField", "jsonSchema", "sourceDefinedCursor", "sourceDefinedPrimaryKey", "supportedSyncModes"},
                error_message,
            )
            self._check_for_invalid_configuration_keys(
                stream["config"], {"aliasName", "cursorField", "destinationSyncMode", "primaryKey", "syncMode"}, error_message
            )

    def _get_remote_comparable_configuration(self) -> dict:
        keys_to_filter_out = [
            "name",
            "source_id",
            "destination_id",
            "connection_id",
            "operation_ids",
            "source_catalog_id",
        ]  # We do not allow local editing of these keys
        return {k: v for k, v in self.remote_resource.to_dict().items() if k not in keys_to_filter_out}


def factory(api_client: airbyte_api_client.ApiClient, workspace_id: str, configuration_path: str) -> Union[Source, Destination, Connection]:
    """Create resource object according to the definition type field in their YAML configuration.

    Args:
        api_client (airbyte_api_client.ApiClient): The Airbyte API client.
        workspace_id (str): The current workspace id.
        configuration_path (str): Path to the YAML file with the configuration.

    Raises:
        NotImplementedError: Raised if the definition type found in the YAML is not a supported resource.

    Returns:
        Union[Source, Destination, Connection]: The resource object created from the YAML config.
    """
    with open(configuration_path, "r") as f:
        raw_configuration = yaml.load(f, EnvVarLoader)
    if raw_configuration["definition_type"] == "source":
        return Source(api_client, workspace_id, raw_configuration, configuration_path)
    if raw_configuration["definition_type"] == "destination":
        return Destination(api_client, workspace_id, raw_configuration, configuration_path)
    if raw_configuration["definition_type"] == "connection":
        return Connection(api_client, workspace_id, raw_configuration, configuration_path)
    else:
        raise NotImplementedError(f"Resource {raw_configuration['definition_type']} was not yet implemented")
