import logging
from io import StringIO
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

import orjson
import pytest

from source_s3.v4.parsers.json_flatten_parser import JsonFlattenParser


class FakeRemoteFile:
    def __init__(self, uri: str):
        self.uri = uri
        self.last_modified = None


class FakeStreamReader:
    """Simulates stream_reader.open_file() returning a file-like object."""

    def __init__(self, content: str):
        self._content = content

    def open_file(self, file, mode, encoding, logger):
        return StringIO(self._content)


def _collect_records(parser, content: str, file_uri: str = "test.json") -> List[Dict[str, Any]]:
    """Helper to run parse_records and collect all yielded records."""
    reader = FakeStreamReader(content)
    file = FakeRemoteFile(file_uri)
    config = MagicMock()
    logger = logging.getLogger("test")
    return list(parser.parse_records(config, file, reader, logger, None))


class TestJsonFlattenParserParseRecords:
    def test_yields_individual_records_as_raw_dicts(self):
        """Each element under the flatten key is yielded as a raw dict (CDK wraps in {"data":...})."""
        content = orjson.dumps({"Records": [{"a": 1}, {"b": 2}, {"c": 3}]}).decode()
        parser = JsonFlattenParser("Records")
        records = _collect_records(parser, content)
        assert records == [{"a": 1}, {"b": 2}, {"c": 3}]

    def test_single_record(self):
        content = orjson.dumps({"Records": [{"only": "one"}]}).decode()
        parser = JsonFlattenParser("Records")
        records = _collect_records(parser, content)
        assert records == [{"only": "one"}]

    def test_empty_array_yields_nothing(self):
        content = orjson.dumps({"Records": []}).decode()
        parser = JsonFlattenParser("Records")
        records = _collect_records(parser, content)
        assert records == []

    def test_missing_key_yields_nothing_and_warns(self, caplog):
        content = orjson.dumps({"Other": [{"a": 1}]}).decode()
        parser = JsonFlattenParser("Records")
        with caplog.at_level(logging.WARNING):
            records = _collect_records(parser, content)
        assert records == []
        assert "not found" in caplog.text

    def test_malformed_json_raises_record_parse_error(self):
        from airbyte_cdk.sources.file_based.exceptions import RecordParseError

        parser = JsonFlattenParser("Records")
        with pytest.raises(RecordParseError):
            _collect_records(parser, "not valid json {{{")

    def test_preserves_nested_event_structure(self):
        event = {
            "eventVersion": "1.08",
            "userIdentity": {"type": "AssumedRole", "arn": "arn:aws:iam::123:role/x"},
            "sourceIPAddress": "10.0.0.1",
            "requestParameters": {"bucketName": "b", "key": "k"},
        }
        content = orjson.dumps({"Records": [event]}).decode()
        parser = JsonFlattenParser("Records")
        records = _collect_records(parser, content)
        assert records == [event]

    def test_custom_flatten_key(self):
        content = orjson.dumps({"events": [{"x": 1}]}).decode()
        parser = JsonFlattenParser("events")
        records = _collect_records(parser, content)
        assert records == [{"x": 1}]


class TestJsonFlattenParserConfig:
    def test_check_config_returns_true(self):
        parser = JsonFlattenParser("Records")
        ok, err = parser.check_config(MagicMock())
        assert ok is True
        assert err is None

    def test_file_read_mode_is_read(self):
        from airbyte_cdk.sources.file_based.file_based_stream_reader import FileReadMode

        parser = JsonFlattenParser("Records")
        assert parser.file_read_mode == FileReadMode.READ
