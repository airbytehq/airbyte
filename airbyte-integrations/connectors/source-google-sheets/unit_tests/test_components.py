#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import io
import json
from typing import Dict, List, Union
from unittest.mock import Mock, patch

import dpath
import pytest
import requests
from components import (
    DpathSchemaExtractor,
    DpathSchemaMatchingExtractor,
    GridDataErrorHandler,
    RawSchemaParser,
    _sanitization,
)

from airbyte_cdk.connector_builder.connector_builder_handler import resolve_manifest
from airbyte_cdk.sources.declarative.decoders.json_decoder import (
    IterableDecoder,
    JsonDecoder,
)
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from unit_tests.conftest import _YAML_FILE_PATH
from unit_tests.integration.conftest import oauth_credentials


config = {"field": "record_array"}
parameters = {"schema_type_identifier": {"key_pointer": ["formattedValue"], "schema_pointer": ["values"]}}

decoder_json = JsonDecoder(parameters={})
decoder_iterable = IterableDecoder(parameters={})


def create_response(body: Union[Dict, bytes]):
    response = requests.Response()
    response.raw = io.BytesIO(body if isinstance(body, bytes) else json.dumps(body).encode("utf-8"))
    return response


_CONFIG = {"spreadsheet_id": "_spread_sheet_id", "credentials": oauth_credentials, "batch_size": 200}
_MANIFEST = resolve_manifest(source=YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), config=_CONFIG, state=[])).record.data[
    "manifest"
]
_FIELD_PATH = list(
    dpath.get(
        obj=_MANIFEST,
        glob=["dynamic_streams", 0, "stream_template", "schema_loader", "retriever", "record_selector", "extractor", "field_path"],
        default=[],
    )
)
_SCHEMA_TYPE_IDENTIFIERS = dpath.get(obj=_MANIFEST, glob=["definitions", "schema_type_identifier"])


@pytest.mark.parametrize(
    "body, expected_records",
    [
        (
            {
                "sheets": [
                    {"data": [{"rowData": [{"values": [{"formattedValue": "h1"}, {"formattedValue": "h2"}, {"formattedValue": "h3"}]}]}]}
                ]
            },
            [{"values": [{"formattedValue": "h1"}, {"formattedValue": "h2"}, {"formattedValue": "h3"}]}],
        ),
        (
            {
                "sheets": [
                    {"data": [{"rowData": [{"values": [{"formattedValue": "h1"}, {"formattedValue": "h1"}, {"formattedValue": "h3"}]}]}]}
                ]
            },
            [{"values": [{"formattedValue": "h1_A1"}, {"formattedValue": "h1_B1"}, {"formattedValue": "h3"}]}],
        ),
        (
            {
                "sheets": [
                    {"data": [{"rowData": [{"values": [{"formattedValue": "h1"}, {"formattedValue": "h3"}, {"formattedValue": "h3"}]}]}]}
                ]
            },
            [{"values": [{"formattedValue": "h1"}, {"formattedValue": "h3_B1"}, {"formattedValue": "h3_C1"}]}],
        ),
        (
            {
                "sheets": [
                    {"data": [{"rowData": [{"values": [{"formattedValue": "h1"}, {"formattedValue": ""}, {"formattedValue": "h3"}]}]}]}
                ]
            },
            [{"values": [{"formattedValue": "h1"}]}],
        ),
        (
            {"sheets": [{"data": [{"rowData": [{"values": [{"formattedValue": ""}, {"formattedValue": ""}, {"formattedValue": ""}]}]}]}]},
            [{"values": []}],
        ),
    ],
    ids=[
        "test_headers",
        "test_duplicate_headers_retrieved",
        "test_duplicate_headers_retrieved_not_first_position",
        "test_blank_values_terminate_row",
        "test_is_row_empty_with_empty_row",
    ],
)
def test_dpath_schema_extractor(body, expected_records: List):
    extractor = DpathSchemaExtractor(field_path=_FIELD_PATH, config=config, decoder=decoder_json, parameters=parameters)

    response = create_response(body)
    actual_records = list(extractor.extract_records(response))

    assert actual_records == expected_records


@pytest.mark.parametrize(
    "raw_schema_data, expected_data",
    [
        (
            {"values": [{"formattedValue": "h1"}, {"formattedValue": "h2"}, {"formattedValue": "h3"}]},
            [(0, "h1", {"formattedValue": "h1"}), (1, "h2", {"formattedValue": "h2"}), (2, "h3", {"formattedValue": "h3"})],
        ),
        (
            {"values": [{"formattedValue": "h1"}, {"formattedValue": "h1"}, {"formattedValue": "h3"}]},
            [(0, "h1_A1", {"formattedValue": "h1"}), (1, "h1_B1", {"formattedValue": "h1"}), (2, "h3", {"formattedValue": "h3"})],
        ),
        (
            {"values": [{"formattedValue": "h1"}, {"formattedValue": "h3"}, {"formattedValue": "h3"}]},
            [(0, "h1", {"formattedValue": "h1"}), (1, "h3_B1", {"formattedValue": "h3"}), (2, "h3_C1", {"formattedValue": "h3"})],
        ),
        ({"values": [{"formattedValue": "h1"}, {"formattedValue": ""}, {"formattedValue": "h3"}]}, [(0, "h1", {"formattedValue": "h1"})]),
        ({"values": [{"formattedValue": ""}, {"formattedValue": ""}, {"formattedValue": ""}]}, []),
        (
            {"values": [{"formattedValue": "h1"}, {"formattedValue": "   "}, {"formattedValue": "h3"}]},
            [(0, "h1", {"formattedValue": "h1"})],
        ),
    ],
    ids=[
        "test_headers",
        "test_duplicate_headers_retrieved",
        "test_duplicate_headers_retrieved_not_first_position",
        "test_blank_values_terminate_row",
        "test_is_row_empty_with_empty_row",
        "test_whitespace_terminates_row",
    ],
)
def test_parse_raw_schema_value(raw_schema_data, expected_data):
    extractor = RawSchemaParser()
    parsed_data = extractor.parse_raw_schema_values(
        raw_schema_data,
        schema_pointer=_SCHEMA_TYPE_IDENTIFIERS["schema_pointer"],
        key_pointer=_SCHEMA_TYPE_IDENTIFIERS["key_pointer"],
        names_conversion=False,
    )
    assert parsed_data == expected_data


@pytest.mark.parametrize(
    "raw_schema_data, expected_data",
    [
        pytest.param(
            {"values": [{"formattedValue": "h1"}, {"formattedValue": ""}, {"formattedValue": "h3"}]},
            [(0, "h1", {"formattedValue": "h1"}), (1, "column_B", {"formattedValue": ""}), (2, "h3", {"formattedValue": "h3"})],
            id="blank_header_in_middle_generates_placeholder",
        ),
        pytest.param(
            {"values": [{"formattedValue": "h1"}, {"formattedValue": "   "}, {"formattedValue": "h3"}]},
            [(0, "h1", {"formattedValue": "h1"}), (1, "column_B", {"formattedValue": "   "}), (2, "h3", {"formattedValue": "h3"})],
            id="whitespace_header_generates_placeholder",
        ),
        pytest.param(
            {"values": [{"formattedValue": ""}, {"formattedValue": ""}, {"formattedValue": "h3"}]},
            [(0, "column_A", {"formattedValue": ""}), (1, "column_B", {"formattedValue": ""}), (2, "h3", {"formattedValue": "h3"})],
            id="multiple_blank_headers_generate_placeholders",
        ),
        pytest.param(
            {"values": [{"formattedValue": ""}, {"formattedValue": ""}, {"formattedValue": ""}]},
            [(0, "column_A", {"formattedValue": ""}), (1, "column_B", {"formattedValue": ""}), (2, "column_C", {"formattedValue": ""})],
            id="all_blank_headers_generate_placeholders",
        ),
        pytest.param(
            {
                "values": [
                    {"formattedValue": "columnA"},
                    {"formattedValue": "columnB"},
                    {"formattedValue": ""},
                    {"formattedValue": "columnD"},
                ]
            },
            [
                (0, "columnA", {"formattedValue": "columnA"}),
                (1, "columnB", {"formattedValue": "columnB"}),
                (2, "column_C", {"formattedValue": ""}),
                (3, "columnD", {"formattedValue": "columnD"}),
            ],
            id="empty_header_does_not_skip_subsequent_columns",
        ),
    ],
)
def test_parse_raw_schema_value_with_read_empty_header_columns_enabled(raw_schema_data, expected_data):
    """Test that when read_empty_header_columns is enabled, empty headers get placeholder names."""
    extractor = RawSchemaParser()
    extractor.config = {"read_empty_header_columns": True}
    parsed_data = extractor.parse_raw_schema_values(
        raw_schema_data,
        schema_pointer=_SCHEMA_TYPE_IDENTIFIERS["schema_pointer"],
        key_pointer=_SCHEMA_TYPE_IDENTIFIERS["key_pointer"],
        names_conversion=False,
    )
    assert parsed_data == expected_data


@pytest.mark.parametrize(
    "values, expected_response",
    [([" ", "", "     "], True), ([" ", "", "     ", "some_value_here"], False)],
    ids=["with_empty_row", "with_full_row"],
)
def test_is_row_empty(values, expected_response):
    is_row_empty = DpathSchemaMatchingExtractor.is_row_empty(values)
    assert is_row_empty == expected_response


@pytest.mark.parametrize(
    "values, relevant_indices, expected_response",
    [(["c1", "c2", "c3"], [2], True), (["", "", "c3"], [0, 1], False)],
    ids=["is_true", "is_false"],
)
def test_row_contains_relevant_data(values, relevant_indices, expected_response):
    is_row_empty = DpathSchemaMatchingExtractor.row_contains_relevant_data(values, relevant_indices)
    assert is_row_empty == expected_response


@pytest.mark.parametrize(
    "values, expected_response",
    [([" ", "", "     "], True), ([" ", "", "     ", "some_value_here"], False)],
    ids=["with_empty_row", "with_full_row"],
)
def test_is_row_empty(values, expected_response):
    is_row_empty = DpathSchemaMatchingExtractor.is_row_empty(values)
    assert is_row_empty == expected_response


@pytest.mark.parametrize(
    "values, relevant_indices, expected_response",
    [(["c1", "c2", "c3"], [2], True), (["", "", "c3"], [0, 1], False)],
    ids=["is_true", "is_false"],
)
def test_row_contains_relevant_data(values, relevant_indices, expected_response):
    is_row_empty = DpathSchemaMatchingExtractor.row_contains_relevant_data(values, relevant_indices)
    assert is_row_empty == expected_response


# Tests for _sanitization
def test_remove_leading_trailing_underscores():
    assert _sanitization(" EXAMPLE Domain ", remove_leading_trailing_underscores=True) == "example_domain"


def test_remove_special_characters():
    assert _sanitization("Example ID*", remove_special_characters=True) == "example_id"


def test_combine_number_word_pairs():
    assert _sanitization("50th Percentile", combine_number_word_pairs=True) == "_50th_percentile"


def test_combine_letter_number_pairs():
    assert _sanitization("Q3 2023", combine_letter_number_pairs=True) == "q3_2023"


def test_allow_leading_numbers():
    assert _sanitization("50th Percentile", allow_leading_numbers=True, combine_number_word_pairs=True) == "50th_percentile"


def test_combined_flags():
    assert (
        _sanitization(
            " Example ID*",
            remove_leading_trailing_underscores=True,
            remove_special_characters=True,
        )
        == "example_id"
    )


def test_all_flags():
    assert (
        _sanitization(
            "  23Full1st(1)test 123aaa     *! ",
            remove_leading_trailing_underscores=True,
            remove_special_characters=True,
            combine_number_word_pairs=True,
            combine_letter_number_pairs=True,
            allow_leading_numbers=True,
        )
        == "23full_1st_1test_123aaa"
    )


def test_multiple_consecutive_special_characters():
    assert _sanitization("a!!b", remove_special_characters=False) == "a_b"
    assert _sanitization("a!!b", remove_special_characters=True) == "ab"


def test_starting_with_number():
    assert _sanitization("123abc", allow_leading_numbers=False) == "_123_abc"
    assert _sanitization("123abc", allow_leading_numbers=True) == "123_abc"


def test_mixed_case_and_special_characters():
    assert _sanitization("Test_Name!123", remove_special_characters=False) == "test_name_123"
    assert _sanitization("Test_Name!123", remove_special_characters=True) == "test_name_123"


def test_leading_special_characters():
    assert _sanitization("*M1k", remove_special_characters=False, combine_letter_number_pairs=True) == "_m1_k"
    assert _sanitization("*M1k", remove_special_characters=True, combine_letter_number_pairs=True) == "m1_k"


def test_trailing_special_characters():
    assert _sanitization("M1k*", remove_special_characters=False, combine_letter_number_pairs=True) == "m1_k_"
    assert _sanitization("M1k*", remove_special_characters=True, combine_letter_number_pairs=True) == "m1_k"


def test_multiple_flags_with_special_characters():
    assert (
        _sanitization(
            "  *50th Percentile! ",
            remove_leading_trailing_underscores=True,
            remove_special_characters=True,
            combine_number_word_pairs=True,
            allow_leading_numbers=True,
        )
        == "50th_percentile"
    )


def test_dpath_schema_matching_extractor_without_properties_to_match():
    """
    Test that DpathSchemaMatchingExtractor can be instantiated without the
    "properties_to_match" parameter in cases where it is not provided.
    """
    parameters_without_properties = {
        "values_to_match_key": "values",
        "schema_type_identifier": {"key_pointer": ["formattedValue"], "schema_pointer": ["values"]},
    }

    # This should not raise an exception
    extractor = DpathSchemaMatchingExtractor(
        field_path=_FIELD_PATH, config=config, decoder=decoder_json, parameters=parameters_without_properties
    )

    # Verify that the extractor was created successfully
    assert extractor is not None
    assert extractor._values_to_match_key == "values"
    assert extractor._indexed_properties_to_match == {}


@pytest.mark.parametrize(
    "alt_status_code, expected_action, expected_message",
    [
        (200, "IGNORE", "Skipping sheet 'TestSheet' due to corrupt grid data"),
        (500, "RETRY", "Internal server error encountered. Retrying with backoff."),
    ],
    ids=["alt_200_ignore", "alt_500_retry"],
)
@patch("components.requests.get")
@patch("components.logger")
def test_grid_data_error_handler_500_filter(mock_logger, mock_requests_get, alt_status_code, expected_action, expected_message):
    """Test Filter 3: grid_data_500 handling in GridDataErrorHandler.

    When a 500 error occurs with includeGridData=true, the handler immediately tests
    with includeGridData=false to determine if it's corrupt grid data or a genuine server error.
    """
    # Create handler
    handler = GridDataErrorHandler(config={}, parameters={"max_retries": 5})

    # Create mock response for 500 error with grid data
    mock_response = create_response({})
    mock_response.status_code = 500
    mock_response.request = Mock()
    mock_response.request.url = "https://sheets.googleapis.com/v4/spreadsheets/test?includeGridData=true&ranges=TestSheet!1:1"
    mock_response.request.headers = {"Authorization": "Bearer test"}
    mock_response.json = Mock(return_value={"error": "Internal Server Error"})

    # Mock the alt response for the test without grid data
    mock_alt_response = Mock()
    mock_alt_response.status_code = alt_status_code
    mock_requests_get.return_value = mock_alt_response

    # Call interpret_response - it should immediately test without grid data
    resolution = handler.interpret_response(mock_response)

    # Verify the alt request was made immediately
    mock_requests_get.assert_called_once_with(
        "https://sheets.googleapis.com/v4/spreadsheets/test?includeGridData=false&ranges=TestSheet!1:1",
        headers={"Authorization": "Bearer test"},
        timeout=30,
    )

    # Check the result based on alt_status_code
    assert resolution.response_action.name == expected_action
    assert expected_message in resolution.error_message

    # Verify appropriate logging
    if alt_status_code == 200:
        # Corrupt grid data case - should log warning
        mock_logger.warning.assert_called_once()
        assert "corrupt or incompatible grid data" in mock_logger.warning.call_args[0][0]
    else:
        # Genuine server error case - should log info about retrying
        mock_logger.info.assert_called()
        # Check that one of the info calls mentions the failure
        info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any("also failed" in msg for msg in info_calls)
