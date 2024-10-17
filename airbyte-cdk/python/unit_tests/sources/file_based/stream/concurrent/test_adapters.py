#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
import unittest
from datetime import datetime
from unittest.mock import MagicMock, Mock

import pytest
from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, AirbyteStream, Level, SyncMode
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.file_based.availability_strategy import DefaultFileBasedAvailabilityStrategy
from airbyte_cdk.sources.file_based.config.csv_format import CsvFormat
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.discovery_policy import DefaultDiscoveryPolicy
from airbyte_cdk.sources.file_based.exceptions import FileBasedErrorsCollector
from airbyte_cdk.sources.file_based.file_types import default_parsers
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_validation_policies import EmitRecordPolicy
from airbyte_cdk.sources.file_based.stream import DefaultFileBasedStream
from airbyte_cdk.sources.file_based.stream.concurrent.adapters import (
    FileBasedStreamFacade,
    FileBasedStreamPartition,
    FileBasedStreamPartitionGenerator,
)
from airbyte_cdk.sources.file_based.stream.concurrent.cursor import FileBasedFinalStateCursor
from airbyte_cdk.sources.message import InMemoryMessageRepository
from airbyte_cdk.sources.streams.concurrent.cursor import Cursor
from airbyte_cdk.sources.streams.concurrent.exceptions import ExceptionWithDisplayMessage
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.utils.slice_logger import SliceLogger
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from freezegun import freeze_time

_ANY_SYNC_MODE = SyncMode.full_refresh
_ANY_STATE = {"state_key": "state_value"}
_ANY_CURSOR_FIELD = ["a", "cursor", "key"]
_STREAM_NAME = "stream"
_ANY_CURSOR = Mock(spec=FileBasedFinalStateCursor)


@pytest.mark.parametrize(
    "sync_mode",
    [
        pytest.param(SyncMode.full_refresh, id="test_full_refresh"),
        pytest.param(SyncMode.incremental, id="test_incremental"),
    ],
)
def test_file_based_stream_partition_generator(sync_mode):
    stream = Mock()
    message_repository = Mock()
    stream_slices = [
        {"files": [RemoteFile(uri="1", last_modified=datetime.now())]},
        {"files": [RemoteFile(uri="2", last_modified=datetime.now())]},
    ]
    stream.stream_slices.return_value = stream_slices

    partition_generator = FileBasedStreamPartitionGenerator(
        stream, message_repository, _ANY_SYNC_MODE, _ANY_CURSOR_FIELD, _ANY_STATE, _ANY_CURSOR
    )

    partitions = list(partition_generator.generate())
    slices = [partition.to_slice() for partition in partitions]
    assert slices == stream_slices
    stream.stream_slices.assert_called_once_with(sync_mode=_ANY_SYNC_MODE, cursor_field=_ANY_CURSOR_FIELD, stream_state=_ANY_STATE)


@pytest.mark.parametrize(
    "transformer, expected_records",
    [
        pytest.param(
            TypeTransformer(TransformConfig.NoTransform),
            [Record({"data": "1"}, Mock(spec=FileBasedStreamPartition, stream_name=Mock(return_value=_STREAM_NAME))), Record({"data": "2"}, Mock(spec=FileBasedStreamPartition, stream_name=Mock(return_value=_STREAM_NAME)))],
            id="test_no_transform",
        ),
        pytest.param(
            TypeTransformer(TransformConfig.DefaultSchemaNormalization),
            [Record({"data": 1}, Mock(spec=FileBasedStreamPartition, stream_name=Mock(return_value=_STREAM_NAME))), Record({"data": 2}, Mock(spec=FileBasedStreamPartition, stream_name=Mock(return_value=_STREAM_NAME)))],
            id="test_default_transform",
        ),
    ],
)
def test_file_based_stream_partition(transformer, expected_records):
    stream = Mock()
    stream.name = _STREAM_NAME
    stream.get_json_schema.return_value = {"type": "object", "properties": {"data": {"type": ["integer"]}}}
    stream.transformer = transformer
    message_repository = InMemoryMessageRepository()
    _slice = None
    sync_mode = SyncMode.full_refresh
    cursor_field = None
    state = None
    partition = FileBasedStreamPartition(stream, _slice, message_repository, sync_mode, cursor_field, state, _ANY_CURSOR)

    a_log_message = AirbyteMessage(
        type=MessageType.LOG,
        log=AirbyteLogMessage(
            level=Level.INFO,
            message='slice:{"partition": 1}',
        ),
    )

    stream_data = [a_log_message, {"data": "1"}, {"data": "2"}]
    stream.read_records.return_value = stream_data

    records = list(partition.read())
    messages = list(message_repository.consume_queue())

    assert records == expected_records
    assert messages == [a_log_message]


@pytest.mark.parametrize(
    "exception_type, expected_display_message",
    [
        pytest.param(Exception, None, id="test_exception_no_display_message"),
        pytest.param(ExceptionWithDisplayMessage, "display_message", id="test_exception_no_display_message"),
    ],
)
def test_file_based_stream_partition_raising_exception(exception_type, expected_display_message):
    stream = Mock()
    stream.get_error_display_message.return_value = expected_display_message

    message_repository = InMemoryMessageRepository()
    _slice = None

    partition = FileBasedStreamPartition(stream, _slice, message_repository, _ANY_SYNC_MODE, _ANY_CURSOR_FIELD, _ANY_STATE, _ANY_CURSOR)

    stream.read_records.side_effect = Exception()

    with pytest.raises(exception_type) as e:
        list(partition.read())
        if isinstance(e, ExceptionWithDisplayMessage):
            assert e.display_message == "display message"


@freeze_time("2023-06-09T00:00:00Z")
@pytest.mark.parametrize(
    "_slice, expected_hash",
    [
        pytest.param(
            {"files": [RemoteFile(uri="1", last_modified=datetime.strptime("2023-06-09T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"))]},
            hash(("stream", "2023-06-09T00:00:00.000000Z_1")),
            id="test_hash_with_slice",
        ),
        pytest.param(None, hash("stream"), id="test_hash_no_slice"),
    ],
)
def test_file_based_stream_partition_hash(_slice, expected_hash):
    stream = Mock()
    stream.name = "stream"
    partition = FileBasedStreamPartition(stream, _slice, Mock(), _ANY_SYNC_MODE, _ANY_CURSOR_FIELD, _ANY_STATE, _ANY_CURSOR)

    _hash = partition.__hash__()
    assert _hash == expected_hash


class StreamFacadeTest(unittest.TestCase):
    def setUp(self):
        self._abstract_stream = Mock()
        self._abstract_stream.name = "stream"
        self._abstract_stream.as_airbyte_stream.return_value = AirbyteStream(
            name="stream",
            json_schema={"type": "object"},
            supported_sync_modes=[SyncMode.full_refresh],
        )
        self._legacy_stream = DefaultFileBasedStream(
            cursor=FileBasedFinalStateCursor(stream_config=MagicMock(), stream_namespace=None, message_repository=Mock()),
            config=FileBasedStreamConfig(name="stream", format=CsvFormat()),
            catalog_schema={},
            stream_reader=MagicMock(),
            availability_strategy=DefaultFileBasedAvailabilityStrategy(MagicMock()),
            discovery_policy=DefaultDiscoveryPolicy(),
            parsers=default_parsers,
            validation_policy=EmitRecordPolicy(),
            errors_collector=FileBasedErrorsCollector(),
        )
        self._cursor = Mock(spec=Cursor)
        self._logger = Mock()
        self._slice_logger = Mock()
        self._slice_logger.should_log_slice_message.return_value = False
        self._facade = FileBasedStreamFacade(self._abstract_stream, self._legacy_stream, self._cursor, self._slice_logger, self._logger)
        self._source = Mock()

        self._stream = Mock()
        self._stream.primary_key = "id"

    def test_name_is_delegated_to_wrapped_stream(self):
        assert self._facade.name == self._abstract_stream.name

    def test_cursor_field_is_a_string(self):
        self._abstract_stream.cursor_field = "cursor_field"
        assert self._facade.cursor_field == "cursor_field"

    def test_source_defined_cursor_is_true(self):
        assert self._facade.source_defined_cursor

    def test_json_schema_is_delegated_to_wrapped_stream(self):
        json_schema = {"type": "object"}
        self._abstract_stream.get_json_schema.return_value = json_schema
        assert self._facade.get_json_schema() == json_schema
        self._abstract_stream.get_json_schema.assert_called_once_with()

    def test_given_cursor_is_noop_when_supports_incremental_then_return_legacy_stream_response(self):
        assert (
            FileBasedStreamFacade(
                self._abstract_stream, self._legacy_stream, _ANY_CURSOR, Mock(spec=SliceLogger), Mock(spec=logging.Logger)
            ).supports_incremental
            == self._legacy_stream.supports_incremental
        )

    def test_given_cursor_is_not_noop_when_supports_incremental_then_return_true(self):
        assert FileBasedStreamFacade(
            self._abstract_stream, self._legacy_stream, Mock(spec=Cursor), Mock(spec=SliceLogger), Mock(spec=logging.Logger)
        ).supports_incremental

    def test_full_refresh(self):
        expected_stream_data = [{"data": 1}, {"data": 2}]

        partition = Mock()
        records = [Record(data, partition) for data in expected_stream_data]
        partition.read.return_value = records
        self._abstract_stream.generate_partitions.return_value = [partition]

        actual_stream_data = list(self._facade.read_records(SyncMode.full_refresh, None, {}, None))

        assert actual_stream_data == expected_stream_data

    def test_read_records(self):
        expected_stream_data = [{"data": 1}, {"data": 2}]
        records = [Record(data, "stream") for data in expected_stream_data]
        partition = Mock()
        partition.read.return_value = records
        self._abstract_stream.generate_partitions.return_value = [partition]

        actual_stream_data = list(self._facade.read(None, None, None, None, None, None))

        assert actual_stream_data == expected_stream_data

    def test_create_from_stream_stream(self):
        stream = Mock()
        stream.name = "stream"
        stream.primary_key = "id"
        stream.cursor_field = "cursor"

        facade = FileBasedStreamFacade.create_from_stream(stream, self._source, self._logger, _ANY_STATE, self._cursor)

        assert facade.name == "stream"
        assert facade.cursor_field == "cursor"
        assert facade._abstract_stream._primary_key == ["id"]

    def test_create_from_stream_stream_with_none_primary_key(self):
        stream = Mock()
        stream.name = "stream"
        stream.primary_key = None
        stream.cursor_field = []

        facade = FileBasedStreamFacade.create_from_stream(stream, self._source, self._logger, _ANY_STATE, self._cursor)
        assert facade._abstract_stream._primary_key == []

    def test_create_from_stream_with_composite_primary_key(self):
        stream = Mock()
        stream.name = "stream"
        stream.primary_key = ["id", "name"]
        stream.cursor_field = []

        facade = FileBasedStreamFacade.create_from_stream(stream, self._source, self._logger, _ANY_STATE, self._cursor)
        assert facade._abstract_stream._primary_key == ["id", "name"]

    def test_create_from_stream_with_empty_list_cursor(self):
        stream = Mock()
        stream.primary_key = "id"
        stream.cursor_field = []

        facade = FileBasedStreamFacade.create_from_stream(stream, self._source, self._logger, _ANY_STATE, self._cursor)

        assert facade.cursor_field == []

    def test_create_from_stream_raises_exception_if_primary_key_is_nested(self):
        stream = Mock()
        stream.name = "stream"
        stream.primary_key = [["field", "id"]]

        with self.assertRaises(ValueError):
            FileBasedStreamFacade.create_from_stream(stream, self._source, self._logger, _ANY_STATE, self._cursor)

    def test_create_from_stream_raises_exception_if_primary_key_has_invalid_type(self):
        stream = Mock()
        stream.name = "stream"
        stream.primary_key = 123

        with self.assertRaises(ValueError):
            FileBasedStreamFacade.create_from_stream(stream, self._source, self._logger, _ANY_STATE, self._cursor)

    def test_create_from_stream_raises_exception_if_cursor_field_is_nested(self):
        stream = Mock()
        stream.name = "stream"
        stream.primary_key = "id"
        stream.cursor_field = ["field", "cursor"]

        with self.assertRaises(ValueError):
            FileBasedStreamFacade.create_from_stream(stream, self._source, self._logger, _ANY_STATE, self._cursor)

    def test_create_from_stream_with_cursor_field_as_list(self):
        stream = Mock()
        stream.name = "stream"
        stream.primary_key = "id"
        stream.cursor_field = ["cursor"]

        facade = FileBasedStreamFacade.create_from_stream(stream, self._source, self._logger, _ANY_STATE, self._cursor)
        assert facade.cursor_field == "cursor"

    def test_create_from_stream_none_message_repository(self):
        self._stream.name = "stream"
        self._stream.primary_key = "id"
        self._stream.cursor_field = "cursor"
        self._source.message_repository = None

        with self.assertRaises(ValueError):
            FileBasedStreamFacade.create_from_stream(self._stream, self._source, self._logger, {}, self._cursor)

    def test_get_error_display_message_no_display_message(self):
        self._stream.get_error_display_message.return_value = "display_message"

        facade = FileBasedStreamFacade.create_from_stream(self._stream, self._source, self._logger, _ANY_STATE, self._cursor)

        expected_display_message = None
        e = Exception()

        display_message = facade.get_error_display_message(e)

        assert display_message == expected_display_message

    def test_get_error_display_message_with_display_message(self):
        self._stream.get_error_display_message.return_value = "display_message"

        facade = FileBasedStreamFacade.create_from_stream(self._stream, self._source, self._logger, _ANY_STATE, self._cursor)

        expected_display_message = "display_message"
        e = ExceptionWithDisplayMessage("display_message")

        display_message = facade.get_error_display_message(e)

        assert display_message == expected_display_message


@pytest.mark.parametrize(
    "exception, expected_display_message",
    [
        pytest.param(Exception("message"), None, id="test_no_display_message"),
        pytest.param(ExceptionWithDisplayMessage("message"), "message", id="test_no_display_message"),
    ],
)
def test_get_error_display_message(exception, expected_display_message):
    stream = Mock()
    legacy_stream = Mock()
    cursor = Mock(spec=Cursor)
    facade = FileBasedStreamFacade(stream, legacy_stream, cursor, Mock().Mock(), Mock())

    display_message = facade.get_error_display_message(exception)

    assert display_message == expected_display_message
