#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import io
import json
from typing import Dict, List, Union

import dpath
import pytest
import requests
from source_google_sheets import SourceGoogleSheets
from source_google_sheets.components import DpathSchemaExtractor, DpathSchemaMatchingExtractor
from source_google_sheets.components.extractors import RawSchemaParser

from airbyte_cdk.connector_builder.connector_builder_handler import resolve_manifest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.decoders.json_decoder import (
    IterableDecoder,
    JsonDecoder,
)
from unit_tests.integration.conftest import catalog_helper, oauth_credentials


config = {"field": "record_array"}
parameters = {"schema_type_identifier": {"key_pointer": ["formattedValue"], "schema_pointer": ["values"]}}

decoder_json = JsonDecoder(parameters={})
decoder_iterable = IterableDecoder(parameters={})


def create_response(body: Union[Dict, bytes]):
    response = requests.Response()
    response.raw = io.BytesIO(body if isinstance(body, bytes) else json.dumps(body).encode("utf-8"))
    return response


_CONFIG = {"spreadsheet_id": "_spread_sheet_id", "credentials": oauth_credentials, "batch_size": 200}
_MANIFEST = resolve_manifest(
    source=SourceGoogleSheets(catalog=catalog_helper(SyncMode.full_refresh, "a_stream"), config=_CONFIG, state={})
).record.data["manifest"]
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
            [{"values": [{"formattedValue": "h3"}]}],
        ),
        (
            {
                "sheets": [
                    {"data": [{"rowData": [{"values": [{"formattedValue": "h1"}, {"formattedValue": "h3"}, {"formattedValue": "h3"}]}]}]}
                ]
            },
            [{"values": [{"formattedValue": "h1"}]}],
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
    "raw_schema_data, expected_data, names_conversion, experimental_names_conversion",
    [
        # Basic header handling
        (
            {"values": [{"formattedValue": "h1"}, {"formattedValue": "h2"}, {"formattedValue": "h3"}]},
            [(0, "h1", {"formattedValue": "h1"}), (1, "h2", {"formattedValue": "h2"}), (2, "h3", {"formattedValue": "h3"})],
            False,
            False,
        ),
        # Duplicate headers
        (
            {"values": [{"formattedValue": "h1"}, {"formattedValue": "h1"}, {"formattedValue": "h3"}]},
            [(2, "h3", {"formattedValue": "h3"})],
            False,
            False,
        ),
        (
            {"values": [{"formattedValue": "h1"}, {"formattedValue": "h3"}, {"formattedValue": "h3"}]},
            [(0, "h1", {"formattedValue": "h1"})],
            False,
            False,
        ),
        # Blank values and whitespace
        (
            {"values": [{"formattedValue": "h1"}, {"formattedValue": ""}, {"formattedValue": "h3"}]},
            [(0, "h1", {"formattedValue": "h1"})],
            False,
            False,
        ),
        (
            {"values": [{"formattedValue": ""}, {"formattedValue": ""}, {"formattedValue": ""}]},
            [],
            False,
            False,
        ),
        (
            {"values": [{"formattedValue": "h1"}, {"formattedValue": "   "}, {"formattedValue": "h3"}]},
            [(0, "h1", {"formattedValue": "h1"})],
            False,
            False,
        ),
        # Experimental name conversion: basic case
        (
            {"values": [{"formattedValue": "AMPED Domain "}, {"formattedValue": "50th Percentile"}, {"formattedValue": "Normal Header"}]},
            [
                (0, "amped_domain", {"formattedValue": "AMPED Domain "}),
                (1, "50th_percentile", {"formattedValue": "50th Percentile"}),
                (2, "normal_header", {"formattedValue": "Normal Header"}),
            ],
            False,
            True,
        ),
        # Special characters
        (
            {"values": [{"formattedValue": "Customer ID*"}, {"formattedValue": "Order#"}, {"formattedValue": "Price!"}]},
            [
                (0, "customer_id", {"formattedValue": "Customer ID*"}),
                (1, "order", {"formattedValue": "Order#"}),
                (2, "price", {"formattedValue": "Price!"}),
            ],
            False,
            True,
        ),
        # Leading and trailing spaces
        (
            {"values": [{"formattedValue": "  Leading Space"}, {"formattedValue": "Trailing Space  "}, {"formattedValue": "  Both  "}]},
            [
                (0, "leading_space", {"formattedValue": "  Leading Space"}),
                (1, "trailing_space", {"formattedValue": "Trailing Space  "}),
                (2, "both", {"formattedValue": "  Both  "}),
            ],
            False,
            True,
        ),
        # Consecutive spaces and special characters
        (
            {"values": [{"formattedValue": "Word  ?!"}, {"formattedValue": "Multi   Space"}, {"formattedValue": "@@Item@@"}]},
            [
                (0, "word", {"formattedValue": "Word  ?!"}),
                (1, "multi_space", {"formattedValue": "Multi   Space"}),
                (2, "item", {"formattedValue": "@@Item@@"}),
            ],
            False,
            True,
        ),
        # Letter-number and number-word pairs
        (
            {"values": [{"formattedValue": "Q3 2023"}, {"formattedValue": "A1 Test"}, {"formattedValue": "X9 Data"}]},
            [
                (0, "q3_2023", {"formattedValue": "Q3 2023"}),
                (1, "a1_test", {"formattedValue": "A1 Test"}),
                (2, "x9_data", {"formattedValue": "X9 Data"}),
            ],
            False,
            True,
        ),
        (
            {"values": [{"formattedValue": "50th Percentile"}, {"formattedValue": "1st Place"}, {"formattedValue": "3rd Rank"}]},
            [
                (0, "50th_percentile", {"formattedValue": "50th Percentile"}),
                (1, "1st_place", {"formattedValue": "1st Place"}),
                (2, "3rd_rank", {"formattedValue": "3rd Rank"}),
            ],
            False,
            True,
        ),
        # Edge cases
        (
            {"values": [{"formattedValue": ""}, {"formattedValue": "!!!"}, {"formattedValue": "   "}]},
            [
                (0, "unnamed_column", {"formattedValue": ""}),
                (1, "unnamed_column", {"formattedValue": "!!!"}),
                (2, "unnamed_column", {"formattedValue": "   "}),
            ],
            False,
            True,
        ),
        # Mixed case and non-ASCII characters
        (
            {"values": [{"formattedValue": "Café 2023"}, {"formattedValue": "UserName"}, {"formattedValue": "Äbc Def"}]},
            [
                (0, "cafe_2023", {"formattedValue": "Café 2023"}),
                (1, "username", {"formattedValue": "UserName"}),
                (2, "abc_def", {"formattedValue": "Äbc Def"}),
            ],
            False,
            True,
        ),
    ],
    ids=[
        "test_headers",
        "test_duplicate_headers_retrieved",
        "test_duplicate_headers_retrieved_not_first_position",
        "test_blank_values_terminate_row",
        "test_is_row_empty_with_empty_row",
        "test_whitespace_terminates_row",
        "test_experimental_names_conversion",
        "test_special_characters",
        "test_leading_trailing_spaces",
        "test_consecutive_spaces_special_chars",
        "test_letter_number_pairs",
        "test_number_word_pairs",
        "test_edge_cases",
        "test_mixed_case_non_ascii",
    ],
)
def test_parse_raw_schema_value(raw_schema_data, expected_data, names_conversion, experimental_names_conversion):
    extractor = RawSchemaParser()
    extractor.config = {"names_conversion": names_conversion, "experimental_names_conversion": experimental_names_conversion}
    parsed_data = extractor.parse_raw_schema_values(
        raw_schema_data,
        schema_pointer=_SCHEMA_TYPE_IDENTIFIERS["schema_pointer"],
        key_pointer=_SCHEMA_TYPE_IDENTIFIERS["key_pointer"],
        names_conversion=names_conversion,
        experimental_names_conversion=experimental_names_conversion,
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
