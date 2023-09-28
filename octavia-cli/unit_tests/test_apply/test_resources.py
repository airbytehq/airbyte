#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from copy import deepcopy
from unittest.mock import mock_open, patch

import pytest
from airbyte_api_client import ApiException
from airbyte_api_client.model.airbyte_catalog import AirbyteCatalog
from airbyte_api_client.model.connection_schedule_data_basic_schedule import ConnectionScheduleDataBasicSchedule
from airbyte_api_client.model.connection_schedule_type import ConnectionScheduleType
from airbyte_api_client.model.connection_status import ConnectionStatus
from airbyte_api_client.model.destination_definition_id_request_body import DestinationDefinitionIdRequestBody
from airbyte_api_client.model.destination_definition_id_with_workspace_id import DestinationDefinitionIdWithWorkspaceId
from airbyte_api_client.model.namespace_definition_type import NamespaceDefinitionType
from airbyte_api_client.model.operation_create import OperationCreate
from airbyte_api_client.model.operator_type import OperatorType
from airbyte_api_client.model.resource_requirements import ResourceRequirements
from airbyte_api_client.model.source_definition_id_request_body import SourceDefinitionIdRequestBody
from airbyte_api_client.model.source_definition_id_with_workspace_id import SourceDefinitionIdWithWorkspaceId
from airbyte_api_client.model.web_backend_operation_create_or_update import WebBackendOperationCreateOrUpdate
from octavia_cli.apply import resources, yaml_loaders


class TestResourceState:
    def test_init(self, mocker):
        mocker.patch.object(resources, "os")
        state = resources.ResourceState("config_path", "workspace_id", "resource_id", 123, "config_hash")
        assert state.configuration_path == "config_path"
        assert state.workspace_id == "workspace_id"
        assert state.resource_id == "resource_id"
        assert state.generation_timestamp == 123
        assert state.configuration_hash == "config_hash"
        assert state.path == resources.os.path.join.return_value
        resources.os.path.dirname.assert_called_with("config_path")
        resources.os.path.join.assert_called_with(resources.os.path.dirname.return_value, "state_workspace_id.yaml")

    @pytest.fixture
    def state(self):
        return resources.ResourceState("config_path", "workspace_id", "resource_id", 123, "config_hash")

    def test_as_dict(self, state):
        assert state.as_dict() == {
            "configuration_path": state.configuration_path,
            "resource_id": state.resource_id,
            "generation_timestamp": state.generation_timestamp,
            "configuration_hash": state.configuration_hash,
            "workspace_id": state.workspace_id,
        }

    def test_save(self, mocker, state):
        mocker.patch.object(resources, "yaml")
        mocker.patch.object(state, "as_dict")

        expected_content = state.as_dict.return_value
        with patch("builtins.open", mock_open()) as mock_file:
            state._save()
        mock_file.assert_called_with(state.path, "w")
        resources.yaml.dump.assert_called_with(expected_content, mock_file.return_value)

    def test_create(self, mocker):
        mocker.patch.object(resources.time, "time", mocker.Mock(return_value=0))
        mocker.patch.object(resources.ResourceState, "_save")
        state = resources.ResourceState.create("config_path", "my_hash", "workspace_id", "resource_id")
        assert isinstance(state, resources.ResourceState)
        resources.ResourceState._save.assert_called_once()
        assert state.configuration_path == "config_path"
        assert state.resource_id == "resource_id"
        assert state.generation_timestamp == 0
        assert state.configuration_hash == "my_hash"

    def test_delete(self, mocker, state):
        mocker.patch.object(resources.os, "remove")
        state.delete()
        resources.os.remove.assert_called_with(state.path)

    def test_from_file(self, mocker):
        mocker.patch.object(resources, "yaml")
        resources.yaml.safe_load.return_value = {
            "configuration_path": "config_path",
            "resource_id": "resource_id",
            "generation_timestamp": 0,
            "configuration_hash": "my_hash",
            "workspace_id": "workspace_id",
        }
        with patch("builtins.open", mock_open(read_data="data")) as mock_file:
            state = resources.ResourceState.from_file("state_workspace_id.yaml")
        resources.yaml.safe_load.assert_called_with(mock_file.return_value)
        assert isinstance(state, resources.ResourceState)
        assert state.configuration_path == "config_path"
        assert state.resource_id == "resource_id"
        assert state.generation_timestamp == 0
        assert state.configuration_hash == "my_hash"

    def test__get_path_from_configuration_and_workspace_id(self, mocker):
        mocker.patch.object(resources.os.path, "dirname", mocker.Mock(return_value="my_dir"))
        state_path = resources.ResourceState._get_path_from_configuration_and_workspace_id("config_path", "workspace_id")
        assert state_path == "my_dir/state_workspace_id.yaml"
        resources.os.path.dirname.assert_called_with("config_path")

    def test_from_configuration_path_and_workspace(self, mocker):
        mocker.patch.object(resources.ResourceState, "_get_path_from_configuration_and_workspace_id")
        mocker.patch.object(resources.ResourceState, "from_file")
        state = resources.ResourceState.from_configuration_path_and_workspace("config_path", "workspace_id")
        assert state == resources.ResourceState.from_file.return_value
        resources.ResourceState.from_file.assert_called_with(
            resources.ResourceState._get_path_from_configuration_and_workspace_id.return_value
        )
        resources.ResourceState._get_path_from_configuration_and_workspace_id.assert_called_with("config_path", "workspace_id")

    def test_migrate(self, mocker):
        mocker.patch.object(resources.ResourceState, "from_file")
        mocker.patch.object(resources.ResourceState, "create")
        new_state = resources.ResourceState.migrate("old_state_path", "workspace_id")
        resources.ResourceState.from_file.assert_called_with("old_state_path")
        old_state = resources.ResourceState.from_file.return_value
        resources.ResourceState.create.assert_called_with(
            old_state.configuration_path, old_state.configuration_hash, "workspace_id", old_state.resource_id
        )
        old_state.delete.assert_called_once()
        assert new_state == resources.ResourceState.create.return_value


@pytest.fixture
def local_configuration():
    return {
        "exotic_attribute": "foo",
        "configuration": {"foo": "bar"},
        "resource_name": "bar",
        "definition_id": "bar",
        "definition_image": "fooo",
        "definition_version": "barrr",
    }


class TestBaseResource:
    @pytest.fixture
    def patch_base_class(self, mocker):
        # Mock abstract methods to enable instantiating abstract class
        mocker.patch.object(resources.BaseResource, "__abstractmethods__", set())
        mocker.patch.object(resources.BaseResource, "create_function_name", "create_resource")
        mocker.patch.object(resources.BaseResource, "resource_id_field", "resource_id")
        mocker.patch.object(resources.BaseResource, "update_function_name", "update_resource")
        mocker.patch.object(resources.BaseResource, "get_function_name", "get_resource")
        mocker.patch.object(resources.BaseResource, "resource_type", "universal_resource")
        mocker.patch.object(resources.BaseResource, "api")

    def test_init_no_remote_resource(self, mocker, patch_base_class, mock_api_client, local_configuration):
        mocker.patch.object(resources.BaseResource, "_get_state_from_file", mocker.Mock(return_value=None))
        mocker.patch.object(resources, "hash_config")
        resource = resources.BaseResource(mock_api_client, "workspace_id", local_configuration, "bar.yaml")
        assert resource.APPLY_PRIORITY == 0
        assert resource.workspace_id == "workspace_id"
        assert resource.raw_configuration == local_configuration
        assert resource.configuration_path == "bar.yaml"
        assert resource.api_instance == resource.api.return_value
        resource.api.assert_called_with(mock_api_client)
        assert resource.state == resource._get_state_from_file.return_value
        assert resource.remote_resource is None
        assert resource.was_created is False
        assert resource.local_file_changed is True
        assert resource.resource_id is None

    def test_init_with_remote_resource_not_changed(self, mocker, patch_base_class, mock_api_client, local_configuration):
        mocker.patch.object(
            resources.BaseResource, "_get_state_from_file", mocker.Mock(return_value=mocker.Mock(configuration_hash="my_hash"))
        )
        mocker.patch.object(resources.BaseResource, "_get_remote_resource", mocker.Mock(return_value={"resource_id": "my_resource_id"}))

        mocker.patch.object(resources, "hash_config", mocker.Mock(return_value="my_hash"))
        resource = resources.BaseResource(mock_api_client, "workspace_id", local_configuration, "bar.yaml")
        assert resource.was_created is True
        assert resource.local_file_changed is False
        assert resource.resource_id == resource.state.resource_id

    def test_init_with_remote_resource_changed(self, mocker, patch_base_class, mock_api_client, local_configuration):
        mocker.patch.object(
            resources.BaseResource,
            "_get_state_from_file",
            mocker.Mock(return_value=mocker.Mock(configuration_hash="my_state_hash")),
        )
        mocker.patch.object(resources.BaseResource, "_get_remote_resource", mocker.Mock(return_value={"resource_id": "my_resource_id"}))
        mocker.patch.object(resources, "hash_config", mocker.Mock(return_value="my_new_hash"))
        resource = resources.BaseResource(mock_api_client, "workspace_id", local_configuration, "bar.yaml")
        assert resource.was_created is True
        assert resource.local_file_changed is True
        assert resource.resource_id == resource.state.resource_id

    @pytest.fixture
    def resource(self, patch_base_class, mock_api_client, local_configuration):
        return resources.BaseResource(mock_api_client, "workspace_id", local_configuration, "bar.yaml")

    def test_get_remote_resource(self, resource, mocker):
        mocker.patch.object(resource, "_get_fn")
        remote_resource = resource._get_remote_resource()
        assert remote_resource == resource._get_fn.return_value
        resource._get_fn.assert_called_with(resource.api_instance, resource.get_payload)

    @pytest.mark.parametrize(
        "state_path_is_file, legacy_state_path_is_file, confirm_migration",
        [(True, False, False), (False, True, True), (False, True, False), (False, False, False)],
    )
    def test_get_state_from_file(self, mocker, resource, state_path_is_file, legacy_state_path_is_file, confirm_migration):
        mocker.patch.object(resources, "os")
        mocker.patch.object(resources.click, "confirm", mocker.Mock(return_value=confirm_migration))
        mock_expected_state_path = mocker.Mock(is_file=mocker.Mock(return_value=state_path_is_file))
        mock_expected_legacy_state_path = mocker.Mock(is_file=mocker.Mock(return_value=legacy_state_path_is_file))
        mocker.patch.object(resources, "Path", mocker.Mock(side_effect=[mock_expected_state_path, mock_expected_legacy_state_path]))
        mocker.patch.object(resources, "ResourceState")

        if legacy_state_path_is_file and not confirm_migration:
            with pytest.raises(resources.InvalidStateError):
                state = resource._get_state_from_file(resource.configuration_path, resource.workspace_id)
        else:
            state = resource._get_state_from_file(resource.configuration_path, resource.workspace_id)

        resources.os.path.dirname.assert_called_with(resource.configuration_path)
        resources.os.path.join.assert_has_calls(
            [
                mocker.call(resources.os.path.dirname.return_value, f"state_{resource.workspace_id}.yaml"),
                mocker.call(resources.os.path.dirname.return_value, "state.yaml"),
            ]
        )
        resources.Path.assert_called_with(resources.os.path.join.return_value)
        mock_expected_state_path.is_file.assert_called_once()
        if state_path_is_file:
            resources.ResourceState.from_file.assert_called_with(mock_expected_state_path)
            assert state == resources.ResourceState.from_file.return_value
            mock_expected_legacy_state_path.is_file.assert_not_called()
        elif legacy_state_path_is_file:
            if confirm_migration:
                mock_expected_legacy_state_path.is_file.assert_called_once()
                resources.ResourceState.migrate.assert_called_with(mock_expected_legacy_state_path, resource.workspace_id)
                assert state == resources.ResourceState.migrate.return_value
        else:
            assert state is None

    @pytest.mark.parametrize(
        "was_created",
        [True, False],
    )
    def test_get_diff_with_remote_resource(self, patch_base_class, mocker, mock_api_client, local_configuration, was_created):
        mocker.patch.object(resources.BaseResource, "_get_remote_comparable_configuration")
        mocker.patch.object(resources.BaseResource, "was_created", was_created)
        resource = resources.BaseResource(mock_api_client, "workspace_id", local_configuration, "bar.yaml")
        mocker.patch.object(resources, "compute_diff")
        if was_created:
            diff = resource.get_diff_with_remote_resource()
            resources.compute_diff.assert_called_with(resource._get_remote_comparable_configuration.return_value, resource.configuration)
            assert diff == resources.compute_diff.return_value.pretty.return_value
        else:
            with pytest.raises(resources.NonExistingResourceError):
                resource.get_diff_with_remote_resource()

    def test_create_or_update(self, mocker, resource):
        expected_results = {resource.resource_id_field: "resource_id"}
        operation_fn = mocker.Mock(return_value=expected_results)
        mocker.patch.object(resources, "ResourceState")
        payload = "foo"
        result, state = resource._create_or_update(operation_fn, payload)
        assert result == expected_results
        assert state == resources.ResourceState.create.return_value
        resources.ResourceState.create.assert_called_with(
            resource.configuration_path, resource.configuration_hash, resource.workspace_id, "resource_id"
        )

    @pytest.mark.parametrize(
        "response_status,expected_error",
        [(404, ApiException), (422, resources.InvalidConfigurationError)],
    )
    def test_create_or_update_error(self, mocker, resource, response_status, expected_error):
        operation_fn = mocker.Mock(side_effect=ApiException(status=response_status))
        mocker.patch.object(resources, "ResourceState")
        with pytest.raises(expected_error):
            resource._create_or_update(operation_fn, "foo")

    def test_create(self, mocker, resource):
        mocker.patch.object(resource, "_create_or_update")
        assert resource.create() == resource._create_or_update.return_value
        resource._create_or_update.assert_called_with(resource._create_fn, resource.create_payload)

    def test_update(self, mocker, resource):
        mocker.patch.object(resource, "_create_or_update")
        assert resource.update() == resource._create_or_update.return_value
        resource._create_or_update.assert_called_with(resource._update_fn, resource.update_payload)

    def test_manage(self, mocker, resource):
        mocker.patch.object(resources, "ResourceState")
        remote_resource, new_state = resource.manage("resource_id")
        resources.ResourceState.create.assert_called_with(
            resource.configuration_path, resource.configuration_hash, resource.workspace_id, "resource_id"
        )
        assert new_state == resources.ResourceState.create.return_value
        assert remote_resource == resource.remote_resource

    @pytest.mark.parametrize(
        "configuration, invalid_keys, expect_error",
        [
            ({"valid_key": "foo", "invalidKey": "bar"}, {"invalidKey"}, True),
            ({"valid_key": "foo", "invalidKey": "bar", "secondInvalidKey": "bar"}, {"invalidKey", "secondInvalidKey"}, True),
            ({"valid_key": "foo", "validKey": "bar"}, {"invalidKey"}, False),
        ],
    )
    def test__check_for_invalid_configuration_keys(self, configuration, invalid_keys, expect_error):
        if not expect_error:
            result = resources.BaseResource._check_for_invalid_configuration_keys(configuration, invalid_keys, "Invalid configuration keys")
            assert result is None
        else:
            with pytest.raises(resources.InvalidConfigurationError, match="Invalid configuration keys") as error_info:
                resources.BaseResource._check_for_invalid_configuration_keys(configuration, invalid_keys, "Invalid configuration keys")
            assert all([invalid_key in str(error_info) for invalid_key in invalid_keys])


class TestSourceAndDestination:
    @pytest.fixture
    def patch_source_and_destination(self, mocker):
        mocker.patch.object(resources.SourceAndDestination, "__abstractmethods__", set())
        mocker.patch.object(resources.SourceAndDestination, "api")
        mocker.patch.object(resources.SourceAndDestination, "create_function_name", "create")
        mocker.patch.object(resources.SourceAndDestination, "update_function_name", "update")
        mocker.patch.object(resources.SourceAndDestination, "get_function_name", "get")
        mocker.patch.object(resources.SourceAndDestination, "_get_state_from_file", mocker.Mock(return_value=None))
        mocker.patch.object(resources, "hash_config")

    def test_init(self, patch_source_and_destination, mocker, mock_api_client, local_configuration):
        assert resources.SourceAndDestination.__base__ == resources.BaseResource
        resource = resources.SourceAndDestination(mock_api_client, "workspace_id", local_configuration, "bar.yaml")
        assert resource.definition_id == local_configuration["definition_id"]
        assert resource.definition_image == local_configuration["definition_image"]
        assert resource.definition_version == local_configuration["definition_version"]

    def test_get_remote_comparable_configuration(self, patch_source_and_destination, mocker, mock_api_client, local_configuration):
        mocker.patch.object(resources.Source, "remote_resource")
        resource = resources.Source(mock_api_client, "workspace_id", local_configuration, "bar.yaml")
        assert resource._get_remote_comparable_configuration() == resource.remote_resource.connection_configuration


class TestSource:
    @pytest.mark.parametrize(
        "state",
        [None, resources.ResourceState("config_path", "workspace_id", "resource_id", 123, "abc")],
    )
    def test_init(self, mocker, mock_api_client, local_configuration, state):
        assert resources.Source.__base__ == resources.SourceAndDestination
        mocker.patch.object(resources.Source, "resource_id", "foo")
        source = resources.Source(mock_api_client, "workspace_id", local_configuration, "bar.yaml")
        mocker.patch.object(source, "state", state)
        assert source.api == resources.source_api.SourceApi
        assert source.create_function_name == "create_source"
        assert source.resource_id_field == "source_id"
        assert source.update_function_name == "update_source"
        assert source.resource_type == "source"
        assert source.APPLY_PRIORITY == 0
        assert source.create_payload == resources.SourceCreate(
            source.definition_id, source.configuration, source.workspace_id, source.resource_name
        )
        assert source.update_payload == resources.SourceUpdate(
            source_id=source.resource_id, connection_configuration=source.configuration, name=source.resource_name
        )
        if state is None:
            assert source.get_payload is None
        else:
            assert source.get_payload == resources.SourceIdRequestBody(state.resource_id)

    @pytest.mark.parametrize(
        "resource_id",
        [None, "foo"],
    )
    def test_source_discover_schema_request_body(self, mocker, mock_api_client, resource_id, local_configuration):
        mocker.patch.object(resources, "SourceDiscoverSchemaRequestBody")
        mocker.patch.object(resources.Source, "resource_id", resource_id)
        source = resources.Source(mock_api_client, "workspace_id", local_configuration, "bar.yaml")
        if resource_id is None:
            with pytest.raises(resources.NonExistingResourceError):
                source.source_discover_schema_request_body
                resources.SourceDiscoverSchemaRequestBody.assert_not_called()
        else:
            assert source.source_discover_schema_request_body == resources.SourceDiscoverSchemaRequestBody.return_value
            resources.SourceDiscoverSchemaRequestBody.assert_called_with(source.resource_id)

    def test_catalog(self, mocker, mock_api_client, local_configuration):
        mocker.patch.object(resources.Source, "source_discover_schema_request_body")
        source = resources.Source(mock_api_client, "workspace_id", local_configuration, "bar.yaml")
        source.api_instance = mocker.Mock()
        catalog = source.catalog
        assert catalog == source.api_instance.discover_schema_for_source.return_value.catalog
        source.api_instance.discover_schema_for_source.assert_called_with(source.source_discover_schema_request_body)

    def test_definition(self, mocker, mock_api_client, local_configuration):
        mocker.patch.object(resources.source_definition_api, "SourceDefinitionApi")
        mock_api_instance = resources.source_definition_api.SourceDefinitionApi.return_value
        source = resources.Source(mock_api_client, "workspace_id", local_configuration, "bar.yaml")
        assert source.definition == mock_api_instance.get_source_definition.return_value
        resources.source_definition_api.SourceDefinitionApi.assert_called_with(mock_api_client)
        expected_payload = SourceDefinitionIdRequestBody(source_definition_id=source.definition_id)
        mock_api_instance.get_source_definition.assert_called_with(expected_payload)

    def test_definition_specification(self, mocker, mock_api_client, local_configuration):
        mocker.patch.object(resources.source_definition_specification_api, "SourceDefinitionSpecificationApi")
        mock_api_instance = resources.source_definition_specification_api.SourceDefinitionSpecificationApi.return_value
        source = resources.Source(mock_api_client, "workspace_id", local_configuration, "bar.yaml")
        assert source.definition_specification == mock_api_instance.get_source_definition_specification.return_value
        resources.source_definition_specification_api.SourceDefinitionSpecificationApi.assert_called_with(mock_api_client)
        expected_payload = SourceDefinitionIdWithWorkspaceId(source_definition_id=source.definition_id, workspace_id=source.workspace_id)
        mock_api_instance.get_source_definition_specification.assert_called_with(expected_payload)


class TestDestination:
    @pytest.mark.parametrize(
        "state",
        [None, resources.ResourceState("config_path", "workspace_id", "resource_id", 123, "abc")],
    )
    def test_init(self, mocker, mock_api_client, local_configuration, state):
        assert resources.Destination.__base__ == resources.SourceAndDestination
        mocker.patch.object(resources.Destination, "resource_id", "foo")
        destination = resources.Destination(mock_api_client, "workspace_id", local_configuration, "bar.yaml")
        mocker.patch.object(destination, "state", state)
        assert destination.api == resources.destination_api.DestinationApi
        assert destination.create_function_name == "create_destination"
        assert destination.resource_id_field == "destination_id"
        assert destination.update_function_name == "update_destination"
        assert destination.resource_type == "destination"
        assert destination.APPLY_PRIORITY == 0
        assert destination.create_payload == resources.DestinationCreate(
            destination.workspace_id, destination.resource_name, destination.definition_id, destination.configuration
        )
        assert destination.update_payload == resources.DestinationUpdate(
            destination_id=destination.resource_id, connection_configuration=destination.configuration, name=destination.resource_name
        )
        if state is None:
            assert destination.get_payload is None
        else:
            assert destination.get_payload == resources.DestinationIdRequestBody(state.resource_id)

    def test_definition(self, mocker, mock_api_client, local_configuration):
        mocker.patch.object(resources.destination_definition_api, "DestinationDefinitionApi")
        mock_api_instance = resources.destination_definition_api.DestinationDefinitionApi.return_value
        destination = resources.Destination(mock_api_client, "workspace_id", local_configuration, "bar.yaml")
        assert destination.definition == mock_api_instance.get_destination_definition.return_value
        resources.destination_definition_api.DestinationDefinitionApi.assert_called_with(mock_api_client)
        expected_payload = DestinationDefinitionIdRequestBody(
            destination_definition_id=destination.definition_id
        )
        mock_api_instance.get_destination_definition.assert_called_with(expected_payload)

    def test_definition_specification(self, mocker, mock_api_client, local_configuration):
        mocker.patch.object(resources.destination_definition_specification_api, "DestinationDefinitionSpecificationApi")
        mock_api_instance = resources.destination_definition_specification_api.DestinationDefinitionSpecificationApi.return_value
        destination = resources.Destination(mock_api_client, "workspace_id", local_configuration, "bar.yaml")
        assert destination.definition_specification == mock_api_instance.get_destination_definition_specification.return_value
        resources.destination_definition_specification_api.DestinationDefinitionSpecificationApi.assert_called_with(mock_api_client)
        expected_payload = DestinationDefinitionIdWithWorkspaceId(
            destination_definition_id=destination.definition_id, workspace_id=destination.workspace_id
        )
        mock_api_instance.get_destination_definition_specification.assert_called_with(expected_payload)


class TestConnection:
    @pytest.fixture
    def connection_configuration(self):
        return {
            "definition_type": "connection",
            "resource_name": "my_connection",
            "source_configuration_path": "my_source_configuration_path",
            "destination_configuration_path": "my_destination_configuration_path",
            "configuration": {
                "namespace_definition": "customformat",
                "namespace_format": "foo",
                "prefix": "foo",
                "sync_catalog": {
                    "streams": [
                        {
                            "stream": {
                                "name": "name_example",
                                "json_schema": {},
                                "supported_sync_modes": ["incremental"],
                                "source_defined_cursor": True,
                                "default_cursor_field": ["default_cursor_field"],
                                "source_defined_primary_key": [["string_example"]],
                                "namespace": "namespace_example",
                            },
                            "config": {
                                "sync_mode": "incremental",
                                "cursor_field": ["cursor_field_example"],
                                "destination_sync_mode": "append_dedup",
                                "primary_key": [["string_example"]],
                                "alias_name": "alias_name_example",
                                "selected": True,
                            },
                        }
                    ]
                },
                "schedule_type": "basic",
                "schedule_data": {"units": 1, "time_unit": "days"},
                "status": "active",
                "resource_requirements": {"cpu_request": "foo", "cpu_limit": "foo", "memory_request": "foo", "memory_limit": "foo"},
            },
        }

    @pytest.fixture
    def connection_configuration_with_manual_schedule(self, connection_configuration):
        connection_configuration_with_manual_schedule = deepcopy(connection_configuration)
        connection_configuration_with_manual_schedule["configuration"]["schedule_type"] = "manual"
        connection_configuration_with_manual_schedule["configuration"]["schedule_data"] = None
        return connection_configuration_with_manual_schedule

    @pytest.fixture
    def connection_configuration_with_normalization(self, connection_configuration):
        connection_configuration_with_normalization = deepcopy(connection_configuration)
        connection_configuration_with_normalization["configuration"]["operations"] = [
            {"name": "Normalization", "operator_configuration": {"normalization": {"option": "basic"}, "operator_type": "normalization"}}
        ]
        return connection_configuration_with_normalization

    @pytest.fixture
    def legacy_connection_configurations(self):
        return [
            {
                "definition_type": "connection",
                "resource_name": "my_connection",
                "source_id": "my_source",
                "destination_id": "my_destination",
                "configuration": {
                    "namespaceDefinition": "customformat",
                    "namespaceFormat": "foo",
                    "prefix": "foo",
                    "syncCatalog": {
                        "streams": [
                            {
                                "stream": {
                                    "name": "name_example",
                                    "json_schema": {},
                                    "supported_sync_modes": ["incremental"],
                                    "source_defined_cursor": True,
                                    "default_cursor_field": ["default_cursor_field"],
                                    "source_defined_primary_key": [["string_example"]],
                                    "namespace": "namespace_example",
                                },
                                "config": {
                                    "sync_mode": "incremental",
                                    "cursor_field": ["cursor_field_example"],
                                    "destination_sync_mode": "append_dedup",
                                    "primary_key": [["string_example"]],
                                    "alias_name": "alias_name_example",
                                    "selected": True,
                                },
                            }
                        ]
                    },
                    "schedule": {"units": 1, "time_unit": "days"},
                    "status": "active",
                    "resourceRequirements": {"cpu_request": "foo", "cpu_limit": "foo", "memory_request": "foo", "memory_limit": "foo"},
                },
            },
            {
                "definition_type": "connection",
                "resource_name": "my_connection",
                "source_id": "my_source",
                "destination_id": "my_destination",
                "configuration": {
                    "namespace_definition": "customformat",
                    "namespace_format": "foo",
                    "prefix": "foo",
                    "sync_catalog": {
                        "streams": [
                            {
                                "stream": {
                                    "name": "name_example",
                                    "jsonSchema": {},
                                    "supportedSyncModes": ["incremental"],
                                    "sourceDefinedCursor": True,
                                    "defaultCursorField": ["default_cursor_field"],
                                    "sourceDefinedPrimary_key": [["string_example"]],
                                    "namespace": "namespace_example",
                                },
                                "config": {
                                    "syncMode": "incremental",
                                    "cursorField": ["cursor_field_example"],
                                    "destinationSyncMode": "append_dedup",
                                    "primaryKey": [["string_example"]],
                                    "aliasName": "alias_name_example",
                                    "selected": True,
                                },
                            }
                        ]
                    },
                    "schedule": {"units": 1, "time_unit": "days"},
                    "status": "active",
                    "resource_requirements": {"cpu_request": "foo", "cpu_limit": "foo", "memory_request": "foo", "memory_limit": "foo"},
                },
            },
            {
                "definition_type": "connection",
                "resource_name": "my_connection",
                "source_id": "my_source",
                "destination_id": "my_destination",
                "configuration": {
                    "namespace_definition": "customformat",
                    "namespace_format": "foo",
                    "prefix": "foo",
                    "sync_catalog": {
                        "streams": [
                            {
                                "stream": {},
                                "config": {},
                            }
                        ]
                    },
                    "schedule": {"units": 1, "time_unit": "days"},
                    "status": "active",
                    "resource_requirements": {"cpu_request": "foo", "cpu_limit": "foo", "memory_request": "foo", "memory_limit": "foo"},
                },
            },
        ]

    @pytest.mark.parametrize(
        "state",
        [None, resources.ResourceState("config_path", "workspace_id", "resource_id", 123, "abc")],
    )
    def test_init(self, mocker, mock_api_client, state, connection_configuration):
        assert resources.Connection.__base__ == resources.BaseResource
        mocker.patch.object(resources.Connection, "resource_id", "foo")
        connection = resources.Connection(mock_api_client, "workspace_id", connection_configuration, "bar.yaml")
        mocker.patch.object(connection, "state", state)
        assert connection.api == resources.web_backend_api.WebBackendApi
        assert connection.create_function_name == "web_backend_create_connection"
        assert connection.update_function_name == "web_backend_update_connection"
        assert connection.resource_id_field == "connection_id"
        assert connection.resource_type == "connection"
        assert connection.APPLY_PRIORITY == 1

        assert connection.update_payload == resources.WebBackendConnectionUpdate(
            connection_id=connection.resource_id, **connection.configuration
        )
        if state is None:
            assert connection.get_payload is None
        else:
            assert connection.get_payload == resources.WebBackendConnectionRequestBody(
                connection_id=state.resource_id, with_refreshed_catalog=False
            )

    @pytest.mark.parametrize("file_not_found_error", [False, True])
    def test_source_id(self, mocker, mock_api_client, connection_configuration, file_not_found_error):
        assert resources.Connection.__base__ == resources.BaseResource
        mocker.patch.object(resources.Connection, "resource_id", "foo")
        if file_not_found_error:
            mocker.patch.object(
                resources.ResourceState, "from_configuration_path_and_workspace", mocker.Mock(side_effect=FileNotFoundError())
            )
        else:
            mocker.patch.object(
                resources.ResourceState,
                "from_configuration_path_and_workspace",
                mocker.Mock(return_value=mocker.Mock(resource_id="expected_source_id")),
            )

        connection = resources.Connection(mock_api_client, "workspace_id", connection_configuration, "bar.yaml")
        if file_not_found_error:
            with pytest.raises(resources.MissingStateError):
                connection.source_id
        else:
            source_id = connection.source_id
            assert source_id == "expected_source_id"
        resources.ResourceState.from_configuration_path_and_workspace.assert_called_with(
            connection_configuration["source_configuration_path"], connection.workspace_id
        )

    @pytest.mark.parametrize("file_not_found_error", [False, True])
    def test_destination_id(self, mocker, mock_api_client, connection_configuration, file_not_found_error):
        assert resources.Connection.__base__ == resources.BaseResource
        mocker.patch.object(resources.Connection, "resource_id", "foo")
        if file_not_found_error:
            mocker.patch.object(
                resources.ResourceState, "from_configuration_path_and_workspace", mocker.Mock(side_effect=FileNotFoundError())
            )
        else:
            mocker.patch.object(
                resources.ResourceState,
                "from_configuration_path_and_workspace",
                mocker.Mock(return_value=mocker.Mock(resource_id="expected_destination_id")),
            )

        connection = resources.Connection(mock_api_client, "workspace_id", connection_configuration, "bar.yaml")
        if file_not_found_error:
            with pytest.raises(resources.MissingStateError):
                connection.destination_id
        else:
            destination_id = connection.destination_id
            assert destination_id == "expected_destination_id"
        resources.ResourceState.from_configuration_path_and_workspace.assert_called_with(
            connection_configuration["destination_configuration_path"], connection.workspace_id
        )

    def test_create_payload_no_normalization(self, mocker, mock_api_client, connection_configuration):
        assert resources.Connection.__base__ == resources.BaseResource
        mocker.patch.object(resources.Connection, "resource_id", "foo")
        mocker.patch.object(resources.Connection, "source_id", "source_id")
        mocker.patch.object(resources.Connection, "destination_id", "destination_id")
        connection = resources.Connection(mock_api_client, "workspace_id", connection_configuration, "bar.yaml")
        assert connection.create_payload == resources.WebBackendConnectionCreate(
            name=connection.resource_name,
            source_id=connection.source_id,
            destination_id=connection.destination_id,
            **connection.configuration,
        )
        assert "operations" not in connection.create_payload

    def test_create_payload_with_normalization(self, mocker, mock_api_client, connection_configuration_with_normalization):
        assert resources.Connection.__base__ == resources.BaseResource
        mocker.patch.object(resources.Connection, "resource_id", "foo")
        mocker.patch.object(resources.Connection, "source_id", "source_id")
        mocker.patch.object(resources.Connection, "destination_id", "destination_id")
        connection = resources.Connection(mock_api_client, "workspace_id", connection_configuration_with_normalization, "bar.yaml")
        assert connection.create_payload == resources.WebBackendConnectionCreate(
            name=connection.resource_name,
            source_id=connection.source_id,
            destination_id=connection.destination_id,
            **connection.configuration,
        )
        assert isinstance(connection.create_payload["operations"][0], OperationCreate)

    def test_update_payload_no_normalization(self, mocker, mock_api_client, connection_configuration):
        assert resources.Connection.__base__ == resources.BaseResource
        mocker.patch.object(resources.Connection, "resource_id", "foo")
        mocker.patch.object(resources.Connection, "source_id", "source_id")
        mocker.patch.object(resources.Connection, "destination_id", "destination_id")
        connection = resources.Connection(mock_api_client, "workspace_id", connection_configuration, "bar.yaml")
        assert connection.update_payload == resources.WebBackendConnectionUpdate(
            connection_id=connection.resource_id,
            **connection.configuration,
        )
        assert "operations" not in connection.update_payload

    def test_update_payload_with_normalization(self, mocker, mock_api_client, connection_configuration_with_normalization):
        assert resources.Connection.__base__ == resources.BaseResource
        mocker.patch.object(resources.Connection, "resource_id", "foo")
        mocker.patch.object(resources.Connection, "source_id", "source_id")
        mocker.patch.object(resources.Connection, "destination_id", "destination_id")
        connection = resources.Connection(mock_api_client, "workspace_id", connection_configuration_with_normalization, "bar.yaml")
        assert connection.update_payload == resources.WebBackendConnectionUpdate(
            connection_id=connection.resource_id,
            **connection.configuration,
        )
        assert isinstance(connection.update_payload["operations"][0], WebBackendOperationCreateOrUpdate)

    @pytest.mark.parametrize(
        "remote_resource",
        [
            {
                "name": "foo",
                "source_id": "bar",
                "destination_id": "fooo",
                "connection_id": "baar",
                "operation_ids": "foooo",
                "foo": "bar",
            },
            {
                "name": "foo",
                "source_id": "bar",
                "destination_id": "fooo",
                "connection_id": "baar",
                "operation_ids": "foooo",
                "foo": "bar",
                "operations": [],
            },
            {
                "name": "foo",
                "source_id": "bar",
                "destination_id": "fooo",
                "connection_id": "baar",
                "operation_ids": "foooo",
                "foo": "bar",
                "operations": [{"workspace_id": "foo", "operation_id": "foo", "operator_configuration": {"normalization": "foo"}}],
            },
            {
                "name": "foo",
                "source_id": "bar",
                "destination_id": "fooo",
                "connection_id": "baar",
                "operation_ids": "foooo",
                "foo": "bar",
                "operations": [{"workspace_id": "foo", "operation_id": "foo", "operator_configuration": {"dbt": "foo"}}],
            },
        ],
    )
    def test_get_remote_comparable_configuration(self, mocker, mock_api_client, connection_configuration, remote_resource):
        mocker.patch.object(
            resources.Connection,
            "remote_resource",
            mocker.Mock(to_dict=mocker.Mock(return_value=remote_resource)),
        )
        resource = resources.Connection(mock_api_client, "workspace_id", connection_configuration, "bar.yaml")
        comparable = resource._get_remote_comparable_configuration()
        resource.remote_resource.to_dict.assert_called_once()

        assert isinstance(comparable, dict)
        assert all([k not in comparable for k in resource.remote_root_level_keys_to_filter_out_for_comparison])
        if "operations" in remote_resource and "operations" in comparable:
            assert all([k not in comparable["operations"][0] for k in resource.remote_operation_level_keys_to_filter_out])
            if remote_resource["operations"][0]["operator_configuration"].get("normalization") is not None:
                assert "dbt" not in remote_resource["operations"][0]["operator_configuration"]
            if remote_resource["operations"][0]["operator_configuration"].get("dbt") is not None:
                assert "normalization" not in remote_resource["operations"][0]["operator_configuration"]
        if "operations" in remote_resource and len(remote_resource["operations"]) == 0:
            assert "operations" not in comparable

    def test_create(self, mocker, mock_api_client, connection_configuration):
        mocker.patch.object(resources.Connection, "_create_or_update")
        mocker.patch.object(resources.Connection, "source_id", "source_id")
        mocker.patch.object(resources.Connection, "destination_id", "destination_id")
        resource = resources.Connection(mock_api_client, "workspace_id", connection_configuration, "bar.yaml")
        create_result = resource.create()
        assert create_result == resource._create_or_update.return_value
        resource._create_or_update.assert_called_with(resource._create_fn, resource.create_payload)

    def test_update(self, mocker, mock_api_client, connection_configuration):
        mocker.patch.object(resources.Connection, "_create_or_update")
        resource = resources.Connection(mock_api_client, "workspace_id", connection_configuration, "bar.yaml")
        resource.state = mocker.Mock(resource_id="foo")
        update_result = resource.update()
        assert update_result == resource._create_or_update.return_value
        resource._create_or_update.assert_called_with(resource._update_fn, resource.update_payload)

    def test__deserialize_raw_configuration(self, mock_api_client, connection_configuration, connection_configuration_with_manual_schedule):
        resource = resources.Connection(mock_api_client, "workspace_id", connection_configuration, "bar.yaml")
        configuration = resource._deserialize_raw_configuration()
        assert isinstance(configuration["sync_catalog"], AirbyteCatalog)
        assert configuration["namespace_definition"] == NamespaceDefinitionType(
            connection_configuration["configuration"]["namespace_definition"]
        )
        assert configuration["schedule_type"] == ConnectionScheduleType(connection_configuration["configuration"]["schedule_type"])
        assert (
            configuration["schedule_data"].to_dict()
            == ConnectionScheduleDataBasicSchedule(**connection_configuration["configuration"]["schedule_data"]).to_dict()
        )
        assert configuration["resource_requirements"] == ResourceRequirements(
            **connection_configuration["configuration"]["resource_requirements"]
        )
        assert configuration["status"] == ConnectionStatus(connection_configuration["configuration"]["status"])
        assert list(configuration.keys()) == [
            "namespace_definition",
            "namespace_format",
            "prefix",
            "sync_catalog",
            "schedule_type",
            "schedule_data",
            "status",
            "resource_requirements",
            "non_breaking_changes_preference",
            "geography",
        ]

        resource = resources.Connection(mock_api_client, "workspace_id", connection_configuration_with_manual_schedule, "bar.yaml")
        configuration = resource._deserialize_raw_configuration()
        assert configuration["schedule_type"] == ConnectionScheduleType(
            connection_configuration_with_manual_schedule["configuration"]["schedule_type"]
        )
        assert configuration["schedule_data"] is None

    def test__deserialize_operations(self, mock_api_client, connection_configuration):
        resource = resources.Connection(mock_api_client, "workspace_id", connection_configuration, "bar.yaml")
        operations = [
            {
                "operator_configuration": {"operator_type": "normalization", "normalization": {"option": "basic"}},
                "name": "operation-with-normalization",
            },
            {
                "operator_configuration": {
                    "operator_type": "dbt",
                    "dbt": {
                        "dbt_arguments": "run",
                        "docker_image": "fishtownanalytics/dbt:0.19.1",
                        "git_repo_branch": "my-branch-name",
                        "git_repo_url": "https://github.com/airbytehq/airbyte",
                    },
                },
                "name": "operation-with-custom_dbt",
            },
        ]
        deserialized_operations = resource._deserialize_operations(operations, OperationCreate)
        assert len(deserialized_operations) == 2
        assert all([isinstance(o, OperationCreate) for o in deserialized_operations])
        assert "normalization" in deserialized_operations[0]["operator_configuration"] and deserialized_operations[0][
            "operator_configuration"
        ]["operator_type"] == OperatorType("normalization")
        assert "dbt" in deserialized_operations[1]["operator_configuration"]
        assert deserialized_operations[1]["operator_configuration"]["operator_type"] == OperatorType("dbt")

        with pytest.raises(ValueError):
            resource._deserialize_operations(
                [
                    {
                        "operator_configuration": {"operator_type": "not-supported", "normalization": {"option": "basic"}},
                        "name": "operation-not-supported",
                    },
                ],
                OperationCreate,
            )

    def test__create_configured_catalog(self, mock_api_client, connection_configuration):
        resource = resources.Connection(mock_api_client, "workspace_id", connection_configuration, "bar.yaml")
        created_catalog = resource._create_configured_catalog(connection_configuration["configuration"]["sync_catalog"])
        stream, config = (
            connection_configuration["configuration"]["sync_catalog"]["streams"][0]["stream"],
            connection_configuration["configuration"]["sync_catalog"]["streams"][0]["config"],
        )

        assert len(created_catalog.streams) == len(connection_configuration["configuration"]["sync_catalog"]["streams"])
        assert created_catalog.streams[0].stream.name == stream["name"]
        assert created_catalog.streams[0].stream.json_schema == stream["json_schema"]
        assert created_catalog.streams[0].stream.supported_sync_modes == stream["supported_sync_modes"]
        assert created_catalog.streams[0].stream.source_defined_cursor == stream["source_defined_cursor"]
        assert created_catalog.streams[0].stream.namespace == stream["namespace"]
        assert created_catalog.streams[0].stream.source_defined_primary_key == stream["source_defined_primary_key"]
        assert created_catalog.streams[0].stream.default_cursor_field == stream["default_cursor_field"]

        assert created_catalog.streams[0].config.sync_mode == config["sync_mode"]
        assert created_catalog.streams[0].config.cursor_field == config["cursor_field"]
        assert created_catalog.streams[0].config.destination_sync_mode == config["destination_sync_mode"]
        assert created_catalog.streams[0].config.primary_key == config["primary_key"]
        assert created_catalog.streams[0].config.alias_name == config["alias_name"]
        assert created_catalog.streams[0].config.selected == config["selected"]

    def test__check_for_legacy_connection_configuration_keys(
        self, mock_api_client, connection_configuration, legacy_connection_configurations
    ):
        resource = resources.Connection(mock_api_client, "workspace_id", connection_configuration, "bar.yaml")
        assert resource._check_for_legacy_connection_configuration_keys(connection_configuration["configuration"]) is None
        for legacy_configuration in legacy_connection_configurations:
            with pytest.raises(resources.InvalidConfigurationError):
                resource._check_for_legacy_connection_configuration_keys(legacy_configuration["configuration"])


@pytest.mark.parametrize(
    "local_configuration,resource_to_mock,expected_error",
    [
        ({"definition_type": "source"}, "Source", None),
        ({"definition_type": "destination"}, "Destination", None),
        ({"definition_type": "connection"}, "Connection", None),
        ({"definition_type": "not_existing"}, None, NotImplementedError),
    ],
)
def test_factory(mocker, mock_api_client, local_configuration, resource_to_mock, expected_error):
    mocker.patch.object(resources, "yaml")
    if resource_to_mock is not None:
        mocker.patch.object(resources, resource_to_mock)
    resources.yaml.load.return_value = local_configuration
    with patch("builtins.open", mock_open(read_data="data")) as mock_file:
        if not expected_error:
            resource = resources.factory(mock_api_client, "workspace_id", "my_config.yaml")
            resources.yaml.load.assert_called_with(mock_file.return_value, yaml_loaders.EnvVarLoader)
            resource == getattr(resources, resource_to_mock).return_value
            mock_file.assert_called_with("my_config.yaml", "r")
        else:
            with pytest.raises(expected_error):
                resources.factory(mock_api_client, "workspace_id", "my_config.yaml")
                mock_file.assert_called_with("my_config.yaml", "r")
