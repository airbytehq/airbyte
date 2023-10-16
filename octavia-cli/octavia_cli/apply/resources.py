#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import abc
import os
import time
from copy import deepcopy
from pathlib import Path
from typing import Callable, List, Optional, Set, Tuple, Type, Union

import airbyte_api_client
import click
import yaml
from airbyte_api_client.api import (
    destination_api,
    destination_definition_api,
    destination_definition_specification_api,
    source_api,
    source_definition_api,
    source_definition_specification_api,
    web_backend_api,
)
from airbyte_api_client.model.airbyte_catalog import AirbyteCatalog
from airbyte_api_client.model.airbyte_stream import AirbyteStream
from airbyte_api_client.model.airbyte_stream_and_configuration import AirbyteStreamAndConfiguration
from airbyte_api_client.model.airbyte_stream_configuration import AirbyteStreamConfiguration
from airbyte_api_client.model.connection_read import ConnectionRead
from airbyte_api_client.model.connection_schedule_data import ConnectionScheduleData
from airbyte_api_client.model.connection_schedule_data_basic_schedule import ConnectionScheduleDataBasicSchedule
from airbyte_api_client.model.connection_schedule_data_cron import ConnectionScheduleDataCron
from airbyte_api_client.model.connection_schedule_type import ConnectionScheduleType
from airbyte_api_client.model.connection_status import ConnectionStatus
from airbyte_api_client.model.destination_create import DestinationCreate
from airbyte_api_client.model.destination_definition_id_request_body import DestinationDefinitionIdRequestBody
from airbyte_api_client.model.destination_definition_id_with_workspace_id import DestinationDefinitionIdWithWorkspaceId
from airbyte_api_client.model.destination_definition_read import DestinationDefinitionRead
from airbyte_api_client.model.destination_definition_specification_read import DestinationDefinitionSpecificationRead
from airbyte_api_client.model.destination_id_request_body import DestinationIdRequestBody
from airbyte_api_client.model.destination_read import DestinationRead
from airbyte_api_client.model.destination_sync_mode import DestinationSyncMode
from airbyte_api_client.model.destination_update import DestinationUpdate
from airbyte_api_client.model.geography import Geography
from airbyte_api_client.model.namespace_definition_type import NamespaceDefinitionType
from airbyte_api_client.model.non_breaking_changes_preference import NonBreakingChangesPreference
from airbyte_api_client.model.operation_create import OperationCreate
from airbyte_api_client.model.operator_configuration import OperatorConfiguration
from airbyte_api_client.model.operator_dbt import OperatorDbt
from airbyte_api_client.model.operator_normalization import OperatorNormalization
from airbyte_api_client.model.operator_type import OperatorType
from airbyte_api_client.model.resource_requirements import ResourceRequirements
from airbyte_api_client.model.selected_field_info import SelectedFieldInfo
from airbyte_api_client.model.source_create import SourceCreate
from airbyte_api_client.model.source_definition_id_request_body import SourceDefinitionIdRequestBody
from airbyte_api_client.model.source_definition_id_with_workspace_id import SourceDefinitionIdWithWorkspaceId
from airbyte_api_client.model.source_definition_read import SourceDefinitionRead
from airbyte_api_client.model.source_definition_specification_read import SourceDefinitionSpecificationRead
from airbyte_api_client.model.source_discover_schema_request_body import SourceDiscoverSchemaRequestBody
from airbyte_api_client.model.source_id_request_body import SourceIdRequestBody
from airbyte_api_client.model.source_read import SourceRead
from airbyte_api_client.model.source_update import SourceUpdate
from airbyte_api_client.model.sync_mode import SyncMode
from airbyte_api_client.model.web_backend_connection_create import WebBackendConnectionCreate
from airbyte_api_client.model.web_backend_connection_request_body import WebBackendConnectionRequestBody
from airbyte_api_client.model.web_backend_connection_update import WebBackendConnectionUpdate
from airbyte_api_client.model.web_backend_operation_create_or_update import WebBackendOperationCreateOrUpdate

from .diff_helpers import compute_diff, hash_config
from .yaml_loaders import EnvVarLoader


class NonExistingResourceError(click.ClickException):
    pass


class InvalidConfigurationError(click.ClickException):
    pass


class InvalidStateError(click.ClickException):
    pass


class MissingStateError(click.ClickException):
    pass


class ResourceState:
    def __init__(
        self,
        configuration_path: Union[str, Path],
        workspace_id: Optional[str],
        resource_id: str,
        generation_timestamp: int,
        configuration_hash: str,
    ):
        """This constructor is meant to be private. Construction shall be made with create or from_file class methods.
        Args:
            configuration_path (str): Path to the configuration this state relates to.
            workspace_id Optional(str): Id of the workspace the state relates to. #TODO mark this a not optional after the user base has upgraded to >= 0.39.18
            resource_id (str): Id of the resource the state relates to.
            generation_timestamp (int): State generation timestamp.
            configuration_hash (str): Hash of the loaded configuration file.
        """
        self.configuration_path = str(configuration_path)
        self.resource_id = resource_id
        self.generation_timestamp = generation_timestamp
        self.configuration_hash = configuration_hash
        self.workspace_id = workspace_id
        self.path = self._get_path_from_configuration_and_workspace_id(configuration_path, workspace_id)

    def as_dict(self):
        return {
            "resource_id": self.resource_id,
            "workspace_id": self.workspace_id,
            "generation_timestamp": self.generation_timestamp,
            "configuration_path": self.configuration_path,
            "configuration_hash": self.configuration_hash,
        }

    def _save(self) -> None:
        """Save the state as a YAML file."""
        with open(self.path, "w") as state_file:
            yaml.dump(self.as_dict(), state_file)

    @classmethod
    def create(cls, configuration_path: str, configuration_hash: str, workspace_id: str, resource_id: str) -> "ResourceState":
        """Create a state for a resource configuration.
        Args:
            configuration_path (str): Path to the YAML file defining the resource.
            configuration_hash (str): Hash of the loaded configuration fie.
            resource_id (str): UUID of the resource.
        Returns:
            ResourceState: state representing the resource.
        """
        generation_timestamp = int(time.time())
        state = ResourceState(configuration_path, workspace_id, resource_id, generation_timestamp, configuration_hash)
        state._save()
        return state

    def delete(self) -> None:
        """Delete the state file"""
        os.remove(self.path)

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
            # TODO: workspace id should not be nullable after the user base has upgraded to >= 0.39.18
            raw_state.get("workspace_id"),
            raw_state["resource_id"],
            raw_state["generation_timestamp"],
            raw_state["configuration_hash"],
        )

    @classmethod
    def _get_path_from_configuration_and_workspace_id(cls, configuration_path, workspace_id):
        return os.path.join(os.path.dirname(configuration_path), f"state_{workspace_id}.yaml")

    @classmethod
    def from_configuration_path_and_workspace(cls, configuration_path, workspace_id):
        state_path = cls._get_path_from_configuration_and_workspace_id(configuration_path, workspace_id)
        state = cls.from_file(state_path)
        return state

    @classmethod
    def migrate(self, state_to_migrate_path: str, workspace_id: str) -> "ResourceState":
        """Create a per workspace state from a legacy state file and remove the legacy state file.
        Args:
            state_to_migrate_path (str): Path to the legacy state file to migrate.
            workspace_id (str): Workspace id for which the new state will be stored.
        Returns:
            ResourceState: The new state after migration.
        """
        state_to_migrate = ResourceState.from_file(state_to_migrate_path)
        new_state = ResourceState.create(
            state_to_migrate.configuration_path, state_to_migrate.configuration_hash, workspace_id, state_to_migrate.resource_id
        )
        state_to_migrate.delete()
        return new_state


class BaseResource(abc.ABC):
    # Priority of the resource during the apply. 0 means the resource is top priority.
    APPLY_PRIORITY = 0

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

        self.workspace_id = workspace_id
        self.configuration_path = configuration_path
        self.state = self._get_state_from_file(configuration_path, workspace_id)
        self.configuration_hash = hash_config(
            raw_configuration
        )  # Hash as early as possible to limit risks of raw_configuration downstream mutations.

        self.local_file_changed = True if self.state is None else self.configuration_hash != self.state.configuration_hash

        self.raw_configuration = raw_configuration
        self.configuration = self._deserialize_raw_configuration()
        self.api_client = api_client
        self.api_instance = self.api(api_client)
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
            raise InvalidConfigurationError(f"Invalid configuration keys: {', '.join(invalid_keys)}. {error_message}. ")

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
    def _get_state_from_file(configuration_file: str, workspace_id: str) -> Optional[ResourceState]:
        """Retrieve a state object from a local YAML file if it exists.
        Returns:
            Optional[ResourceState]: the deserialized resource state if YAML file found.
        """
        expected_state_path = Path(os.path.join(os.path.dirname(configuration_file), f"state_{workspace_id}.yaml"))
        legacy_state_path = Path(os.path.join(os.path.dirname(configuration_file), "state.yaml"))
        if expected_state_path.is_file():
            return ResourceState.from_file(expected_state_path)
        elif legacy_state_path.is_file():  # TODO: remove condition after user base has upgraded to >= 0.39.18
            if click.confirm(
                click.style(
                    f"⚠️  - State files are now saved on a workspace basis. Do you want octavia to rename and update {legacy_state_path}? ",
                    fg="red",
                )
            ):
                return ResourceState.migrate(legacy_state_path, workspace_id)
            else:
                raise InvalidStateError(
                    f"Octavia expects the state file to be located at {expected_state_path} with a workspace_id key. Please update {legacy_state_path}."
                )
        else:
            return None

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
        payload: Union[
            SourceCreate, SourceUpdate, DestinationCreate, DestinationUpdate, WebBackendConnectionCreate, WebBackendConnectionUpdate
        ],
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
            new_state = ResourceState.create(
                self.configuration_path, self.configuration_hash, self.workspace_id, result[self.resource_id_field]
            )
            return result, new_state
        except airbyte_api_client.ApiException as api_error:
            if api_error.status == 422:
                # This  API response error is really verbose, but it embodies all the details about why the config is not valid.
                # TODO alafanechere: try to parse it and display it in a more readable way.
                raise InvalidConfigurationError(api_error.body)
            else:
                raise api_error

    def manage(
        self, resource_id: str
    ) -> Union[Tuple[SourceRead, ResourceState], Tuple[DestinationRead, ResourceState], Tuple[ConnectionRead, ResourceState]]:
        """Declare a remote resource as locally managed by creating a local state

        Args:
            resource_id (str): Remote resource ID.

        Returns:
            Union[Tuple[SourceRead, ResourceState], Tuple[DestinationRead, ResourceState], Tuple[ConnectionRead, ResourceState]]: The remote resource model instance and its local state.
        """
        self.state = ResourceState.create(self.configuration_path, self.configuration_hash, self.workspace_id, resource_id)

        return self.remote_resource, self.state

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


class SourceAndDestination(BaseResource):
    @property
    @abc.abstractmethod
    def definition(
        self,
    ):  # pragma: no cover
        pass

    @property
    @abc.abstractmethod
    def definition_specification(
        self,
    ):  # pragma: no cover
        pass

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
        if schema.job_info.succeeded:
            return schema.catalog
        raise Exception("Could not discover schema for source", self.source_discover_schema_request_body, schema.job_info.logs)

    @property
    def definition(self) -> SourceDefinitionRead:
        api_instance = source_definition_api.SourceDefinitionApi(self.api_client)
        payload = SourceDefinitionIdRequestBody(source_definition_id=self.definition_id)
        return api_instance.get_source_definition(payload)

    @property
    def definition_specification(self) -> SourceDefinitionSpecificationRead:
        api_instance = source_definition_specification_api.SourceDefinitionSpecificationApi(self.api_client)
        payload = SourceDefinitionIdWithWorkspaceId(source_definition_id=self.definition_id, workspace_id=self.workspace_id)
        return api_instance.get_source_definition_specification(payload)


class Destination(SourceAndDestination):
    api = destination_api.DestinationApi
    create_function_name = "create_destination"
    resource_id_field = "destination_id"
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

    @property
    def definition(self) -> DestinationDefinitionRead:
        api_instance = destination_definition_api.DestinationDefinitionApi(self.api_client)
        payload = DestinationDefinitionIdRequestBody(destination_definition_id=self.definition_id)
        return api_instance.get_destination_definition(payload)

    @property
    def definition_specification(self) -> DestinationDefinitionSpecificationRead:
        api_instance = destination_definition_specification_api.DestinationDefinitionSpecificationApi(self.api_client)
        payload = DestinationDefinitionIdWithWorkspaceId(destination_definition_id=self.definition_id, workspace_id=self.workspace_id)
        return api_instance.get_destination_definition_specification(payload)


class Connection(BaseResource):
    # Set to 1 to create connection after source or destination.
    APPLY_PRIORITY = 1
    api = web_backend_api.WebBackendApi
    create_function_name = "web_backend_create_connection"
    update_function_name = "web_backend_update_connection"
    get_function_name = "web_backend_get_connection"
    resource_id_field = "connection_id"

    resource_type = "connection"

    local_root_level_keys_to_remove_during_create = ["skip_reset"]  # Remove these keys when sending a create request

    local_root_level_keys_to_filter_out_for_comparison = ["skip_reset"]  # Remote do not have these keys

    remote_root_level_keys_to_filter_out_for_comparison = [
        "name",
        "source",
        "destination",
        "source_id",
        "destination_id",
        "connection_id",
        "operation_ids",
        "source_catalog_id",
        "catalog_id",
        "is_syncing",
        "latest_sync_job_status",
        "latest_sync_job_created_at",
        "schedule",
    ]  # We do not allow local editing of these keys

    # We do not allow local editing of these keys
    remote_operation_level_keys_to_filter_out = ["workspace_id", "operation_id"]

    def _deserialize_raw_configuration(self):
        """Deserialize a raw configuration into another dict and perform serialization if needed.
        In this implementation we cast raw types to Airbyte API client models types for validation.
        Args:
            raw_configuration (dict): The raw configuration
        Returns:
            dict: Deserialized connection configuration
        """
        self._check_for_legacy_raw_configuration_keys(self.raw_configuration)
        configuration = super()._deserialize_raw_configuration()
        self._check_for_legacy_connection_configuration_keys(configuration)
        configuration["sync_catalog"] = self._create_configured_catalog(configuration["sync_catalog"])
        configuration["namespace_definition"] = NamespaceDefinitionType(configuration["namespace_definition"])
        if "non_breaking_changes_preference" in configuration:
            configuration["non_breaking_changes_preference"] = NonBreakingChangesPreference(
                configuration["non_breaking_changes_preference"]
            )
        else:
            configuration["non_breaking_changes_preference"] = NonBreakingChangesPreference("ignore")
        if "geography" in configuration:
            configuration["geography"] = Geography(configuration["geography"])
        else:
            configuration["geography"] = Geography("auto")

        if "schedule_type" in configuration:
            # If schedule type is manual we do not expect a schedule_data field to be set
            # TODO: sending a WebConnectionCreate payload without schedule_data (for manual) fails.
            is_manual = configuration["schedule_type"] == "manual"
            configuration["schedule_type"] = ConnectionScheduleType(configuration["schedule_type"])
            if not is_manual:
                if "basic_schedule" in configuration["schedule_data"]:
                    basic_schedule = ConnectionScheduleDataBasicSchedule(**configuration["schedule_data"]["basic_schedule"])
                    configuration["schedule_data"]["basic_schedule"] = basic_schedule
                if "cron" in configuration["schedule_data"]:
                    cron = ConnectionScheduleDataCron(**configuration["schedule_data"]["cron"])
                    configuration["schedule_data"]["cron"] = cron
                configuration["schedule_data"] = ConnectionScheduleData(**configuration["schedule_data"])
        if "resource_requirements" in configuration:
            configuration["resource_requirements"] = ResourceRequirements(**configuration["resource_requirements"])
        configuration["status"] = ConnectionStatus(configuration["status"])
        return configuration

    @property
    def source_id(self):
        """Retrieve the source id from the source state file of the current workspace.
        Raises:
            MissingStateError: Raised if the state file of the current workspace is not found.
        Returns:
            str: source id
        """
        try:
            source_state = ResourceState.from_configuration_path_and_workspace(
                self.raw_configuration["source_configuration_path"], self.workspace_id
            )
        except FileNotFoundError:
            raise MissingStateError(
                f"Could not find the source state file for configuration {self.raw_configuration['source_configuration_path']}."
            )
        return source_state.resource_id

    @property
    def destination_id(self):
        """Retrieve the destination id from the destination state file of the current workspace.
        Raises:
            MissingStateError: Raised if the state file of the current workspace is not found.
        Returns:
            str: destination id
        """
        try:
            destination_state = ResourceState.from_configuration_path_and_workspace(
                self.raw_configuration["destination_configuration_path"], self.workspace_id
            )
        except FileNotFoundError:
            raise MissingStateError(
                f"Could not find the destination state file for configuration {self.raw_configuration['destination_configuration_path']}."
            )
        return destination_state.resource_id

    @property
    def create_payload(self) -> WebBackendConnectionCreate:
        """Defines the payload to create the remote connection.
        Returns:
            WebBackendConnectionCreate: The WebBackendConnectionCreate model instance
        """

        if self.raw_configuration["configuration"].get("operations") is not None:
            self.configuration["operations"] = self._deserialize_operations(
                self.raw_configuration["configuration"]["operations"], OperationCreate
            )
        for k in self.local_root_level_keys_to_remove_during_create:
            self.configuration.pop(k, None)
        return WebBackendConnectionCreate(
            name=self.resource_name, source_id=self.source_id, destination_id=self.destination_id, **self.configuration
        )

    @property
    def get_payload(self) -> Optional[WebBackendConnectionRequestBody]:
        """Defines the payload to retrieve the remote connection if a state exists.
        Returns:
            ConnectionIdRequestBody: The ConnectionIdRequestBody payload.
        """
        if self.state is not None:
            return WebBackendConnectionRequestBody(connection_id=self.state.resource_id, with_refreshed_catalog=False)

    @property
    def update_payload(self) -> WebBackendConnectionUpdate:
        """Defines the payload to update a remote connection.
        Returns:
            WebBackendConnectionUpdate: The DestinationUpdate model instance.
        """
        if self.raw_configuration["configuration"].get("operations") is not None:
            self.configuration["operations"] = self._deserialize_operations(
                self.raw_configuration["configuration"]["operations"], WebBackendOperationCreateOrUpdate
            )
        return WebBackendConnectionUpdate(connection_id=self.resource_id, **self.configuration)

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
            if "selected_fields" in stream["config"]:
                stream["config"]["selected_fields"] = [
                    SelectedFieldInfo(field_path=selected_field["field_path"]) for selected_field in stream["config"]["selected_fields"]
                ]
            streams_and_configurations.append(
                AirbyteStreamAndConfiguration(
                    stream=AirbyteStream(**stream["stream"]), config=AirbyteStreamConfiguration(**stream["config"])
                )
            )
        return AirbyteCatalog(streams_and_configurations)

    def _deserialize_operations(
        self, operations: List[dict], outputModelClass: Union[Type[OperationCreate], Type[WebBackendOperationCreateOrUpdate]]
    ) -> List[Union[OperationCreate, WebBackendOperationCreateOrUpdate]]:
        """Deserialize operations to OperationCreate (to create connection) or WebBackendOperationCreateOrUpdate (to update connection) models.
        Args:
            operations (List[dict]): List of operations to deserialize
            outputModelClass (Union[Type[OperationCreate], Type[WebBackendOperationCreateOrUpdate]]): The model to which the operation dict will be deserialized
        Raises:
            ValueError: Raised if the operator type declared in the configuration is not supported
        Returns:
            List[Union[OperationCreate, WebBackendOperationCreateOrUpdate]]: Deserialized operations
        """
        deserialized_operations = []
        for operation in operations:
            if operation["operator_configuration"]["operator_type"] == "normalization":
                operation = outputModelClass(
                    workspace_id=self.workspace_id,
                    name=operation["name"],
                    operator_configuration=OperatorConfiguration(
                        operator_type=OperatorType(operation["operator_configuration"]["operator_type"]),
                        normalization=OperatorNormalization(**operation["operator_configuration"]["normalization"]),
                    ),
                )
            elif operation["operator_configuration"]["operator_type"] == "dbt":
                operation = outputModelClass(
                    workspace_id=self.workspace_id,
                    name=operation["name"],
                    operator_configuration=OperatorConfiguration(
                        operator_type=OperatorType(operation["operator_configuration"]["operator_type"]),
                        dbt=OperatorDbt(**operation["operator_configuration"]["dbt"]),
                    ),
                )
            else:
                raise ValueError(f"Operation type {operation['operator_configuration']['operator_type']} is not supported")
            deserialized_operations.append(operation)
        return deserialized_operations

    def _check_for_legacy_connection_configuration_keys(self, configuration_to_check):
        self._check_for_wrong_casing_in_connection_configurations_keys(configuration_to_check)
        self._check_for_schedule_in_connection_configurations_keys(configuration_to_check)

    # TODO this check can be removed when all our active user are on >= 0.37.0
    def _check_for_schedule_in_connection_configurations_keys(self, configuration_to_check):
        error_message = "The schedule key is deprecated since 0.40.0, please use a combination of schedule_type and schedule_data"
        self._check_for_invalid_configuration_keys(configuration_to_check, {"schedule"}, error_message)

    def _check_for_wrong_casing_in_connection_configurations_keys(self, configuration_to_check):
        """We changed connection configuration keys from camelCase to snake_case in 0.37.0.
        This function check if the connection configuration has some camelCase keys and display a meaningful error message.
        Args:
            configuration_to_check (dict): Configuration to validate
        """
        error_message = "These keys should be in snake_case since version 0.37.0, please edit or regenerate your connection configuration"
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

    # TODO this check can be removed when all our active user are on > 0.39.18
    def _check_for_legacy_raw_configuration_keys(self, raw_configuration):
        self._check_for_invalid_configuration_keys(
            raw_configuration,
            {"source_id", "destination_id"},
            "These keys changed to source_configuration_path and destination_configuration_path in version > 0.39.18, please update your connection configuration to give path to source and destination configuration files or regenerate the connection",
        )

    def _get_local_comparable_configuration(self) -> dict:
        comparable = {
            k: v
            for k, v in self.raw_configuration["configuration"].items()
            if k not in self.local_root_level_keys_to_filter_out_for_comparison
        }
        return comparable

    def _get_remote_comparable_configuration(self) -> dict:

        comparable = {
            k: v for k, v in self.remote_resource.to_dict().items() if k not in self.remote_root_level_keys_to_filter_out_for_comparison
        }
        if "operations" in comparable:
            for operation in comparable["operations"]:
                for k in self.remote_operation_level_keys_to_filter_out:
                    operation.pop(k)
        if "operations" in comparable and len(comparable["operations"]) == 0:
            comparable.pop("operations")
        return comparable


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
