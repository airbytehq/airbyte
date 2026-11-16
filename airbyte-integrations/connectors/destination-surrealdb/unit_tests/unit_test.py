#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import pytest
from destination_surrealdb.destination import destination_field_name, normalize_url, quote_identifier, surrealdb_field_type


def test_invalid_url():
    invalid_input = "invalid_url"
    with pytest.raises(ValueError):
        _ = normalize_url(invalid_input)

    assert True


@pytest.mark.parametrize(
    "input, expected",
    [
        ("rocksdb:test", "rocksdb://test"),
        ("surrealkv:test", "surrealkv://test"),
        ("file:test", "file://test"),
        ("rocksdb://test", "rocksdb://test"),
        ("surrealkv://test", "surrealkv://test"),
        ("file://test", "file://test"),
        ("wss://test", "wss://test"),
        ("wss:test", "wss://test"),
        ("https://surrealdb.example.com/", "https://surrealdb.example.com"),
        ("ws://localhost:8000/", "ws://localhost:8000"),
    ],
)
def test_normalize_url(input, expected):
    if expected is None:
        with pytest.raises(ValueError):
            normalize_url(input)
    else:
        assert normalize_url(input) == expected


@pytest.mark.parametrize(
    "props, expected",
    [
        ({"type": "string"}, "option<string>"),
        ({"type": "integer"}, "option<int>"),
        ({"type": "number"}, "option<number>"),
        ({"type": "boolean"}, "option<bool>"),
        ({"type": "object"}, "option<object>"),
        ({"type": "array"}, "option<array>"),
        ({"type": "string", "format": "date-time"}, "option<datetime>"),
        ({"type": ["null", "string"], "format": "date-time"}, "option<datetime>"),
        ({"type": ["null", "boolean"]}, "option<bool>"),
        ({"type": ["string", "integer"]}, "option<string | int>"),
        ({"type": "null"}, "any"),
        ({}, "any"),
        ({"type": ["null", "unknown"]}, "any"),
    ],
)
def test_surrealdb_field_type(props, expected):
    assert surrealdb_field_type(props) == expected


@pytest.mark.parametrize(
    "name, expected",
    [
        ("id", "_airbyte_source_id"),
        ("name", "name"),
        ("_airbyte_raw_id", "_airbyte_raw_id"),
    ],
)
def test_destination_field_name(name, expected):
    assert destination_field_name(name) == expected


@pytest.mark.parametrize(
    "name, expected",
    [
        ("users", "`users`"),
        ("my-stream", "`my-stream`"),
        ("select", "`select`"),
        ("a`b", "`a\\`b`"),
    ],
)
def test_quote_identifier(name, expected):
    assert quote_identifier(name) == expected
