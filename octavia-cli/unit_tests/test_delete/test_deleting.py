#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_api_client.api import connection_api, destination_api, destination_definition_api, source_api, source_definition_api
from click import ClickException

# connection_api, destination_api, destination_definition_api, source_api, source_definition_api
from octavia_cli.delete import deletings
from octavia_cli.delete.deletings import (  # Connections,; DestinationConnectorsDefinitions,; Destinations,; SourceConnectorsDefinitions,; Sources,
    BaseDeleting,
    Connections,
    DestinationConnectorsDefinitions,
    Destinations,
    FailedToDeleteError,
    SourceConnectorsDefinitions,
    Sources,
)


class TestFailedToDeleteError:
    def test_init(self):
        assert FailedToDeleteError.__base__ == ClickException


class TestBaseDeleting:
    @pytest.fixture
    def patch_base_class(self, mocker):
        # Mock abstract methods to enable instantiating abstract class
        mocker.patch.object(BaseDeleting, "__abstractmethods__", set())
        mocker.patch.object(BaseDeleting, "delete_function_name", "my_delete_function_name")
        mocker.patch.object(BaseDeleting, "api", mocker.Mock(my_delete_function_name=mocker.Mock()))

    def test_init(self, patch_base_class, mock_api_client):
        base_deleting = BaseDeleting(mock_api_client)
        assert base_deleting._delete_fn == BaseDeleting.api.my_delete_function_name
        assert base_deleting.delete_function_kwargs == {}
        assert base_deleting.api_instance == base_deleting.api.return_value
        base_deleting.api.assert_called_with(mock_api_client)
        assert base_deleting.COMMON_DELETE_FUNCTION_KWARGS == {"_check_return_type": False}
        assert base_deleting.id is None

    def test_abstract_methods(self, mock_api_client):
        assert BaseDeleting.__abstractmethods__ == {"api", "delete_function_name"}
        with pytest.raises(TypeError):
            BaseDeleting(mock_api_client)

    def test_deleting(self, patch_base_class, mocker, mock_api_client):
        mocker.patch.object(BaseDeleting, "_delete_fn")
        mocker.patch.object(BaseDeleting, "id", "my_test_id")
        base_deleting = BaseDeleting(mock_api_client)
        deleting = base_deleting.deleting()
        base_deleting._delete_fn.assert_called_with(
            base_deleting.api_instance, **base_deleting.delete_function_kwargs, **base_deleting.COMMON_DELETE_FUNCTION_KWARGS
        )
        assert deleting == "Successfully deleted Airbyte resource with ID: my_test_id"

    def test_deleting_exception(self, patch_base_class, mocker, mock_api_client):
        mocker.patch.object(BaseDeleting, "_delete_fn")
        mocker.patch.object(BaseDeleting, "id", "my_test_id")
        mocker.patch.object(BaseDeleting, "deleting", mocker.Mock(side_effect=[FailedToDeleteError("Error")]))
        with pytest.raises(FailedToDeleteError) as e:
            base_deleting = BaseDeleting(mock_api_client)
            base_deleting.deleting()
            assert e == "Error"

    def test_repr(self, patch_base_class, mocker, mock_api_client):
        api_response_deleting = "Successfully deleted Airbyte resource with ID: my_test_id"
        mocker.patch.object(BaseDeleting, "deleting", mocker.Mock(return_value=api_response_deleting))
        base_deleting = BaseDeleting(mock_api_client)
        representation = base_deleting.__repr__()
        assert representation == api_response_deleting

    def test_repr_exception(self, patch_base_class, mocker, mock_api_client):
        mocker.patch.object(BaseDeleting, "deleting", mocker.Mock(side_effect=[FailedToDeleteError("Error")]))
        base_deleting = BaseDeleting(mock_api_client)
        with pytest.raises(FailedToDeleteError):
            base_deleting.__repr__()


class TestSourceConnectorsDefinitions:
    def test_init(self, mocker, mock_api_client):
        mocker.patch.object(deletings, "SourceDefinitionIdRequestBody")
        mocker.patch.object(BaseDeleting, "__init__")
        assert SourceConnectorsDefinitions.__base__ == BaseDeleting
        source_connectors_definition = SourceConnectorsDefinitions(mock_api_client, "my_source_definition_id")
        assert source_connectors_definition.delete_function_kwargs == {
            "source_definition_id_request_body": deletings.SourceDefinitionIdRequestBody.return_value
        }
        assert source_connectors_definition.api == source_definition_api.SourceDefinitionApi
        assert source_connectors_definition.delete_function_name == "delete_source_definition"
        deletings.SourceDefinitionIdRequestBody.assert_called_with(source_definition_id="my_source_definition_id")
        BaseDeleting.__init__.assert_called_with(mock_api_client)


class TestDestinationConnectorsDefinitions:
    def test_init(self, mocker, mock_api_client):
        mocker.patch.object(deletings, "DestinationDefinitionIdRequestBody")
        mocker.patch.object(BaseDeleting, "__init__")
        assert DestinationConnectorsDefinitions.__base__ == BaseDeleting
        destination_connectors_definition = DestinationConnectorsDefinitions(mock_api_client, "my_destination_definition_id")
        assert destination_connectors_definition.delete_function_kwargs == {
            "destination_definition_id_request_body": deletings.DestinationDefinitionIdRequestBody.return_value
        }
        assert destination_connectors_definition.api == destination_definition_api.DestinationDefinitionApi
        assert destination_connectors_definition.delete_function_name == "delete_destination_definition"
        deletings.DestinationDefinitionIdRequestBody.assert_called_with(destination_definition_id="my_destination_definition_id")
        BaseDeleting.__init__.assert_called_with(mock_api_client)


class TestSources:
    def test_init(self, mocker, mock_api_client):
        mocker.patch.object(deletings, "SourceIdRequestBody")
        mocker.patch.object(BaseDeleting, "__init__")
        assert Sources.__base__ == BaseDeleting
        sources = Sources(mock_api_client, "my_source_id")
        assert sources.delete_function_kwargs == {"source_id_request_body": deletings.SourceIdRequestBody.return_value}
        assert sources.api == source_api.SourceApi
        assert sources.delete_function_name == "delete_source"
        deletings.SourceIdRequestBody.assert_called_with(source_id="my_source_id")
        BaseDeleting.__init__.assert_called_with(mock_api_client)


class TestDestinations:
    def test_init(self, mocker, mock_api_client):
        mocker.patch.object(deletings, "DestinationIdRequestBody")
        mocker.patch.object(BaseDeleting, "__init__")
        assert Destinations.__base__ == BaseDeleting
        destinations = Destinations(mock_api_client, "my_destination_id")
        assert destinations.delete_function_kwargs == {"destination_id_request_body": deletings.DestinationIdRequestBody.return_value}
        assert destinations.api == destination_api.DestinationApi
        assert destinations.delete_function_name == "delete_destination"
        deletings.DestinationIdRequestBody.assert_called_with(destination_id="my_destination_id")
        BaseDeleting.__init__.assert_called_with(mock_api_client)


class TestConnections:
    def test_init(self, mocker, mock_api_client):
        mocker.patch.object(deletings, "ConnectionIdRequestBody")
        mocker.patch.object(BaseDeleting, "__init__")
        assert Connections.__base__ == BaseDeleting
        connections = Connections(mock_api_client, "my_connection_id")
        assert connections.delete_function_kwargs == {"connection_id_request_body": deletings.ConnectionIdRequestBody.return_value}
        assert connections.api == connection_api.ConnectionApi
        assert connections.delete_function_name == "delete_connection"
        deletings.ConnectionIdRequestBody.assert_called_with(connection_id="my_connection_id")
        BaseDeleting.__init__.assert_called_with(mock_api_client)
