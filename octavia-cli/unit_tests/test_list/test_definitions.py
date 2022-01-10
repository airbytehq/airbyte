#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import pytest
from airbyte_api_client.api import destination_definition_api, source_definition_api
from octavia_cli.list.definitions import (
    Definitions,
    DefinitionType,
    DestinationDefinitions,
    SourceDefinitions,
)


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

    def test_abstract_methods(self, mock_definition_type, mock_api_client):
        assert Definitions.__abstractmethods__ == {"api", "latest_definitions"}
        with pytest.raises(TypeError):
            Definitions(mock_definition_type, mock_api_client)

    def test_fields_to_display(self, patch_base_class, mock_definition_type, mock_api_client):
        definitions = Definitions(mock_definition_type, mock_api_client)
        expected_field_to_display = ["name", "docker_repository", "docker_image_tag", "my_definition_type_definition_id"]
        assert definitions.fields_to_display == expected_field_to_display

    def test_response_definition_list_field(self, patch_base_class, mock_definition_type, mock_api_client):
        definitions = Definitions(mock_definition_type, mock_api_client)
        expected_response_definition_list_field = "my_definition_type_definitions"
        assert definitions.response_definition_list_field == expected_response_definition_list_field

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
            assert parsed_definitions[i] == [f"{field}_value_{i}" for field in definitions.fields_to_display]
            assert "discarded_value" not in parsed_definitions[i]

    def test_repr(self, patch_base_class, mocker, mock_definition_type, mock_api_client):
        headers = ["field_a", "field_b", "field_c"]
        latest_definitions = [["a", "b", "c"]]
        mocker.patch.object(Definitions, "fields_to_display", headers)
        mocker.patch.object(Definitions, "latest_definitions", latest_definitions)
        mocker.patch.object(Definitions, "_display_as_table", mocker.Mock())
        definitions = Definitions(mock_definition_type, mock_api_client)
        representation = definitions.__repr__()
        definitions._display_as_table.assert_called_with([[f.upper() for f in headers]] + latest_definitions)
        assert representation == definitions._display_as_table.return_value

    @pytest.mark.parametrize(
        "test_data,padding,expected_col_width",
        [([["a", "___10chars"], ["e", "f"]], 2, 2 + 10), ([["a", "___10chars"], ["e", "____11chars"]], 2, 2 + 11), ([[""]], 2, 2)],
    )
    def test_compute_col_width(self, test_data, padding, expected_col_width):
        col_width = Definitions._compute_col_width(test_data, padding)
        assert col_width == expected_col_width

    @pytest.mark.parametrize(
        "test_data,col_width,expected_output",
        [
            ([["a", "___10chars"], ["e", "____11chars"]], 13, "a            ___10chars   \ne            ____11chars  "),
        ],
    )
    def test_display_as_table(self, mocker, test_data, col_width, expected_output, mock_definition_type, mock_api_client):
        mocker.patch.object(Definitions, "_compute_col_width", mocker.Mock(return_value=col_width))
        assert Definitions._display_as_table(test_data) == expected_output


class TestSubDefinitions:
    @pytest.fixture
    def mock_api_client(self, mocker):
        return mocker.Mock()

    @pytest.mark.parametrize(
        "definition_type,SubDefinitionClass",
        [
            (DefinitionType.SOURCE, SourceDefinitions),
            (DefinitionType.DESTINATION, DestinationDefinitions),
        ],
    )
    def test_init(self, mocker, mock_api_client, definition_type, SubDefinitionClass):
        definitions_init = mocker.Mock()
        mocker.patch.object(Definitions, "__init__", definitions_init)
        SubDefinitionClass(mock_api_client)
        definitions_init.assert_called_with(definition_type, mock_api_client)

    @pytest.mark.parametrize(
        "SubDefinitionClass,expected_api",
        [
            (SourceDefinitions, source_definition_api.SourceDefinitionApi),
            (DestinationDefinitions, destination_definition_api.DestinationDefinitionApi),
        ],
    )
    def test_class_attributes(self, SubDefinitionClass, expected_api):
        assert SubDefinitionClass.api == expected_api

    @pytest.mark.parametrize(
        "SubDefinitionClass,list_latest_fn",
        [
            (SourceDefinitions, "list_latest_source_definitions"),
            (DestinationDefinitions, "list_latest_destination_definitions"),
        ],
    )
    def test_latest_definitions(self, mocker, mock_api_client, SubDefinitionClass, list_latest_fn):
        mocker.patch.object(SubDefinitionClass, "api", mocker.Mock())
        mocker.patch.object(SubDefinitionClass, "_parse_response", mocker.Mock())

        definitions = SubDefinitionClass(mock_api_client)
        definitions.api_instance = mocker.Mock()

        assert definitions.latest_definitions == definitions._parse_response.return_value
        definitions.api.__getattr__(list_latest_fn).assert_called_with(definitions.api_instance)
