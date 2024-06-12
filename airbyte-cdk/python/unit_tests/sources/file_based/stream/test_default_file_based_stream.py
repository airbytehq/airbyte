#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import traceback
import unittest
from datetime import datetime, timezone
from typing import Any, Iterable, Iterator, Mapping
from unittest.mock import Mock

import pytest
from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.file_based.availability_strategy import AbstractFileBasedAvailabilityStrategy
from airbyte_cdk.sources.file_based.discovery_policy import AbstractDiscoveryPolicy
from airbyte_cdk.sources.file_based.exceptions import FileBasedErrorsCollector, FileBasedSourceError
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_validation_policies import AbstractSchemaValidationPolicy
from airbyte_cdk.sources.file_based.stream.cursor import AbstractFileBasedCursor
from airbyte_cdk.sources.file_based.stream.default_file_based_stream import DefaultFileBasedStream
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


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
            {
                "type": ["null", "object"],
                "properties": {"prop": {"type": ["null", "string"]}},
            },
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
            errors_collector=FileBasedErrorsCollector(),
        )

    def test_when_read_records_from_slice_then_return_records(self) -> None:
        self._parser.parse_records.return_value = [self._A_RECORD]
        messages = list(self._stream.read_records_from_slice({"files": [RemoteFile(uri="uri", last_modified=self._NOW)]}))
        assert list(map(lambda message: message.record.data["data"], messages)) == [self._A_RECORD]

    def test_given_exception_when_read_records_from_slice_then_do_process_other_files(
        self,
    ) -> None:
        """
        The current behavior for source-s3 v3 does not fail sync on some errors and hence, we will keep this behaviour for now. One example
        we can easily reproduce this is by having a file with gzip extension that is not actually a gzip file. The reader will fail to open
        the file but the sync won't fail.
        Ticket: https://github.com/airbytehq/airbyte/issues/29680
        """
        self._parser.parse_records.side_effect = [
            ValueError("An error"),
            [self._A_RECORD],
        ]

        messages = list(
            self._stream.read_records_from_slice(
                {
                    "files": [
                        RemoteFile(uri="invalid_file", last_modified=self._NOW),
                        RemoteFile(uri="valid_file", last_modified=self._NOW),
                    ]
                }
            )
        )

        assert messages[0].log.level == Level.ERROR
        assert messages[1].record.data["data"] == self._A_RECORD

    def test_given_traced_exception_when_read_records_from_slice_then_fail(
        self,
    ) -> None:
        """
        When a traced exception is raised, the stream shouldn't try to handle but pass it on to the caller.
        """
        self._parser.parse_records.side_effect = [AirbyteTracedException("An error")]

        with pytest.raises(AirbyteTracedException):
            list(
                self._stream.read_records_from_slice(
                    {
                        "files": [
                            RemoteFile(uri="invalid_file", last_modified=self._NOW),
                            RemoteFile(uri="valid_file", last_modified=self._NOW),
                        ]
                    }
                )
            )

    def test_given_exception_after_skipping_records_when_read_records_from_slice_then_send_warning(
        self,
    ) -> None:
        self._stream_config.schemaless = False
        self._validation_policy.record_passes_validation_policy.return_value = False
        self._parser.parse_records.side_effect = [self._iter([self._A_RECORD, ValueError("An error")])]

        messages = list(
            self._stream.read_records_from_slice(
                {
                    "files": [
                        RemoteFile(uri="invalid_file", last_modified=self._NOW),
                        RemoteFile(uri="valid_file", last_modified=self._NOW),
                    ]
                }
            )
        )

        assert messages[0].log.level == Level.ERROR
        assert messages[1].log.level == Level.WARN

    def test_override_max_n_files_for_schema_inference_is_respected(self) -> None:
        self._discovery_policy.n_concurrent_requests = 1
        self._discovery_policy.get_max_n_files_for_schema_inference.return_value = 3
        self._stream.config.input_schema = None
        self._stream.config.schemaless = None
        self._parser.infer_schema.return_value = {"data": {"type": "string"}}
        files = [RemoteFile(uri=f"file{i}", last_modified=self._NOW) for i in range(10)]
        self._stream_reader.get_matching_files.return_value = files

        schema = self._stream.get_json_schema()

        assert schema == {
            "type": "object",
            "properties": {
                "_ab_source_file_last_modified": {"type": "string"},
                "_ab_source_file_url": {"type": "string"},
                "data": {"type": ["null", "string"]},
            },
        }
        assert self._parser.infer_schema.call_count == 3

    def _iter(self, x: Iterable[Any]) -> Iterator[Any]:
        for item in x:
            if isinstance(item, Exception):
                raise item
            yield item


class TestFileBasedErrorCollector:
    test_error_collector: FileBasedErrorsCollector = FileBasedErrorsCollector()

    @pytest.mark.parametrize(
        "stream, file, line_no, n_skipped, collector_expected_len",
        (
            ("stream_1", "test.csv", 1, 1, 1),
            ("stream_2", "test2.csv", 2, 2, 2),
        ),
        ids=[
            "Single error",
            "Multiple errors",
        ],
    )
    def test_collect_parsing_error(self, stream, file, line_no, n_skipped, collector_expected_len) -> None:
        test_error_pattern = "Error parsing record."
        # format the error body
        test_error = (
            AirbyteMessage(
                type=MessageType.LOG,
                log=AirbyteLogMessage(
                    level=Level.ERROR,
                    message=f"{FileBasedSourceError.ERROR_PARSING_RECORD.value} stream={stream} file={file} line_no={line_no} n_skipped={n_skipped}",
                    stack_trace=traceback.format_exc(),
                ),
            ),
        )
        # collecting the error
        self.test_error_collector.collect(test_error)
        # check the error has been collected
        assert len(self.test_error_collector.errors) == collector_expected_len
        # check for the patern presence for the collected errors
        for error in self.test_error_collector.errors:
            assert test_error_pattern in error[0].log.message

    def test_yield_and_raise_collected(self) -> None:
        # we expect the following method will raise the AirbyteTracedException
        with pytest.raises(AirbyteTracedException) as parse_error:
            list(self.test_error_collector.yield_and_raise_collected())
        assert parse_error.value.message == "Some errors occured while reading from the source."
        assert parse_error.value.internal_message == "Please check the logged errors for more information."
