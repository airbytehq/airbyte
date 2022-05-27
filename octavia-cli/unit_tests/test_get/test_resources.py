#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_api_client.api import connection_api, destination_api, source_api
from airbyte_api_client.model.connection_id_request_body import ConnectionIdRequestBody
from airbyte_api_client.model.destination_id_request_body import DestinationIdRequestBody
from airbyte_api_client.model.source_id_request_body import SourceIdRequestBody
from octavia_cli.get.resources import BaseResource, Connection, Destination, Source


class TestBaseResource:
    @pytest.fixture
    def patch_base_class(self, mocker):
        # Mock abstract methods to enable instantiating abstract class
        mocker.patch.object(BaseResource, "__abstractmethods__", set())
        mocker.patch.object(BaseResource, "api", mocker.Mock())
        mocker.patch.object(BaseResource, "get_function_name", "foo")

    def test_init(self, patch_base_class, mock_api_client, mocker):
        base_definition = BaseResource(mock_api_client, "workspace_id", "resource_id")
        assert base_definition.api_instance == base_definition.api.return_value
        base_definition.api.assert_called_with(mock_api_client)
        assert base_definition.get_function_kwargs == {}
        assert base_definition._get_fn == getattr(base_definition.api, base_definition.get_function_name)

    def test_get_config(self, patch_base_class, mock_api_client, mocker):
        assert Source.__base__ == BaseResource

        base_definition = BaseResource(mock_api_client, "workspace_id", "resource_id")
        assert base_definition._get_fn == getattr(base_definition.api, base_definition.get_function_name)


class TestSource:
    def test_init(self, mock_api_client):
        assert Source.__base__ == BaseResource
        source = Source(mock_api_client, "workspace_id", "resource_id")
        assert source.api == source_api.SourceApi
        assert source.get_function_name == "get_source"
        assert source.get_function_kwargs == {"source_id_request_body": SourceIdRequestBody("resource_id")}


class TestDestination:
    def test_init(self, mock_api_client):
        assert Destination.__base__ == BaseResource
        destination = Destination(mock_api_client, "workspace_id", "resource_id")
        assert destination.api == destination_api.DestinationApi
        assert destination.get_function_name == "get_destination"
        assert destination.get_function_kwargs == {"destination_id_request_body": DestinationIdRequestBody("resource_id")}


class TestConnection:
    def test_init(self, mock_api_client):
        assert Connection.__base__ == BaseResource
        connection = Connection(mock_api_client, "workspace_id", "resource_id")
        assert connection.api == connection_api.ConnectionApi
        assert connection.get_function_name == "get_connection"
        assert connection.get_function_kwargs == {"connection_id_request_body": ConnectionIdRequestBody("resource_id")}
