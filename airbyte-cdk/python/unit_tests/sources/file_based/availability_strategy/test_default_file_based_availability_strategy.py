#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import unittest
from datetime import datetime
from unittest.mock import Mock, PropertyMock

from airbyte_cdk.sources.file_based.availability_strategy.default_file_based_availability_strategy import (
    DefaultFileBasedAvailabilityStrategy,
)
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.config.jsonl_format import JsonlFormat
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.stream import AbstractFileBasedStream

_FILE_WITH_UNKNOWN_EXTENSION = RemoteFile(uri="a.unknown_extension", last_modified=datetime.now(), file_type="csv")
_ANY_CONFIG = FileBasedStreamConfig(
    name="config.name",
    file_type="parquet",
    format=JsonlFormat(),
)
_ANY_SCHEMA = {"key": "value"}


class DefaultFileBasedAvailabilityStrategyTest(unittest.TestCase):

    def setUp(self) -> None:
        self._stream_reader = Mock(spec=AbstractFileBasedStreamReader)
        self._strategy = DefaultFileBasedAvailabilityStrategy(self._stream_reader)

        self._parser = Mock(spec=FileTypeParser)
        self._stream = Mock(spec=AbstractFileBasedStream)
        self._stream.get_parser.return_value = self._parser
        self._stream.catalog_schema = _ANY_SCHEMA
        self._stream.config = _ANY_CONFIG
        self._stream.validation_policy = PropertyMock(validate_schema_before_sync=False)

    def test_given_file_extension_does_not_match_when_check_availability_and_parsability_then_stream_is_still_available(self) -> None:
        """
        Before, we had a validation on the file extension but it turns out that in production, users sometimes have mismatch there. The
        example we've seen was for JSONL parser but the file extension was just `.json`. Note that there we more than one record extracted
        from this stream so it's not just that the file is one JSON object
        """
        self._stream.list_files.return_value = [_FILE_WITH_UNKNOWN_EXTENSION]
        self._parser.parse_records.return_value = [{"a record": 1}]

        is_available, reason = self._strategy.check_availability_and_parsability(self._stream, Mock(), Mock())

        assert is_available
