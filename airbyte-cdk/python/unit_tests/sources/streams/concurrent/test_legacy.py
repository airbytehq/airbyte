#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import unittest
from unittest.mock import Mock

import pytest
from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level, SyncMode
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.message import InMemoryMessageRepository
from airbyte_cdk.sources.streams.concurrent.availability_strategy import STREAM_AVAILABLE, StreamAvailable, StreamUnavailable
from airbyte_cdk.sources.streams.concurrent.legacy import (
    AvailabilityStrategyFacade,
    LegacyAvailabilityStrategy,
    LegacyErrorMessageParser,
    LegacyPartition,
    LegacyPartitionGenerator,
    StreamFacade,
)
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record


@pytest.mark.parametrize(
    "stream_availability, expected_available, expected_message",
    [
        pytest.param(StreamAvailable(), True, None, id="test_stream_is_available"),
        pytest.param(STREAM_AVAILABLE, True, None, id="test_stream_is_available_using_singleton"),
        pytest.param(StreamUnavailable("message"), False, "message", id="test_stream_is_available"),
    ],
)
def test_availability_strategy_facade(stream_availability, expected_available, expected_message):
    strategy = Mock()
    strategy.check_availability.return_value = stream_availability
    facade = AvailabilityStrategyFacade(strategy)

    logger = Mock()
    available, message = facade.check_availability(Mock(), logger, Mock())

    assert available == expected_available
    assert message == expected_message

    strategy.check_availability.assert_called_once_with(logger)


def test_legacy_availability_strategy():
    stream = Mock()
    source = Mock()
    stream.check_availability.return_value = True, None
    logger = Mock()
    availability_strategy = LegacyAvailabilityStrategy(stream, source)

    available, message = availability_strategy.check_availability(logger)
    assert available
    assert message is None

    stream.check_availability.assert_called_once_with(logger, source)


def test_legacy_error_message_parser():
    stream = Mock()
    stream.get_error_display_message.return_value = "error message"
    message_parser = LegacyErrorMessageParser(stream)
    exception = Mock()

    error_message = message_parser.get_error_display_message(exception)

    assert error_message == "error message"
    stream.get_error_display_message.assert_called_once_with(exception)


@pytest.mark.parametrize(
    "sync_mode",
    [
        pytest.param(SyncMode.full_refresh, id="test_full_refresh"),
        pytest.param(SyncMode.incremental, id="test_incremental"),
    ],
)
def test_legacy_partition_generator(sync_mode):
    stream = Mock()
    message_repository = Mock()
    stream_slices = [{"slice": 1}, {"slice": 2}]
    stream.stream_slices.return_value = stream_slices

    partition_generator = LegacyPartitionGenerator(stream, message_repository)

    partitions = list(partition_generator.generate(sync_mode))
    slices = [partition.to_slice() for partition in partitions]
    assert slices == stream_slices


def test_legacy_partition():
    stream = Mock()
    message_repository = InMemoryMessageRepository()
    _slice = None
    partition = LegacyPartition(stream, _slice, message_repository)

    a_log_message = AirbyteMessage(
        type=MessageType.LOG,
        log=AirbyteLogMessage(
            level=Level.INFO,
            message='slice:{"partition": 1}',
        ),
    )

    stream_data = [a_log_message, {"data": 1}, {"data": 2}]
    stream.read_records.return_value = stream_data

    records = list(partition.read())
    messages = list(message_repository.consume_queue())

    expected_records = [
        Record({"data": 1}),
        Record({"data": 2}),
    ]

    assert records == expected_records
    assert messages == [a_log_message]


@pytest.mark.parametrize(
    "_slice, expected_hash",
    [
        pytest.param({"partition": 1, "k": "v"}, hash(("stream", '{"k": "v", "partition": 1}')), id="test_hash_with_slice"),
        pytest.param(None, hash("stream"), id="test_hash_no_slice"),
    ],
)
def test_legacy_partition_hash(_slice, expected_hash):
    stream = Mock()
    stream.name = "stream"
    partition = LegacyPartition(stream, _slice, Mock())

    _hash = partition.__hash__()
    assert _hash == expected_hash


class StreamFacadeTest(unittest.TestCase):
    def setUp(self):
        self._stream = Mock()
        self._facade = StreamFacade(self._stream)

    def test_name_is_delegated_to_wrapped_stream(self):
        assert self._facade.name == self._stream.name

    def test_primary_key_is_delegated_to_wrapped_stream(self):
        assert self._facade.primary_key == self._stream.primary_key

    def test_cursor_field_is_a_string(self):
        self._stream.cursor_field = "cursor_field"
        assert self._facade.cursor_field == "cursor_field"

    def test_none_cursor_field_is_converted_to_an_empty_list(self):
        self._stream.cursor_field = None
        assert self._facade.cursor_field == []

    def test_source_defined_cursor_is_true(self):
        assert self._facade.source_defined_cursor

    def test_json_schema_is_delegated_to_wrapped_stream(self):
        json_schema = {"type": "object"}
        self._stream.get_json_schema.return_value = json_schema
        assert self._facade.get_json_schema() == json_schema
        self._stream.get_json_schema.assert_called_once_with()

    def test_supports_incremental_is_false(self):
        assert self._facade.supports_incremental is False

    def test_check_availability_is_delegated_to_wrapped_stream(self):
        availability = True, None
        self._stream.check_availability.return_value = availability
        assert self._facade.check_availability(Mock(), Mock()) == availability
        self._stream.check_availability.assert_called_once_with()

    def test_get_error_display_message_is_delegated_to_wrapped_stream(self):
        exception = Mock()
        display_message = "display_message"
        self._stream.get_error_display_message.return_value = display_message
        assert self._facade.get_error_display_message(exception) == display_message
        self._stream.get_error_display_message.assert_called_once_with(exception)

    def test_full_refresh(self):
        expected_stream_data = [{"data": 1}, {"data": 2}]
        records = [Record(data) for data in expected_stream_data]
        self._stream.read.return_value = records

        actual_stream_data = list(self._facade.read_records(SyncMode.full_refresh, None, None, None))

        assert actual_stream_data == expected_stream_data

    def test_read_records_full_refresh(self):
        expected_stream_data = [{"data": 1}, {"data": 2}]
        records = [Record(data) for data in expected_stream_data]
        self._stream.read.return_value = records

        actual_stream_data = list(self._facade.read_full_refresh(None, None, None))

        assert actual_stream_data == expected_stream_data

    def test_read_records_incremental(self):
        with self.assertRaises(NotImplementedError):
            list(self._facade.read_records(SyncMode.incremental, None, None, None))

    def test_create_from_legacy_stream(self):
        legacy_stream = Mock()
        legacy_stream.name = "stream"
        legacy_stream.primary_key = "id"
        legacy_stream.cursor_field = "cursor"
        source = Mock()
        max_workers = 10

        facade = StreamFacade.create_from_legacy_stream(legacy_stream, source, max_workers)

        assert facade.name == "stream"
        assert facade.primary_key == "id"
        assert facade.cursor_field == "cursor"

    def test_create_from_legacy_stream_with_none_primary_key(self):
        legacy_stream = Mock()
        legacy_stream.primary_key = None
        legacy_stream.cursor_field = []
        source = Mock()
        max_workers = 10

        facade = StreamFacade.create_from_legacy_stream(legacy_stream, source, max_workers)

        assert facade.primary_key is None

    def test_create_from_legacy_stream_with_composite_primary_key(self):
        legacy_stream = Mock()
        legacy_stream.primary_key = ["id", "name"]
        legacy_stream.cursor_field = []
        source = Mock()
        max_workers = 10

        facade = StreamFacade.create_from_legacy_stream(legacy_stream, source, max_workers)

        assert facade.primary_key == ["id", "name"]

    def test_create_from_legacy_stream_with_empty_list_cursor(self):
        legacy_stream = Mock()
        legacy_stream.primary_key = "id"
        legacy_stream.cursor_field = []
        source = Mock()
        max_workers = 10

        facade = StreamFacade.create_from_legacy_stream(legacy_stream, source, max_workers)

        assert facade.cursor_field == []

    def test_create_from_legacy_stream_raises_exception_if_primary_key_is_nested(self):
        legacy_stream = Mock()
        legacy_stream.name = "stream"
        legacy_stream.primary_key = [["field", "id"]]
        source = Mock()
        max_workers = 10

        with self.assertRaises(ValueError):
            StreamFacade.create_from_legacy_stream(legacy_stream, source, max_workers)

    def test_create_from_legacy_stream_raises_exception_if_primary_key_has_invalid_type(self):
        legacy_stream = Mock()
        legacy_stream.name = "stream"
        legacy_stream.primary_key = 123
        source = Mock()
        max_workers = 10

        with self.assertRaises(ValueError):
            StreamFacade.create_from_legacy_stream(legacy_stream, source, max_workers)

    def test_create_from_legacy_stream_raises_exception_if_cursor_field_is_nested(self):
        legacy_stream = Mock()
        legacy_stream.name = "stream"
        legacy_stream.primary_key = "id"
        legacy_stream.cursor_field = ["field", "cursor"]
        source = Mock()
        max_workers = 10

        with self.assertRaises(ValueError):
            StreamFacade.create_from_legacy_stream(legacy_stream, source, max_workers)

    def test_create_from_legacy_stream_with_cursor_field_as_list(self):
        legacy_stream = Mock()
        legacy_stream.name = "stream"
        legacy_stream.primary_key = "id"
        legacy_stream.cursor_field = ["cursor"]
        source = Mock()
        max_workers = 10

        facade = StreamFacade.create_from_legacy_stream(legacy_stream, source, max_workers)
        assert facade.cursor_field == "cursor"

    def test_create_from_legacy_stream_none_message_repository(self):
        legacy_stream = Mock()
        legacy_stream.name = "stream"
        legacy_stream.primary_key = "id"
        legacy_stream.cursor_field = "cursor"
        source = Mock()
        source.message_repository = None
        max_workers = 10

        with self.assertRaises(ValueError):
            StreamFacade.create_from_legacy_stream(legacy_stream, source, max_workers)
