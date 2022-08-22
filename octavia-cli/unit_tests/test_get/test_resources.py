#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_api_client.api import destination_api, source_api, web_backend_api
from airbyte_api_client.model.destination_id_request_body import DestinationIdRequestBody
from airbyte_api_client.model.source_id_request_body import SourceIdRequestBody
from airbyte_api_client.model.web_backend_connection_request_body import WebBackendConnectionRequestBody
from octavia_cli.get.resources import BaseResource, Connection, Destination, DuplicateResourceError, ResourceNotFoundError, Source


class TestBaseResource:
    @pytest.fixture
    def patch_base_class(self, mocker):
        # Mock abstract methods to enable instantiating abstract class
        mocker.patch.object(BaseResource, "__abstractmethods__", set())
        mocker.patch.object(BaseResource, "api", mocker.Mock())
        mocker.patch.object(BaseResource, "get_function_name", "get_function_name")
        mocker.patch.object(BaseResource, "get_payload", "get_payload")
        mocker.patch.object(BaseResource, "list_for_workspace_function_name", "list_for_workspace_function_name")
        mocker.patch.object(BaseResource, "name", "fake_resource")

    @pytest.mark.parametrize(
        "resource_id, resource_name, expected_error, expected_error_message",
        [
            ("my_resource_id", None, None, None),
            (None, "my_resource_name", None, None),
            (None, None, ValueError, "resource_id and resource_name keyword arguments can't be both None."),
            ("my_resource_id", "my_resource_name", ValueError, "resource_id and resource_name keyword arguments can't be both set."),
        ],
    )
    def test_init(self, patch_base_class, mock_api_client, resource_id, resource_name, expected_error, expected_error_message):
        if expected_error:
            with pytest.raises(expected_error, match=expected_error_message):
                base_resource = BaseResource(mock_api_client, "workspace_id", resource_id=resource_id, resource_name=resource_name)
        else:
            base_resource = BaseResource(mock_api_client, "workspace_id", resource_id=resource_id, resource_name=resource_name)
            base_resource.api.assert_called_with(mock_api_client)
            assert base_resource.api_instance == base_resource.api.return_value
            assert base_resource.workspace_id == "workspace_id"
            assert base_resource._get_fn == getattr(base_resource.api, base_resource.get_function_name)
            assert base_resource._list_for_workspace_fn == getattr(base_resource.api, base_resource.list_for_workspace_function_name)
            assert base_resource.resource_id == resource_id
            assert base_resource.resource_name == resource_name

    @pytest.mark.parametrize(
        "resource_name, api_response_resources_names, expected_error, expected_error_message",
        [
            ("foo", ["foo", "bar"], None, None),
            ("foo", ["bar", "fooo"], ResourceNotFoundError, "The fake_resource foo was not found in your current Airbyte workspace."),
            (
                "foo",
                ["foo", "foo"],
                DuplicateResourceError,
                "2 fake_resources with the name foo were found in your current Airbyte workspace.",
            ),
        ],
    )
    def test__find_by_resource_name(
        self, mocker, patch_base_class, mock_api_client, resource_name, api_response_resources_names, expected_error, expected_error_message
    ):
        mock_api_response_records = []
        for fake_resource_name in api_response_resources_names:
            mock_api_response_record = mocker.Mock()  # We can't set the mock name on creation as it's a reserved attribute
            mock_api_response_record.name = fake_resource_name
            mock_api_response_records.append(mock_api_response_record)

        mocker.patch.object(
            BaseResource, "_list_for_workspace_fn", mocker.Mock(return_value=mocker.Mock(fake_resources=mock_api_response_records))
        )
        base_resource = BaseResource(mock_api_client, "workspace_id", resource_id=None, resource_name=resource_name)
        if not expected_error:
            found_resource = base_resource._find_by_resource_name()
            assert found_resource.name == resource_name
        if expected_error:
            with pytest.raises(expected_error, match=expected_error_message):
                base_resource._find_by_resource_name()

    def test__find_by_id(self, mocker, patch_base_class, mock_api_client):
        mocker.patch.object(BaseResource, "_get_fn")
        base_resource = BaseResource(mock_api_client, "workspace_id", resource_id="my_resource_id")
        base_resource._find_by_resource_id()
        base_resource._get_fn.assert_called_with(base_resource.api_instance, base_resource.get_payload)

    @pytest.mark.parametrize("resource_id, resource_name", [("my_resource_id", None), (None, "my_resource_name")])
    def test_get_remote_resource(self, mocker, patch_base_class, mock_api_client, resource_id, resource_name):
        mocker.patch.object(BaseResource, "_find_by_resource_id")
        mocker.patch.object(BaseResource, "_find_by_resource_name")
        base_resource = BaseResource(mock_api_client, "workspace_id", resource_id=resource_id, resource_name=resource_name)
        remote_resource = base_resource.get_remote_resource()
        if resource_id is not None:
            base_resource._find_by_resource_id.assert_called_once()
            base_resource._find_by_resource_name.assert_not_called()
            assert remote_resource == base_resource._find_by_resource_id.return_value
        if resource_name is not None:
            base_resource._find_by_resource_id.assert_not_called()
            base_resource._find_by_resource_name.assert_called_once()
            assert remote_resource == base_resource._find_by_resource_name.return_value

    def test_to_json(self, mocker, patch_base_class, mock_api_client):
        mocker.patch.object(
            BaseResource, "get_remote_resource", mocker.Mock(return_value=mocker.Mock(to_dict=mocker.Mock(return_value={"foo": "bar"})))
        )
        base_resource = BaseResource(mock_api_client, "workspace_id", resource_id="my_resource_id")
        json_repr = base_resource.to_json()
        assert json_repr == '{"foo": "bar"}'


class TestSource:
    def test_init(self, mock_api_client):
        assert Source.__base__ == BaseResource
        source = Source(mock_api_client, "workspace_id", "resource_id")
        assert source.api == source_api.SourceApi
        assert source.get_function_name == "get_source"
        assert source.list_for_workspace_function_name == "list_sources_for_workspace"
        assert source.get_payload == SourceIdRequestBody("resource_id")


class TestDestination:
    def test_init(self, mock_api_client):
        assert Destination.__base__ == BaseResource
        destination = Destination(mock_api_client, "workspace_id", "resource_id")
        assert destination.api == destination_api.DestinationApi
        assert destination.get_function_name == "get_destination"
        assert destination.list_for_workspace_function_name == "list_destinations_for_workspace"
        assert destination.get_payload == DestinationIdRequestBody("resource_id")


class TestConnection:
    def test_init(self, mock_api_client):
        assert Connection.__base__ == BaseResource
        connection = Connection(mock_api_client, "workspace_id", "resource_id")
        assert connection.api == web_backend_api.WebBackendApi
        assert connection.get_function_name == "web_backend_get_connection"
        assert connection.list_for_workspace_function_name == "web_backend_list_connections_for_workspace"
        assert connection.get_payload == WebBackendConnectionRequestBody(with_refreshed_catalog=False, connection_id=connection.resource_id)
