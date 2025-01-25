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
from unit_tests.integration.mock_credentials import oauth_credentials
from unit_tests.integration.protocol_helpers import catalog_helper


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
    "raw_schema_data, expected_data",
    [
        (
            {"values": [{"formattedValue": "h1"}, {"formattedValue": "h2"}, {"formattedValue": "h3"}]},
            [(0, "h1", {"formattedValue": "h1"}), (1, "h2", {"formattedValue": "h2"}), (2, "h3", {"formattedValue": "h3"})],
        ),
        ({"values": [{"formattedValue": "h1"}, {"formattedValue": "h1"}, {"formattedValue": "h3"}]}, [(2, "h3", {"formattedValue": "h3"})]),
        ({"values": [{"formattedValue": "h1"}, {"formattedValue": "h3"}, {"formattedValue": "h3"}]}, [(0, "h1", {"formattedValue": "h1"})]),
        ({"values": [{"formattedValue": "h1"}, {"formattedValue": ""}, {"formattedValue": "h3"}]}, [(0, "h1", {"formattedValue": "h1"})]),
        ({"values": [{"formattedValue": ""}, {"formattedValue": ""}, {"formattedValue": ""}]}, []),
    ],
    ids=[
        "test_headers",
        "test_duplicate_headers_retrieved",
        "test_duplicate_headers_retrieved_not_first_position",
        "test_blank_values_terminate_row",
        "test_is_row_empty_with_empty_row",
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
