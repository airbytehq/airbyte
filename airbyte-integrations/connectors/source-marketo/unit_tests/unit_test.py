#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import pytest
from source_marketo.utils import clean_string, format_value

test_data = [
    (1, {"type": "integer"}, int),
    ("string", {"type": "string"}, str),
    (True, {"type": ["boolean", "null"]}, bool),
    (1, {"type": ["number", "null"]}, float),
]


@pytest.mark.parametrize("value,schema,expected_output_type", test_data)
def test_fromat_value(value, schema, expected_output_type):
    test = format_value(value, schema)

    assert isinstance(test, expected_output_type)


test_data = [
    ("updatedAt", "updated_at"),
    ("UpdatedAt", "updated_at"),
    ("base URL", "base_url"),
    ("UPdatedAt", "u_pdated_at"),
    ("updated_at", "updated_at"),
    (" updated_at ", "updated_at"),
    ("updatedat", "updatedat"),
    ("", ""),
]


@pytest.mark.parametrize("value,expected", test_data)
def test_clean_string(value, expected):
    test = clean_string(value)

    assert test == expected
