#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_api_client.api import connection_api, destination_api, destination_definition_api, source_api, source_definition_api
from octavia_cli.list import listings
from octavia_cli.list.listings import (
    BaseListing,
    Connections,
    DestinationConnectorsDefinitions,
    Destinations,
    SourceConnectorsDefinitions,
    Sources,
    WorkspaceListing,
)


class TestBaseListing:
    @pytest.fixture
    def patch_base_class(self, mocker):
        # Mock abstract methods to enable instantiating abstract class
        mocker.patch.object(BaseListing, "__abstractmethods__", set())
        mocker.patch.object(BaseListing, "list_function_name", "my_list_function_name")
        mocker.patch.object(BaseListing, "api", mocker.Mock(my_list_function_name=mocker.Mock()))

    def test_init(self, patch_base_class, mock_api_client):
        base_listing = BaseListing(mock_api_client)
        assert base_listing._list_fn == BaseListing.api.my_list_function_name
        assert base_listing.list_function_kwargs == {}
        assert base_listing.api_instance == base_listing.api.return_value
        base_listing.api.assert_called_with(mock_api_client)
        assert base_listing.COMMON_LIST_FUNCTION_KWARGS == {"_check_return_type": False}

    def test_abstract_methods(self, mock_api_client):
        assert BaseListing.__abstractmethods__ == {"api", "fields_to_display", "list_field_in_response", "list_function_name"}
        with pytest.raises(TypeError):
            BaseListing(mock_api_client)

    def test_parse_response(self, patch_base_class, mocker, mock_api_client):
        mocker.patch.object(BaseListing, "fields_to_display", ["fieldA", "fieldB"])
        base_listing = BaseListing(mock_api_client)
        api_response = {base_listing.list_field_in_response: []}
        for i in range(5):
            definition = {field: f"{field}_value_{i}" for field in base_listing.fields_to_display}
            definition["discarded_field"] = "discarded_value"
            api_response[base_listing.list_field_in_response].append(definition)
        parsed_listing = base_listing._parse_response(api_response)
        assert len(parsed_listing) == 5
        for i in range(5):
            assert parsed_listing[i] == [f"{field}_value_{i}" for field in base_listing.fields_to_display]
            assert "discarded_value" not in parsed_listing[i]

    def test_gest_listing(self, patch_base_class, mocker, mock_api_client):
        mocker.patch.object(BaseListing, "_parse_response")
        mocker.patch.object(BaseListing, "_list_fn")
        base_listing = BaseListing(mock_api_client)
        listing = base_listing.get_listing()
        base_listing._list_fn.assert_called_with(
            base_listing.api_instance, **base_listing.list_function_kwargs, **base_listing.COMMON_LIST_FUNCTION_KWARGS
        )
        base_listing._parse_response.assert_called_with(base_listing._list_fn.return_value)
        assert listing == base_listing._parse_response.return_value

    def test_repr(self, patch_base_class, mocker, mock_api_client):
        headers = ["fieldA", "fieldB", "fieldC"]
        api_response_listing = [["a", "b", "c"]]
        mocker.patch.object(BaseListing, "fields_to_display", headers)
        mocker.patch.object(BaseListing, "get_listing", mocker.Mock(return_value=api_response_listing))
        mocker.patch.object(listings, "formatting")
        base_listing = BaseListing(mock_api_client)
        representation = base_listing.__repr__()
        listings.formatting.display_as_table.assert_called_with(
            [listings.formatting.format_column_names.return_value] + api_response_listing
        )
        assert representation == listings.formatting.display_as_table.return_value


class TestSourceConnectorsDefinitions:
    def test_init(self, mock_api_client):
        assert SourceConnectorsDefinitions.__base__ == BaseListing
        source_connectors_definition = SourceConnectorsDefinitions(mock_api_client)
        assert source_connectors_definition.api == source_definition_api.SourceDefinitionApi
        assert source_connectors_definition.fields_to_display == ["name", "dockerRepository", "dockerImageTag", "sourceDefinitionId"]
        assert source_connectors_definition.list_field_in_response == "source_definitions"
        assert source_connectors_definition.list_function_name == "list_source_definitions"


class TestDestinationConnectorsDefinitions:
    def test_init(self, mock_api_client):
        assert DestinationConnectorsDefinitions.__base__ == BaseListing
        destination_connectors_definition = DestinationConnectorsDefinitions(mock_api_client)
        assert destination_connectors_definition.api == destination_definition_api.DestinationDefinitionApi
        assert destination_connectors_definition.fields_to_display == [
            "name",
            "dockerRepository",
            "dockerImageTag",
            "destinationDefinitionId",
        ]
        assert destination_connectors_definition.list_field_in_response == "destination_definitions"
        assert destination_connectors_definition.list_function_name == "list_destination_definitions"


class TestWorkspaceListing:
    @pytest.fixture
    def patch_base_class(self, mocker):
        # Mock abstract methods to enable instantiating abstract class
        mocker.patch.object(WorkspaceListing, "__abstractmethods__", set())
        mocker.patch.object(WorkspaceListing, "api", mocker.Mock())

    def test_init(self, patch_base_class, mocker, mock_api_client):
        mocker.patch.object(listings, "WorkspaceIdRequestBody")
        mocker.patch.object(BaseListing, "__init__")
        assert WorkspaceListing.__base__ == BaseListing
        sources_and_destinations = WorkspaceListing(mock_api_client, "my_workspace_id")

        assert sources_and_destinations.workspace_id == "my_workspace_id"
        assert sources_and_destinations.list_function_kwargs == {"workspace_id_request_body": listings.WorkspaceIdRequestBody.return_value}
        listings.WorkspaceIdRequestBody.assert_called_with(workspace_id="my_workspace_id")
        BaseListing.__init__.assert_called_with(mock_api_client)

    def test_abstract(self, mock_api_client):
        with pytest.raises(TypeError):
            WorkspaceListing(mock_api_client)


class TestSources:
    def test_init(self, mock_api_client):
        assert Sources.__base__ == WorkspaceListing
        sources = Sources(mock_api_client, "my_workspace_id")
        assert sources.api == source_api.SourceApi
        assert sources.fields_to_display == ["name", "sourceName", "sourceId"]
        assert sources.list_field_in_response == "sources"
        assert sources.list_function_name == "list_sources_for_workspace"


class TestDestinations:
    def test_init(self, mock_api_client):
        assert Destinations.__base__ == WorkspaceListing
        destinations = Destinations(mock_api_client, "my_workspace_id")
        assert destinations.api == destination_api.DestinationApi
        assert destinations.fields_to_display == ["name", "destinationName", "destinationId"]
        assert destinations.list_field_in_response == "destinations"
        assert destinations.list_function_name == "list_destinations_for_workspace"


class TestConnections:
    def test_init(self, mock_api_client):
        assert Connections.__base__ == WorkspaceListing
        connections = Connections(mock_api_client, "my_workspace_id")
        assert connections.api == connection_api.ConnectionApi
        assert connections.fields_to_display == ["name", "connectionId", "status", "sourceId", "destinationId"]
        assert connections.list_field_in_response == "connections"
        assert connections.list_function_name == "list_connections_for_workspace"
