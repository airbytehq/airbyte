#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import mock_open, patch

import pytest
from airbyte_api_client import ApiException
from octavia_cli.apply import resources, yaml_loaders


class TestResourceState:
    def test_init(self, mocker):
        mocker.patch.object(resources, "os")
        state = resources.ResourceState("config_path", "resource_id", 123, "config_hash")
        assert state.configuration_path == "config_path"
        assert state.resource_id == "resource_id"
        assert state.generation_timestamp == 123
        assert state.configuration_hash == "config_hash"
        assert state.path == resources.os.path.join.return_value
        resources.os.path.dirname.assert_called_with("config_path")
        resources.os.path.join.assert_called_with(resources.os.path.dirname.return_value, "state.yaml")

    @pytest.fixture
    def state(self):
        return resources.ResourceState("config_path", "resource_id", 123, "config_hash")

    def test_as_dict(self, state):
        assert state.as_dict() == {
            "configuration_path": state.configuration_path,
            "resource_id": state.resource_id,
            "generation_timestamp": state.generation_timestamp,
            "configuration_hash": state.configuration_hash,
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
        mocker.patch.object(resources, "hash_config", mocker.Mock(return_value="my_hash"))
        mocker.patch.object(resources.ResourceState, "_save")
        state = resources.ResourceState.create("config_path", {"my": "config"}, "resource_id")
        assert isinstance(state, resources.ResourceState)
        resources.ResourceState._save.assert_called_once()
        assert state.configuration_path == "config_path"
        assert state.resource_id == "resource_id"
        assert state.generation_timestamp == 0
        assert state.configuration_hash == "my_hash"

    def test_from_file(self, mocker):
        mocker.patch.object(resources, "yaml")
        resources.yaml.safe_load.return_value = {
            "configuration_path": "config_path",
            "resource_id": "resource_id",
            "generation_timestamp": 0,
            "configuration_hash": "my_hash",
        }
        with patch("builtins.open", mock_open(read_data="data")) as mock_file:
            state = resources.ResourceState.from_file("state.yaml")
        resources.yaml.safe_load.assert_called_with(mock_file.return_value)
        assert isinstance(state, resources.ResourceState)
        assert state.configuration_path == "config_path"
        assert state.resource_id == "resource_id"
        assert state.generation_timestamp == 0
        assert state.configuration_hash == "my_hash"


@pytest.fixture
def local_configuration():
    return {"exotic_attribute": "foo", "configuration": {"foo": "bar"}, "resource_name": "bar", "definition_id": "bar"}


class TestBaseResource:
    @pytest.fixture
    def patch_base_class(self, mocker):
        # Mock abstract methods to enable instantiating abstract class
        mocker.patch.object(resources.BaseResource, "__abstractmethods__", set())
        mocker.patch.object(resources.BaseResource, "create_function_name", "create_resource")
        mocker.patch.object(resources.BaseResource, "resource_id_field", "resource_id")
        mocker.patch.object(resources.BaseResource, "ResourceIdRequestBody")
        mocker.patch.object(resources.BaseResource, "search_function_name", "search_resource")
        mocker.patch.object(resources.BaseResource, "update_function_name", "update_resource")
        mocker.patch.object(resources.BaseResource, "resource_type", "universal_resource")
        mocker.patch.object(resources.BaseResource, "api")

    def test_init_no_remote_resource(self, mocker, patch_base_class, mock_api_client, local_configuration):
        mocker.patch.object(resources.BaseResource, "_get_state_from_file", mocker.Mock(return_value=None))
        mocker.patch.object(resources.BaseResource, "_get_remote_resource", mocker.Mock(return_value=False))
        mocker.patch.object(resources, "hash_config")
        resource = resources.BaseResource(mock_api_client, "workspace_id", local_configuration, "bar.yaml")
        assert resource.APPLY_PRIORITY == 0
        assert resource.workspace_id == "workspace_id"
        assert resource.local_configuration == local_configuration
        assert resource.configuration_path == "bar.yaml"
        assert resource.api_instance == resource.api.return_value
        resource.api.assert_called_with(mock_api_client)
        assert resource.state == resource._get_state_from_file.return_value
        assert resource.remote_resource == resource._get_remote_resource.return_value
        assert resource.was_created == resource._get_remote_resource.return_value
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

    def test_get_attr(self, resource, local_configuration):
        assert resource.exotic_attribute == local_configuration["exotic_attribute"]
        with pytest.raises(AttributeError):
            resource.wrong_attribute

    def test_search(self, resource):
        search_results = resource._search()
        assert search_results == resource._search_fn.return_value
        resource._search_fn.assert_called_with(resource.api_instance, resource.search_payload, _check_return_type=True)

    @pytest.mark.parametrize(
        "search_results,expected_error,expected_output",
        [
            ([], None, None),
            (["foo"], None, "foo"),
            (["foo", "bar"], resources.DuplicateResourceError, None),
        ],
    )
    def test_get_remote_resource(self, resource, mocker, search_results, expected_error, expected_output):
        mock_search_results = mocker.Mock(return_value=search_results)
        mocker.patch.object(resource, "_search", mocker.Mock(return_value=mocker.Mock(get=mock_search_results)))
        if expected_error is None:
            remote_resource = resource._get_remote_resource()
            assert remote_resource == expected_output
        else:
            with pytest.raises(expected_error):
                remote_resource = resource._get_remote_resource()
        resource._search.return_value.get.assert_called_with("universal_resources", [])

    @pytest.mark.parametrize(
        "state_path_is_file",
        [True, False],
    )
    def test_get_state_from_file(self, mocker, resource, state_path_is_file):
        mocker.patch.object(resources, "os")
        mock_expected_state_path = mocker.Mock(is_file=mocker.Mock(return_value=state_path_is_file))
        mocker.patch.object(resources, "Path", mocker.Mock(return_value=mock_expected_state_path))
        mocker.patch.object(resources, "ResourceState")
        state = resource._get_state_from_file()
        resources.os.path.dirname.assert_called_with(resource.configuration_path)
        resources.os.path.join.assert_called_with(resources.os.path.dirname.return_value, "state.yaml")
        resources.Path.assert_called_with(resources.os.path.join.return_value)
        if state_path_is_file:
            resources.ResourceState.from_file.assert_called_with(mock_expected_state_path)
            assert state == resources.ResourceState.from_file.return_value
        else:
            assert state is None

    @pytest.mark.parametrize(
        "resource_id",
        [None, "foo"],
    )
    def test_resource_id_request_body(self, mocker, resource_id, resource):
        mocker.patch.object(resources.BaseResource, "resource_id", resource_id)
        if resource_id is None:
            with pytest.raises(resources.NonExistingResourceError):
                resource.resource_id_request_body
                resource.ResourceIdRequestBody.assert_not_called()
        else:
            assert resource.resource_id_request_body == resource.ResourceIdRequestBody.return_value
            resource.ResourceIdRequestBody.assert_called_with(resource_id)

    @pytest.mark.parametrize(
        "was_created",
        [True, False],
    )
    def test_get_diff_with_remote_resource(self, patch_base_class, mocker, mock_api_client, local_configuration, was_created):
        mocker.patch.object(resources.BaseResource, "_get_comparable_configuration")
        mocker.patch.object(resources.BaseResource, "was_created", was_created)
        resource = resources.BaseResource(mock_api_client, "workspace_id", local_configuration, "bar.yaml")
        mocker.patch.object(resources, "compute_diff")
        if was_created:
            diff = resource.get_diff_with_remote_resource()
            resources.compute_diff.assert_called_with(resource._get_comparable_configuration.return_value, resource.configuration)
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
        resources.ResourceState.create.assert_called_with(resource.configuration_path, resource.local_configuration, "resource_id")

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

    @pytest.mark.parametrize(
        "was_created",
        [True, False],
    )
    def test_get_comparable_configuration(self, patch_base_class, mocker, mock_api_client, local_configuration, was_created):
        mocker.patch.object(resources.BaseResource, "was_created", was_created)
        mocker.patch.object(resources.BaseResource, "remote_resource")
        resource = resources.BaseResource(mock_api_client, "workspace_id", local_configuration, "bar.yaml")
        if not was_created:
            with pytest.raises(resources.NonExistingResourceError):
                resource._get_comparable_configuration()
        else:
            assert resource._get_comparable_configuration() == resource.remote_resource


class TestSource:
    @pytest.mark.parametrize(
        "state",
        [None, resources.ResourceState("config_path", "resource_id", 123, "abc")],
    )
    def test_init(self, mocker, mock_api_client, local_configuration, state):
        assert resources.Source.__base__ == resources.BaseResource
        mocker.patch.object(resources.Source, "resource_id", "foo")
        source = resources.Source(mock_api_client, "workspace_id", local_configuration, "bar.yaml")
        mocker.patch.object(source, "state", state)
        assert source.api == resources.source_api.SourceApi
        assert source.create_function_name == "create_source"
        assert source.resource_id_field == "source_id"
        assert source.search_function_name == "search_sources"
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
            assert source.search_payload == resources.SourceSearch(
                source_definition_id=source.definition_id, workspace_id=source.workspace_id, name=source.resource_name
            )
        else:
            assert source.search_payload == resources.SourceSearch(
                source_definition_id=source.definition_id, workspace_id=source.workspace_id, source_id=source.state.resource_id
            )

    def test_get_comparable_configuration(self, mocker, mock_api_client, local_configuration):
        mock_base_comparable_configuration = mocker.Mock()
        mocker.patch.object(resources.BaseResource, "_get_comparable_configuration", mock_base_comparable_configuration)
        mocker.patch.object(resources.Source, "was_created", True)
        mocker.patch.object(resources.Source, "remote_resource")

        resource = resources.Source(mock_api_client, "workspace_id", local_configuration, "bar.yaml")
        assert resource._get_comparable_configuration() == mock_base_comparable_configuration.return_value.connection_configuration

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
        source.api_instance.discover_schema_for_source.assert_called_with(
            source.source_discover_schema_request_body, _check_return_type=False
        )


class TestDestination:
    @pytest.mark.parametrize(
        "state",
        [None, resources.ResourceState("config_path", "resource_id", 123, "abc")],
    )
    def test_init(self, mocker, mock_api_client, local_configuration, state):
        assert resources.Destination.__base__ == resources.BaseResource
        mocker.patch.object(resources.Destination, "resource_id", "foo")
        destination = resources.Destination(mock_api_client, "workspace_id", local_configuration, "bar.yaml")
        mocker.patch.object(destination, "state", state)
        assert destination.api == resources.destination_api.DestinationApi
        assert destination.create_function_name == "create_destination"
        assert destination.resource_id_field == "destination_id"
        assert destination.search_function_name == "search_destinations"
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
            assert destination.search_payload == resources.DestinationSearch(
                destination_definition_id=destination.definition_id, workspace_id=destination.workspace_id, name=destination.resource_name
            )
        else:
            assert destination.search_payload == resources.DestinationSearch(
                destination_definition_id=destination.definition_id,
                workspace_id=destination.workspace_id,
                destination_id=destination.state.resource_id,
            )

    def test_get_comparable_configuration(self, mocker, mock_api_client, local_configuration):
        mock_base_comparable_configuration = mocker.Mock()
        mocker.patch.object(resources.BaseResource, "_get_comparable_configuration", mock_base_comparable_configuration)
        mocker.patch.object(resources.Destination, "was_created", True)
        mocker.patch.object(resources.Destination, "remote_resource")

        resource = resources.Destination(mock_api_client, "workspace_id", local_configuration, "bar.yaml")
        assert resource._get_comparable_configuration() == mock_base_comparable_configuration.return_value.connection_configuration


class TestConnection:
    @pytest.fixture
    def connection_configuration(self):
        return {
            "definition_type": "connection",
            "resource_name": "my_connection",
            "source_id": "my_source",
            "destination_id": "my_destination",
            "configuration": {
                "sourceId": "my_source",
                "destinationId": "my_destination",
                "namespaceDefinition": "customformat",
                "namespaceFormat": "foo",
                "prefix": "foo",
                "syncCatalog": {
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
                "schedule": {"units": 1, "time_units": "days"},
                "status": "active",
                "resourceRequirements": {"cpu_request": "foo", "cpu_limit": "foo", "memory_request": "foo", "memory_limit": "foo"},
            },
        }

    @pytest.mark.parametrize(
        "state",
        [None, resources.ResourceState("config_path", "resource_id", 123, "abc")],
    )
    def test_init(self, mocker, mock_api_client, state, connection_configuration):
        assert resources.Connection.__base__ == resources.BaseResource
        mocker.patch.object(resources.Connection, "resource_id", "foo")
        connection = resources.Connection(mock_api_client, "workspace_id", connection_configuration, "bar.yaml")
        mocker.patch.object(connection, "state", state)
        assert connection.api == resources.connection_api.ConnectionApi
        assert connection.create_function_name == "create_connection"
        assert connection.resource_id_field == "connection_id"
        assert connection.search_function_name == "search_connections"
        assert connection.update_function_name == "update_connection"
        assert connection.resource_type == "connection"
        assert connection.APPLY_PRIORITY == 1

        assert connection.create_payload == resources.ConnectionCreate(
            **connection.configuration, _check_type=False, _spec_property_naming=True
        )
        assert connection.update_payload == resources.ConnectionUpdate(
            connection_id=connection.resource_id,
            sync_catalog=connection.configuration["syncCatalog"],
            status=connection.configuration["status"],
            namespace_definition=connection.configuration["namespaceDefinition"],
            namespace_format=connection.configuration["namespaceFormat"],
            prefix=connection.configuration["prefix"],
            schedule=connection.configuration["schedule"],
            resource_requirements=connection.configuration["resourceRequirements"],
            _check_type=False,
        )
        if state is None:
            assert connection.search_payload == resources.ConnectionSearch(
                source_id=connection.source_id,
                destination_id=connection.destination_id,
                name=connection.resource_name,
                status=resources.ConnectionStatus(
                    connection_configuration["configuration"]["status"],
                ),
            )
        else:
            assert connection.search_payload == resources.ConnectionSearch(
                connection_id=connection.state.resource_id, source_id=connection.source_id, destination_id=connection.destination_id
            )

    def test_get_comparable_configuration(self, mocker, mock_api_client, connection_configuration):
        mock_base_comparable_configuration = mocker.Mock(
            return_value={"foo": "bar", "connectionId": "should be popped", "operationIds": "should be popped"}
        )
        mocker.patch.object(resources.BaseResource, "_get_comparable_configuration", mock_base_comparable_configuration)
        mocker.patch.object(resources.Connection, "was_created", True)
        mocker.patch.object(resources.Connection, "remote_resource")

        resource = resources.Connection(mock_api_client, "workspace_id", connection_configuration, "bar.yaml")
        assert resource._get_comparable_configuration() == {"foo": "bar"}

    def test__search(self, mocker, mock_api_client, connection_configuration):
        resource = resources.Connection(mock_api_client, "workspace_id", connection_configuration, "bar.yaml")
        mocker.patch.object(resource, "_search_fn")
        search_results = resource._search()
        assert search_results == resource._search_fn.return_value
        resource._search_fn.assert_called_with(resource.api_instance, resource.search_payload, _check_return_type=False)

    def test_create(self, mocker, mock_api_client, connection_configuration):
        mocker.patch.object(resources.Connection, "_create_or_update")
        resource = resources.Connection(mock_api_client, "workspace_id", connection_configuration, "bar.yaml")
        create_result = resource.create()
        assert create_result == resource._create_or_update.return_value
        resource._create_or_update.assert_called_with(resource._create_fn, resource.create_payload, _check_return_type=False)

    def test_update(self, mocker, mock_api_client, connection_configuration):
        mocker.patch.object(resources.Connection, "_create_or_update")
        resource = resources.Connection(mock_api_client, "workspace_id", connection_configuration, "bar.yaml")
        update_result = resource.update()
        assert update_result == resource._create_or_update.return_value
        resource._create_or_update.assert_called_with(resource._update_fn, resource.update_payload, _check_return_type=False)


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
