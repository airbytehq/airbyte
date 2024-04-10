#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import os
from typing import Any, Mapping

from source_airtable.schema_helpers import SchemaHelpers


# HELPERS
def load_file(file_name: str) -> Mapping[str, Any]:
    with open(f"{os.path.dirname(__file__)}/{file_name}", "r") as data:
        return json.load(data)


def test_clean_name(field_name_to_cleaned, expected_clean_name):
    assert expected_clean_name == SchemaHelpers.clean_name(field_name_to_cleaned)


def test_get_json_schema(json_response, expected_json_schema):
    json_schema = SchemaHelpers.get_json_schema(json_response["records"][0])
    assert json_schema == expected_json_schema


def test_get_airbyte_stream(table, expected_json_schema):
    stream = SchemaHelpers.get_airbyte_stream(table, expected_json_schema)
    assert stream
    assert stream.name == table
    assert stream.json_schema == expected_json_schema


def test_table_with_formulas():
    table = load_file("sample_table_with_formulas.json")

    stream_schema = SchemaHelpers.get_json_schema(table)

    expected_schema = load_file("expected_schema_for_sample_table.json")
    assert stream_schema == expected_schema
