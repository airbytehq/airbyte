#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_api_client.api import destination_definition_api, source_definition_api
from octavia_cli.list.connectors_definitions import (
    ConnectorsDefinitions,
    DefinitionType,
    DestinationConnectorsDefinitions,
    SourceConnectorsDefinitions,
)


def test_definition_type():
    assert [definition_type.value for definition_type in DefinitionType] == ["source", "destination"]


class TestConnectorsDefinitions:
    @pytest.fixture
    def mock_api(self, mocker):
        return mocker.Mock()

    @pytest.fixture
    def patch_base_class(self, mocker, mock_api):
        # Mock abstract methods to enable instantiating abstract class
        mocker.patch.object(ConnectorsDefinitions, "api", mock_api)
        mocker.patch.object(ConnectorsDefinitions, "__abstractmethods__", set())

    @pytest.fixture
    def connectors_definitions_mock_args(self, mocker):
        return (mocker.Mock(value="my_definition_type"), mocker.Mock(), mocker.Mock())

    def test_init(self, patch_base_class, mock_api, connectors_definitions_mock_args):
        mock_definition_type, mock_api_client, mock_list_latest_definitions = connectors_definitions_mock_args
        definitions = ConnectorsDefinitions(*connectors_definitions_mock_args)
        assert definitions.definition_type == mock_definition_type
        mock_api.assert_called_with(mock_api_client)
        assert definitions.api_instance == mock_api.return_value
        assert definitions.list_latest_definitions == mock_list_latest_definitions

    def test_abstract_methods(self, connectors_definitions_mock_args):
        assert ConnectorsDefinitions.__abstractmethods__ == {"api"}
        with pytest.raises(TypeError):
            ConnectorsDefinitions(*connectors_definitions_mock_args)

    def test_fields_to_display(self, patch_base_class, connectors_definitions_mock_args):
        definitions = ConnectorsDefinitions(*connectors_definitions_mock_args)
        expected_field_to_display = ["name", "dockerRepository", "dockerImageTag", "my_definition_typeDefinitionId"]
        assert definitions.fields_to_display == expected_field_to_display

    def test_response_definition_list_field(self, patch_base_class, connectors_definitions_mock_args):
        definitions = ConnectorsDefinitions(*connectors_definitions_mock_args)
        expected_response_definition_list_field = "my_definition_type_definitions"
        assert definitions.response_definition_list_field == expected_response_definition_list_field

    def test_parse_response(self, patch_base_class, connectors_definitions_mock_args):
        definitions = ConnectorsDefinitions(*connectors_definitions_mock_args)
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

    def test_latest_definitions(self, patch_base_class, mocker, connectors_definitions_mock_args):
        mock_list_latest_definitions = connectors_definitions_mock_args[-1]
        mocker.patch.object(ConnectorsDefinitions, "_parse_response")
        definitions = ConnectorsDefinitions(*connectors_definitions_mock_args)
        assert definitions.latest_definitions == definitions._parse_response.return_value
        mock_list_latest_definitions.assert_called_with(definitions.api_instance, **definitions.LIST_LATEST_DEFINITIONS_KWARGS)
        definitions._parse_response.assert_called_with(mock_list_latest_definitions.return_value)

    def test_repr(self, patch_base_class, mocker, connectors_definitions_mock_args):
        headers = ["fieldA", "fieldB", "fieldC"]
        latest_definitions = [["a", "b", "c"]]
        mocker.patch.object(ConnectorsDefinitions, "fields_to_display", headers)
        mocker.patch.object(ConnectorsDefinitions, "latest_definitions", latest_definitions)
        mocker.patch.object(ConnectorsDefinitions, "_display_as_table")
        mocker.patch.object(ConnectorsDefinitions, "_format_column_names")

        definitions = ConnectorsDefinitions(*connectors_definitions_mock_args)
        representation = definitions.__repr__()
        definitions._display_as_table.assert_called_with([definitions._format_column_names.return_value] + latest_definitions)
        assert representation == definitions._display_as_table.return_value

    @pytest.mark.parametrize(
        "test_data,padding,expected_col_width",
        [([["a", "___10chars"], ["e", "f"]], 2, 2 + 10), ([["a", "___10chars"], ["e", "____11chars"]], 2, 2 + 11), ([[""]], 2, 2)],
    )
    def test_compute_col_width(self, test_data, padding, expected_col_width):
        col_width = ConnectorsDefinitions._compute_col_width(test_data, padding)
        assert col_width == expected_col_width

    @pytest.mark.parametrize(
        "test_data,col_width,expected_output",
        [
            ([["a", "___10chars"], ["e", "____11chars"]], 13, "a            ___10chars   \ne            ____11chars  "),
        ],
    )
    def test_display_as_table(self, mocker, test_data, col_width, expected_output):
        mocker.patch.object(ConnectorsDefinitions, "_compute_col_width", mocker.Mock(return_value=col_width))
        assert ConnectorsDefinitions._display_as_table(test_data) == expected_output

    @pytest.mark.parametrize("input_camelcased,expected_output", [("camelCased", "CAMEL CASED"), ("notcamelcased", "NOTCAMELCASED")])
    def test_camelcased_to_uppercased_spaced(self, input_camelcased, expected_output):
        assert ConnectorsDefinitions._camelcased_to_uppercased_spaced(input_camelcased) == expected_output

    def test_format_column_names(self, mocker):
        columns_to_format = ["camelCased"]
        formatted_columns = ConnectorsDefinitions._format_column_names(columns_to_format)
        assert len(formatted_columns) == 1
        for i, c in enumerate(formatted_columns):
            assert c == ConnectorsDefinitions._camelcased_to_uppercased_spaced(columns_to_format[i])


class TestSubConnectorsDefinitions:
    @pytest.fixture
    def mock_api_client(self, mocker):
        return mocker.Mock()

    @pytest.mark.parametrize(
        "definition_type,SubDefinitionClass,list_latest_definitions",
        [
            (DefinitionType.SOURCE, SourceConnectorsDefinitions, source_definition_api.SourceDefinitionApi.list_latest_source_definitions),
            (
                DefinitionType.DESTINATION,
                DestinationConnectorsDefinitions,
                destination_definition_api.DestinationDefinitionApi.list_latest_destination_definitions,
            ),
        ],
    )
    def test_init(self, mocker, mock_api_client, definition_type, SubDefinitionClass, list_latest_definitions):
        definitions_init = mocker.Mock()
        mocker.patch.object(ConnectorsDefinitions, "__init__", definitions_init)
        SubDefinitionClass(mock_api_client)
        definitions_init.assert_called_with(definition_type, mock_api_client, list_latest_definitions)

    @pytest.mark.parametrize(
        "SubDefinitionClass,expected_api",
        [
            (SourceConnectorsDefinitions, source_definition_api.SourceDefinitionApi),
            (DestinationConnectorsDefinitions, destination_definition_api.DestinationDefinitionApi),
        ],
    )
    def test_class_attributes(self, SubDefinitionClass, expected_api):
        assert SubDefinitionClass.api == expected_api
