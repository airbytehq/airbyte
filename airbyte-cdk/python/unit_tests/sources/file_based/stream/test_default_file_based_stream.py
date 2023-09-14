#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import unittest
from datetime import datetime, timezone
from typing import Any, Iterable, Iterator, Mapping
from unittest.mock import Mock

import pytest
from airbyte_cdk.models import Level
from airbyte_cdk.sources.file_based.availability_strategy import AbstractFileBasedAvailabilityStrategy
from airbyte_cdk.sources.file_based.discovery_policy import AbstractDiscoveryPolicy
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_validation_policies import AbstractSchemaValidationPolicy
from airbyte_cdk.sources.file_based.stream.cursor import AbstractFileBasedCursor
from airbyte_cdk.sources.file_based.stream.default_file_based_stream import DefaultFileBasedStream


class MockFormat:
    pass


@pytest.mark.parametrize(
    "input_schema, expected_output",
    [
        pytest.param({}, {}, id="empty-schema"),
        pytest.param(
            {"type": "string"},
            {"type": ["null", "string"]},
            id="simple-schema",
        ),
        pytest.param(
            {"type": ["string"]},
            {"type": ["null", "string"]},
            id="simple-schema-list-type",
        ),
        pytest.param(
            {"type": ["null", "string"]},
            {"type": ["null", "string"]},
            id="simple-schema-already-has-null",
        ),
        pytest.param(
            {"properties": {"type": "string"}},
            {"properties": {"type": ["null", "string"]}},
            id="nested-schema",
        ),
        pytest.param(
            {"items": {"type": "string"}},
            {"items": {"type": ["null", "string"]}},
            id="array-schema",
        ),
        pytest.param(
            {"type": "object", "properties": {"prop": {"type": "string"}}},
            {"type": ["null", "object"], "properties": {"prop": {"type": ["null", "string"]}}},
            id="deeply-nested-schema",
        ),
    ],
)
def test_fill_nulls(input_schema: Mapping[str, Any], expected_output: Mapping[str, Any]) -> None:
    assert DefaultFileBasedStream._fill_nulls(input_schema) == expected_output


class DefaultFileBasedStreamTest(unittest.TestCase):
    _NOW = datetime(2022, 10, 22, tzinfo=timezone.utc)
    _A_RECORD = {"a_record": 1}

    def setUp(self) -> None:
        self._stream_config = Mock()
        self._stream_config.format = MockFormat()
        self._stream_config.name = "a stream name"
        self._catalog_schema = Mock()
        self._stream_reader = Mock(spec=AbstractFileBasedStreamReader)
        self._availability_strategy = Mock(spec=AbstractFileBasedAvailabilityStrategy)
        self._discovery_policy = Mock(spec=AbstractDiscoveryPolicy)
        self._parser = Mock(spec=FileTypeParser)
        self._validation_policy = Mock(spec=AbstractSchemaValidationPolicy)
        self._validation_policy.name = "validation policy name"
        self._cursor = Mock(spec=AbstractFileBasedCursor)

        self._stream = DefaultFileBasedStream(
            config=self._stream_config,
            catalog_schema=self._catalog_schema,
            stream_reader=self._stream_reader,
            availability_strategy=self._availability_strategy,
            discovery_policy=self._discovery_policy,
            parsers={MockFormat: self._parser},
            validation_policy=self._validation_policy,
            cursor=self._cursor,
        )

    def test_when_read_records_from_slice_then_return_records(self) -> None:
        self._parser.parse_records.return_value = [self._A_RECORD]
        messages = list(self._stream.read_records_from_slice({"files": [RemoteFile(uri="uri", last_modified=self._NOW)]}))
        assert list(map(lambda message: message.record.data["data"], messages)) == [self._A_RECORD]

    def test_given_exception_when_read_records_from_slice_then_do_process_other_files(self) -> None:
        """
        The current behavior for source-s3 v3 does not fail sync on some errors and hence, we will keep this behaviour for now. One example
        we can easily reproduce this is by having a file with gzip extension that is not actually a gzip file. The reader will fail to open
        the file but the sync won't fail.
        Ticket: https://github.com/airbytehq/airbyte/issues/29680
        """
        self._parser.parse_records.side_effect = [ValueError("An error"), [self._A_RECORD]]

        messages = list(self._stream.read_records_from_slice({"files": [
            RemoteFile(uri="invalid_file", last_modified=self._NOW),
            RemoteFile(uri="valid_file", last_modified=self._NOW),
        ]}))

        assert messages[0].log.level == Level.ERROR
        assert messages[1].record.data["data"] == self._A_RECORD

    def test_given_exception_after_skipping_records_when_read_records_from_slice_then_send_warning(self) -> None:
        self._stream_config.schemaless = False
        self._validation_policy.record_passes_validation_policy.return_value = False
        self._parser.parse_records.side_effect = [self._iter([self._A_RECORD, ValueError("An error")])]

        messages = list(self._stream.read_records_from_slice({"files": [
            RemoteFile(uri="invalid_file", last_modified=self._NOW),
            RemoteFile(uri="valid_file", last_modified=self._NOW),
        ]}))

        assert messages[0].log.level == Level.ERROR
        assert messages[1].log.level == Level.WARN

    def _iter(self, x: Iterable[Any]) -> Iterator[Any]:
        for item in x:
            if isinstance(item, Exception):
                raise item
            yield item
