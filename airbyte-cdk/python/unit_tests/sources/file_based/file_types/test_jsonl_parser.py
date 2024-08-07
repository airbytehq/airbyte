#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import asyncio
import io
import json
from typing import Any, Dict
from unittest.mock import MagicMock, Mock

import pytest
from airbyte_cdk.sources.file_based.exceptions import RecordParseError
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_types import JsonlParser

JSONL_CONTENT_WITHOUT_MULTILINE_JSON_OBJECTS = [
    b'{"a": 1, "b": "1"}',
    b'{"a": 2, "b": "2"}',
]
JSONL_CONTENT_WITH_MULTILINE_JSON_OBJECTS = [
    b"{",
    b'  "a": 1,',
    b'  "b": "1"',
    b"}",
    b"{",
    b'  "a": 2,',
    b'  "b": "2"',
    b"}",
]
INVALID_JSON_CONTENT = [
    b"{",
    b'  "a": 1,',
    b'  "b": "1"',
    b"{",
    b'  "a": 2,',
    b'  "b": "2"',
    b"}",
]


@pytest.fixture
def stream_reader() -> MagicMock:
    return MagicMock(spec=AbstractFileBasedStreamReader)


def _infer_schema(stream_reader: MagicMock) -> Dict[str, Any]:
    loop = asyncio.new_event_loop()
    task = loop.create_task(JsonlParser().infer_schema(Mock(), Mock(), stream_reader, Mock()))
    loop.run_until_complete(task)
    return task.result()  # type: ignore  # asyncio has no typing


def test_when_infer_then_return_proper_types(stream_reader: MagicMock) -> None:
    record = {"col1": 1, "col2": 2.2, "col3": "3", "col4": ["a", "list"], "col5": {"inner": "obj"}, "col6": None, "col7": True}
    stream_reader.open_file.return_value.__enter__.return_value = io.BytesIO(json.dumps(record).encode("utf-8"))

    schema = _infer_schema(stream_reader)

    assert schema == {
        "col1": {"type": "integer"},
        "col2": {"type": "number"},
        "col3": {"type": "string"},
        "col4": {"type": "array"},
        "col5": {"type": "object"},
        "col6": {"type": "null"},
        "col7": {"type": "boolean"},
    }


def test_given_str_io_when_infer_then_return_proper_types(stream_reader: MagicMock) -> None:
    stream_reader.open_file.return_value.__enter__.return_value = io.StringIO('{"col": 1}')

    schema = _infer_schema(stream_reader)

    assert schema == {"col": {"type": "integer"}}


def test_given_empty_record_when_infer_then_return_empty_schema(stream_reader: MagicMock) -> None:
    stream_reader.open_file.return_value.__enter__.return_value = io.BytesIO("{}".encode("utf-8"))
    schema = _infer_schema(stream_reader)
    assert schema == {}


def test_given_no_records_when_infer_then_return_empty_schema(stream_reader: MagicMock) -> None:
    stream_reader.open_file.return_value.__enter__.return_value = io.BytesIO("".encode("utf-8"))
    schema = _infer_schema(stream_reader)
    assert schema == {}


def test_given_limit_hit_when_infer_then_stop_considering_records(stream_reader: MagicMock) -> None:
    jsonl_file_content = '{"key": 2.' + "2" * JsonlParser.MAX_BYTES_PER_FILE_FOR_SCHEMA_INFERENCE + '}\n{"key": "a string"}'
    stream_reader.open_file.return_value.__enter__.return_value = io.BytesIO(jsonl_file_content.encode("utf-8"))

    schema = _infer_schema(stream_reader)

    assert schema == {"key": {"type": "number"}}


def test_given_multiline_json_objects_and_read_limit_hit_when_infer_then_return_parse_until_at_least_one_record(
    stream_reader: MagicMock,
) -> None:
    jsonl_file_content = '{\n"key": 2.' + "2" * JsonlParser.MAX_BYTES_PER_FILE_FOR_SCHEMA_INFERENCE + "\n}"
    stream_reader.open_file.return_value.__enter__.return_value = io.BytesIO(jsonl_file_content.encode("utf-8"))

    schema = _infer_schema(stream_reader)

    assert schema == {"key": {"type": "number"}}


def test_given_multiline_json_objects_and_hits_read_limit_when_infer_then_return_proper_types(stream_reader: MagicMock) -> None:
    stream_reader.open_file.return_value.__enter__.return_value = JSONL_CONTENT_WITH_MULTILINE_JSON_OBJECTS
    schema = _infer_schema(stream_reader)
    assert schema == {"a": {"type": "integer"}, "b": {"type": "string"}}


def test_given_multiple_records_then_merge_types(stream_reader: MagicMock) -> None:
    stream_reader.open_file.return_value.__enter__.return_value = io.BytesIO('{"col1": 1}\n{"col1": 2.3}'.encode("utf-8"))
    schema = _infer_schema(stream_reader)
    assert schema == {"col1": {"type": "number"}}


def test_given_one_json_per_line_when_parse_records_then_return_records(stream_reader: MagicMock) -> None:
    stream_reader.open_file.return_value.__enter__.return_value = JSONL_CONTENT_WITHOUT_MULTILINE_JSON_OBJECTS
    records = list(JsonlParser().parse_records(Mock(), Mock(), stream_reader, Mock(), None))
    assert records == [{"a": 1, "b": "1"}, {"a": 2, "b": "2"}]


def test_given_one_json_per_line_when_parse_records_then_do_not_send_warning(stream_reader: MagicMock) -> None:
    stream_reader.open_file.return_value.__enter__.return_value = JSONL_CONTENT_WITHOUT_MULTILINE_JSON_OBJECTS
    logger = Mock()

    list(JsonlParser().parse_records(Mock(), Mock(), stream_reader, logger, None))

    assert logger.warning.call_count == 0


def test_given_multiline_json_object_when_parse_records_then_return_records(stream_reader: MagicMock) -> None:
    stream_reader.open_file.return_value.__enter__.return_value = JSONL_CONTENT_WITH_MULTILINE_JSON_OBJECTS
    records = list(JsonlParser().parse_records(Mock(), Mock(), stream_reader, Mock(), None))
    assert records == [{"a": 1, "b": "1"}, {"a": 2, "b": "2"}]


def test_given_multiline_json_object_when_parse_records_then_log_once_one_record_yielded(stream_reader: MagicMock) -> None:
    stream_reader.open_file.return_value.__enter__.return_value = JSONL_CONTENT_WITH_MULTILINE_JSON_OBJECTS
    logger = Mock()

    next(iter(JsonlParser().parse_records(Mock(), Mock(), stream_reader, logger, None)))

    assert logger.warning.call_count == 1


def test_given_unparsable_json_when_parse_records_then_raise_error(stream_reader: MagicMock) -> None:
    stream_reader.open_file.return_value.__enter__.return_value = INVALID_JSON_CONTENT
    logger = Mock()

    with pytest.raises(RecordParseError):
        list(JsonlParser().parse_records(Mock(), Mock(), stream_reader, logger, None))
    assert logger.warning.call_count == 0
