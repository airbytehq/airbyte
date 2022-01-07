#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import pytest
from octavia_cli.list.definitions import Definitions, DefinitionType


def test_definition_type():
    assert [definition_type.value for definition_type in DefinitionType] == ["source", "destination"]


class TestDefinitions:
    @pytest.fixture
    def mock_api(self, mocker):
        return mocker.Mock()

    @pytest.fixture
    def patch_base_class(self, mocker, mock_api):
        # Mock abstract methods to enable instantiating abstract class
        mocker.patch.object(Definitions, "api", mock_api)
        mocker.patch.object(Definitions, "__abstractmethods__", set())

    @pytest.fixture
    def mock_definition_type(self, mocker):
        return mocker.Mock(value="my_definition_type")

    @pytest.fixture
    def mock_api_client(self, mocker):
        return mocker.Mock()

    def test_init(self, patch_base_class, mock_api, mock_definition_type, mock_api_client):
        definitions = Definitions(mock_definition_type, mock_api_client)
        assert definitions.definition_type == mock_definition_type
        mock_api.assert_called_with(mock_api_client)
        assert definitions.api_instance == mock_api.return_value

    def test_fields_to_display(self, patch_base_class, mock_definition_type, mock_api_client):
        definitions = Definitions(mock_definition_type, mock_api_client)
        expected_field_to_display = ["name", "docker_repository", "docker_image_tag", "my_definition_type_definition_id"]
        assert definitions.fields_to_display == expected_field_to_display

    def test_response_definition_list_field(self, patch_base_class, mock_definition_type, mock_api_client):
        definitions = Definitions(mock_definition_type, mock_api_client)
        expected_response_definition_list_field = "my_definition_type_definitions"
        assert definitions.response_definition_list_field == expected_response_definition_list_field

    def test_latest_definitions(self, patch_base_class, mock_definition_type, mock_api_client, mocker):
        mock_list_latest_definitions = mocker.Mock()
        mocker.patch.object(Definitions, "list_latest_definitions", mock_list_latest_definitions)
        definitions = Definitions(mock_definition_type, mock_api_client)
        latest_definitions = definitions.latest_definitions
        mock_list_latest_definitions.assert_called_with(definitions.api_instance)
        assert latest_definitions == mock_list_latest_definitions.return_value

    def test_parse_response(self, patch_base_class, mock_definition_type, mock_api_client):
        definitions = Definitions(mock_definition_type, mock_api_client)
        api_response = {definitions.response_definition_list_field: []}
        for i in range(5):
            definition = {field: f"{field}_value_{i}" for field in definitions.fields_to_display}
            definition["discarded_field"] = "discarded_value"
            api_response[definitions.response_definition_list_field].append(definition)
        parsed_definitions = definitions._parse_response(api_response)
        assert len(parsed_definitions) == 5
        for i in range(5):
            assert parsed_definitions[i] == {field: f"{field}_value_{i}" for field in definitions.fields_to_display}
            assert "discarded_value" not in parsed_definitions[i]
