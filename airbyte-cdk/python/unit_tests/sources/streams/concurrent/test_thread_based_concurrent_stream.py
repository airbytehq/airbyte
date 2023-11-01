#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import unittest
from unittest.mock import Mock, call

from airbyte_cdk.models import AirbyteStream, SyncMode
from airbyte_cdk.sources.streams.concurrent.availability_strategy import STREAM_AVAILABLE
from airbyte_cdk.sources.streams.concurrent.cursor import Cursor
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.concurrent.thread_based_concurrent_stream import ThreadBasedConcurrentStream


class ThreadBasedConcurrentStreamTest(unittest.TestCase):
    def setUp(self):
        self._partition_generator = Mock()
        self._max_workers = 1
        self._name = "name"
        self._json_schema = {}
        self._availability_strategy = Mock()
        self._primary_key = []
        self._cursor_field = None
        self._slice_logger = Mock()
        self._logger = Mock()
        self._message_repository = Mock()
        self._cursor = Mock(spec=Cursor)
        self._stream = ThreadBasedConcurrentStream(
            self._partition_generator,
            self._max_workers,
            self._name,
            self._json_schema,
            self._availability_strategy,
            self._primary_key,
            self._cursor_field,
            self._slice_logger,
            self._logger,
            self._message_repository,
            1,
            2,
            0,
            cursor=self._cursor,
        )

    def test_get_json_schema(self):
        json_schema = self._stream.get_json_schema()
        assert json_schema == self._json_schema

    def test_check_availability(self):
        self._availability_strategy.check_availability.return_value = STREAM_AVAILABLE
        availability = self._stream.check_availability()
        assert availability == STREAM_AVAILABLE
        self._availability_strategy.check_availability.assert_called_once_with(self._logger)

    def test_check_for_error_raises_an_exception_if_any_of_the_futures_are_not_done(self):
        futures = [Mock() for _ in range(3)]
        for f in futures:
            f.exception.return_value = None
        futures[0].done.return_value = False

        with self.assertRaises(Exception):
            self._stream._check_for_errors(futures)

    def test_check_for_error_raises_no_exception_if_all_futures_succeeded(self):
        futures = [Mock() for _ in range(3)]
        for f in futures:
            f.exception.return_value = None

        self._stream._check_for_errors(futures)

    def test_check_for_error_raises_an_exception_if_any_of_the_futures_raised_an_exception(self):
        futures = [Mock() for _ in range(3)]
        for f in futures:
            f.exception.return_value = None
        futures[0].exception.return_value = Exception("error")

        with self.assertRaises(Exception):
            self._stream._check_for_errors(futures)

    def test_read_observe_records_and_close_partition(self):
        partition = Mock(spec=Partition)
        expected_records = [Record({"id": 1}), Record({"id": "2"})]
        partition.read.return_value = expected_records
        partition.to_slice.return_value = {"slice": "slice"}
        self._slice_logger.should_log_slice_message.return_value = False

        self._partition_generator.generate.return_value = [partition]
        actual_records = list(self._stream.read())

        assert expected_records == actual_records

        self._cursor.observe.has_calls([call(record) for record in expected_records])
        self._cursor.close_partition.assert_called_once_with(partition)

    def test_read_no_slice_message(self):
        partition = Mock(spec=Partition)
        expected_records = [Record({"id": 1}), Record({"id": "2"})]
        partition.read.return_value = expected_records
        partition.to_slice.return_value = {"slice": "slice"}
        self._slice_logger.should_log_slice_message.return_value = False

        self._partition_generator.generate.return_value = [partition]
        actual_records = list(self._stream.read())

        assert expected_records == actual_records

        self._message_repository.emit_message.assert_not_called()

    def test_read_log_slice_message(self):
        partition = Mock(spec=Partition)
        expected_records = [Record({"id": 1}), Record({"id": "2"})]
        partition.read.return_value = expected_records
        partition.to_slice.return_value = {"slice": "slice"}
        self._slice_logger.should_log_slice_message.return_value = True
        slice_log_message = Mock()
        self._slice_logger.create_slice_log_message.return_value = slice_log_message

        self._partition_generator.generate.return_value = [partition]
        list(self._stream.read())

        self._message_repository.emit_message.assert_called_once_with(slice_log_message)

    def test_wait_while_task_queue_is_full(self):
        f1 = Mock()
        f2 = Mock()

        # Verify that the done() method will be called until only one future is still running
        f1.done.side_effect = [False, False]
        f2.done.side_effect = [False, True]
        futures = [f1, f2]
        self._stream._wait_while_too_many_pending_futures(futures)

        f1.done.assert_has_calls([call(), call()])
        f2.done.assert_has_calls([call(), call()])

    def test_as_airbyte_stream(self):
        expected_airbyte_stream = AirbyteStream(
            name=self._name,
            json_schema=self._json_schema,
            supported_sync_modes=[SyncMode.full_refresh],
            source_defined_cursor=None,
            default_cursor_field=None,
            source_defined_primary_key=None,
            namespace=None,
        )
        actual_airbyte_stream = self._stream.as_airbyte_stream()

        assert expected_airbyte_stream == actual_airbyte_stream

    def test_as_airbyte_stream_with_primary_key(self):
        json_schema = {
            "type": "object",
            "properties": {
                "id_a": {"type": ["null", "string"]},
                "id_b": {"type": ["null", "string"]},
            },
        }
        stream = ThreadBasedConcurrentStream(
            self._partition_generator,
            self._max_workers,
            self._name,
            json_schema,
            self._availability_strategy,
            ["id"],
            self._cursor_field,
            self._slice_logger,
            self._logger,
            self._message_repository,
            1,
            2,
            0,
        )

        expected_airbyte_stream = AirbyteStream(
            name=self._name,
            json_schema=json_schema,
            supported_sync_modes=[SyncMode.full_refresh],
            source_defined_cursor=None,
            default_cursor_field=None,
            source_defined_primary_key=[["id"]],
            namespace=None,
        )

        airbyte_stream = stream.as_airbyte_stream()
        assert expected_airbyte_stream == airbyte_stream

    def test_as_airbyte_stream_with_composite_primary_key(self):
        json_schema = {
            "type": "object",
            "properties": {
                "id_a": {"type": ["null", "string"]},
                "id_b": {"type": ["null", "string"]},
            },
        }
        stream = ThreadBasedConcurrentStream(
            self._partition_generator,
            self._max_workers,
            self._name,
            json_schema,
            self._availability_strategy,
            ["id_a", "id_b"],
            self._cursor_field,
            self._slice_logger,
            self._logger,
            self._message_repository,
            1,
            2,
            0,
        )

        expected_airbyte_stream = AirbyteStream(
            name=self._name,
            json_schema=json_schema,
            supported_sync_modes=[SyncMode.full_refresh],
            source_defined_cursor=None,
            default_cursor_field=None,
            source_defined_primary_key=[["id_a", "id_b"]],
            namespace=None,
        )

        airbyte_stream = stream.as_airbyte_stream()
        assert expected_airbyte_stream == airbyte_stream

    def test_as_airbyte_stream_with_a_cursor(self):
        json_schema = {
            "type": "object",
            "properties": {
                "id": {"type": ["null", "string"]},
                "date": {"type": ["null", "string"]},
            },
        }
        stream = ThreadBasedConcurrentStream(
            self._partition_generator,
            self._max_workers,
            self._name,
            json_schema,
            self._availability_strategy,
            self._primary_key,
            "date",
            self._slice_logger,
            self._logger,
            self._message_repository,
            1,
            2,
            0,
        )

        expected_airbyte_stream = AirbyteStream(
            name=self._name,
            json_schema=json_schema,
            supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
            source_defined_cursor=True,
            default_cursor_field=["date"],
            source_defined_primary_key=None,
            namespace=None,
        )

        airbyte_stream = stream.as_airbyte_stream()
        assert expected_airbyte_stream == airbyte_stream

    def test_as_airbyte_stream_with_namespace(self):
        stream = ThreadBasedConcurrentStream(
            self._partition_generator,
            self._max_workers,
            self._name,
            self._json_schema,
            self._availability_strategy,
            self._primary_key,
            self._cursor_field,
            self._slice_logger,
            self._logger,
            self._message_repository,
            1,
            2,
            0,
            namespace="test",
        )
        expected_airbyte_stream = AirbyteStream(
            name=self._name,
            json_schema=self._json_schema,
            supported_sync_modes=[SyncMode.full_refresh],
            source_defined_cursor=None,
            default_cursor_field=None,
            source_defined_primary_key=None,
            namespace="test",
        )
        actual_airbyte_stream = stream.as_airbyte_stream()

        assert expected_airbyte_stream == actual_airbyte_stream
