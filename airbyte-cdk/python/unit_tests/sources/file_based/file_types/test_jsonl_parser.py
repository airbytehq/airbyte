#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, Mapping
from unittest.mock import MagicMock, Mock

import pytest
from airbyte_cdk.sources.file_based.exceptions import RecordParseError
from airbyte_cdk.sources.file_based.file_types import JsonlParser


@pytest.mark.parametrize(
    "record, expected_schema",
    [
        pytest.param({}, {}, id="no_records"),
        pytest.param(
            {"col1": 1, "col2": 2.2, "col3": "3", "col4": ["a", "list"], "col5": {"inner": "obj"}, "col6": None, "col7": True},
            {
                "col1": {"type": "integer"},
                "col2": {"type": "number"},
                "col3": {"type": "string"},
                "col4": {"type": "array"},
                "col5": {"type": "object"},
                "col6": {"type": "null"},
                "col7": {"type": "boolean"},
            },
            id="all_columns_included_in_schema"
        ),
    ]
)
def test_type_mapping(record: Dict[str, Any], expected_schema: Mapping[str, str]) -> None:
    if expected_schema is None:
        with pytest.raises(ValueError):
            JsonlParser().infer_schema_for_record(record)
    else:
        assert JsonlParser.infer_schema_for_record(record) == expected_schema


JSONL_CONTENT_WITHOUT_MULTILINE_JSON_OBJECTS = [
    b'{"a": 1, "b": "1"}',
    b'{"a": 2, "b": "2"}',
]
JSONL_CONTENT_WITH_MULTILINE_JSON_OBJECTS = [
    b'{',
    b'  "a": 1,',
    b'  "b": "1"',
    b'}',
    b'{',
    b'  "a": 2,',
    b'  "b": "2"',
    b'}',
]
INVALID_JSON_CONTENT = [
    b'{',
    b'  "a": 1,',
    b'  "b": "1"',
    b'{',
    b'  "a": 2,',
    b'  "b": "2"',
    b'}',
]


def test_given_one_json_per_line_when_parse_records_then_return_records() -> None:
    stream_reader = MagicMock()
    stream_reader.open_file.return_value.__enter__.return_value = JSONL_CONTENT_WITHOUT_MULTILINE_JSON_OBJECTS

    records = list(JsonlParser().parse_records(Mock(), Mock(), stream_reader, Mock()))

    assert records == [{"a": 1, "b": "1"}, {"a": 2, "b": "2"}]


def test_given_multiline_json_object_when_parse_records_then_return_records() -> None:
    stream_reader = MagicMock()
    stream_reader.open_file.return_value.__enter__.return_value = JSONL_CONTENT_WITH_MULTILINE_JSON_OBJECTS

    records = list(JsonlParser().parse_records(Mock(), Mock(), stream_reader, Mock()))

    assert records == [{"a": 1, "b": "1"}, {"a": 2, "b": "2"}]


def test_given_multiline_json_object_when_parse_records_then_log_once_one_record_yielded() -> None:
    stream_reader = MagicMock()
    stream_reader.open_file.return_value.__enter__.return_value = JSONL_CONTENT_WITH_MULTILINE_JSON_OBJECTS
    logger = Mock()

    next(iter(JsonlParser().parse_records(Mock(), Mock(), stream_reader, logger)))

    assert logger.warning.call_count == 1


def test_given_unparsable_json_when_parse_records_then_raise_error() -> None:
    stream_reader = MagicMock()
    stream_reader.open_file.return_value.__enter__.return_value = INVALID_JSON_CONTENT
    logger = Mock()

    with pytest.raises(RecordParseError):
        list(JsonlParser().parse_records(Mock(), Mock(), stream_reader, logger))
    assert logger.warning.call_count == 0
