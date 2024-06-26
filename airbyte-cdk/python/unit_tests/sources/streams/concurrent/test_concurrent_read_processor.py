#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
import unittest
from unittest.mock import Mock, call

import freezegun
import pytest
from airbyte_cdk.models import (
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    AirbyteStreamStatus,
    AirbyteStreamStatusTraceMessage,
    AirbyteTraceMessage,
)
from airbyte_cdk.models import Level as LogLevel
from airbyte_cdk.models import StreamDescriptor, SyncMode, TraceType
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.concurrent_source.concurrent_read_processor import ConcurrentReadProcessor
from airbyte_cdk.sources.concurrent_source.partition_generation_completed_sentinel import PartitionGenerationCompletedSentinel
from airbyte_cdk.sources.concurrent_source.stream_thread_exception import StreamThreadException
from airbyte_cdk.sources.concurrent_source.thread_pool_manager import ThreadPoolManager
from airbyte_cdk.sources.message import LogMessage, MessageRepository
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.partition_enqueuer import PartitionEnqueuer
from airbyte_cdk.sources.streams.concurrent.partition_reader import PartitionReader
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.concurrent.partitions.types import PartitionCompleteSentinel
from airbyte_cdk.sources.utils.slice_logger import SliceLogger
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

_STREAM_NAME = "stream"
_ANOTHER_STREAM_NAME = "stream2"
_ANY_AIRBYTE_MESSAGE = Mock(spec=AirbyteMessage)
_IS_SUCCESSFUL = True


class TestConcurrentReadProcessor(unittest.TestCase):
    def setUp(self):
        self._partition_enqueuer = Mock(spec=PartitionEnqueuer)
        self._thread_pool_manager = Mock(spec=ThreadPoolManager)

        self._an_open_partition = Mock(spec=Partition)
        self._log_message = Mock(spec=LogMessage)
        self._an_open_partition.to_slice.return_value = self._log_message
        self._an_open_partition.stream_name.return_value = _STREAM_NAME

        self._a_closed_partition = Mock(spec=Partition)
        self._a_closed_partition.stream_name.return_value = _ANOTHER_STREAM_NAME

        self._logger = Mock(spec=logging.Logger)
        self._slice_logger = Mock(spec=SliceLogger)
        self._slice_logger.create_slice_log_message.return_value = self._log_message
        self._message_repository = Mock(spec=MessageRepository)
        self._message_repository.consume_queue.return_value = []
        self._partition_reader = Mock(spec=PartitionReader)

        self._stream = Mock(spec=AbstractStream)
        self._stream.name = _STREAM_NAME
        self._stream.as_airbyte_stream.return_value = AirbyteStream(
            name=_STREAM_NAME,
            json_schema={},
            supported_sync_modes=[SyncMode.full_refresh],
        )
        self._another_stream = Mock(spec=AbstractStream)
        self._another_stream.name = _ANOTHER_STREAM_NAME
        self._another_stream.as_airbyte_stream.return_value = AirbyteStream(
            name=_ANOTHER_STREAM_NAME,
            json_schema={},
            supported_sync_modes=[SyncMode.full_refresh],
        )

        self._record_data = {"id": 1, "value": "A"}
        self._record = Mock(spec=Record)
        self._record.stream_name = _STREAM_NAME
        self._record.data = self._record_data

    def test_stream_is_not_done_initially(self):
        stream_instances_to_read_from = [self._stream]
        handler = ConcurrentReadProcessor(
            stream_instances_to_read_from,
            self._partition_enqueuer,
            self._thread_pool_manager,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )
        assert not handler._is_stream_done(self._stream.name)

    def test_handle_partition_done_no_other_streams_to_generate_partitions_for(self):
        stream_instances_to_read_from = [self._stream]

        handler = ConcurrentReadProcessor(
            stream_instances_to_read_from,
            self._partition_enqueuer,
            self._thread_pool_manager,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )
        handler.start_next_partition_generator()
        handler.on_partition(self._an_open_partition)

        sentinel = PartitionGenerationCompletedSentinel(self._stream)
        messages = list(handler.on_partition_generation_completed(sentinel))

        expected_messages = []
        assert messages == expected_messages

    @freezegun.freeze_time("2020-01-01T00:00:00")
    def test_handle_last_stream_partition_done(self):
        in_order_validation_mock = Mock()
        in_order_validation_mock.attach_mock(self._another_stream, "_another_stream")
        in_order_validation_mock.attach_mock(self._message_repository, "_message_repository")
        self._message_repository.consume_queue.return_value = iter([_ANY_AIRBYTE_MESSAGE])
        stream_instances_to_read_from = [self._another_stream]

        handler = ConcurrentReadProcessor(
            stream_instances_to_read_from,
            self._partition_enqueuer,
            self._thread_pool_manager,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )
        handler.start_next_partition_generator()

        sentinel = PartitionGenerationCompletedSentinel(self._another_stream)
        messages = list(handler.on_partition_generation_completed(sentinel))

        expected_messages = [
            _ANY_AIRBYTE_MESSAGE,
            AirbyteMessage(
                type=MessageType.TRACE,
                trace=AirbyteTraceMessage(
                    type=TraceType.STREAM_STATUS,
                    emitted_at=1577836800000.0,
                    stream_status=AirbyteStreamStatusTraceMessage(
                        stream_descriptor=StreamDescriptor(name=_ANOTHER_STREAM_NAME),
                        status=AirbyteStreamStatus(AirbyteStreamStatus.COMPLETE),
                    ),
                ),
            ),
        ]
        assert messages == expected_messages
        assert in_order_validation_mock.mock_calls.index(
            call._another_stream.cursor.ensure_at_least_one_state_emitted
        ) < in_order_validation_mock.mock_calls.index(call._message_repository.consume_queue)

    def test_handle_partition(self):
        stream_instances_to_read_from = [self._another_stream]

        handler = ConcurrentReadProcessor(
            stream_instances_to_read_from,
            self._partition_enqueuer,
            self._thread_pool_manager,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )

        handler.on_partition(self._a_closed_partition)

        self._thread_pool_manager.submit.assert_called_with(self._partition_reader.process_partition, self._a_closed_partition)
        assert self._a_closed_partition in handler._streams_to_running_partitions[_ANOTHER_STREAM_NAME]

    def test_handle_partition_emits_log_message_if_it_should_be_logged(self):
        stream_instances_to_read_from = [self._stream]
        self._slice_logger = Mock(spec=SliceLogger)
        self._slice_logger.should_log_slice_message.return_value = True
        self._slice_logger.create_slice_log_message.return_value = self._log_message

        handler = ConcurrentReadProcessor(
            stream_instances_to_read_from,
            self._partition_enqueuer,
            self._thread_pool_manager,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )

        handler.on_partition(self._an_open_partition)

        self._thread_pool_manager.submit.assert_called_with(self._partition_reader.process_partition, self._an_open_partition)
        self._message_repository.emit_message.assert_called_with(self._log_message)

        assert self._an_open_partition in handler._streams_to_running_partitions[_STREAM_NAME]

    @freezegun.freeze_time("2020-01-01T00:00:00")
    def test_handle_on_partition_complete_sentinel_with_messages_from_repository(self):
        stream_instances_to_read_from = [self._stream]
        partition = Mock(spec=Partition)
        log_message = Mock(spec=LogMessage)
        partition.to_slice.return_value = log_message
        partition.stream_name.return_value = _STREAM_NAME

        handler = ConcurrentReadProcessor(
            stream_instances_to_read_from,
            self._partition_enqueuer,
            self._thread_pool_manager,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )
        handler.start_next_partition_generator()
        handler.on_partition(partition)

        sentinel = PartitionCompleteSentinel(partition)

        self._message_repository.consume_queue.return_value = [
            AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=LogLevel.INFO, message="message emitted from the repository"))
        ]

        messages = list(handler.on_partition_complete_sentinel(sentinel))

        expected_messages = [
            AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=LogLevel.INFO, message="message emitted from the repository"))
        ]
        assert messages == expected_messages

        partition.close.assert_called_once()

    @freezegun.freeze_time("2020-01-01T00:00:00")
    def test_handle_on_partition_complete_sentinel_yields_status_message_if_the_stream_is_done(self):
        self._streams_currently_generating_partitions = [self._another_stream]
        stream_instances_to_read_from = [self._another_stream]
        log_message = Mock(spec=LogMessage)
        self._a_closed_partition.to_slice.return_value = log_message
        self._message_repository.consume_queue.return_value = []

        handler = ConcurrentReadProcessor(
            stream_instances_to_read_from,
            self._partition_enqueuer,
            self._thread_pool_manager,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )
        handler.start_next_partition_generator()
        handler.on_partition(self._a_closed_partition)
        list(handler.on_partition_generation_completed(PartitionGenerationCompletedSentinel(self._another_stream)))

        sentinel = PartitionCompleteSentinel(self._a_closed_partition)

        messages = list(handler.on_partition_complete_sentinel(sentinel))

        expected_messages = [
            AirbyteMessage(
                type=MessageType.TRACE,
                trace=AirbyteTraceMessage(
                    type=TraceType.STREAM_STATUS,
                    stream_status=AirbyteStreamStatusTraceMessage(
                        stream_descriptor=StreamDescriptor(
                            name=_ANOTHER_STREAM_NAME,
                        ),
                        status=AirbyteStreamStatus.COMPLETE,
                    ),
                    emitted_at=1577836800000.0,
                ),
            )
        ]
        assert messages == expected_messages
        self._a_closed_partition.close.assert_called_once()

    @freezegun.freeze_time("2020-01-01T00:00:00")
    def test_given_exception_on_partition_complete_sentinel_then_yield_error_trace_message_and_stream_is_incomplete(self) -> None:
        self._a_closed_partition.stream_name.return_value = self._stream.name
        self._a_closed_partition.close.side_effect = ValueError

        handler = ConcurrentReadProcessor(
            [self._stream],
            self._partition_enqueuer,
            self._thread_pool_manager,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )
        handler.start_next_partition_generator()
        handler.on_partition(self._a_closed_partition)
        list(handler.on_partition_generation_completed(PartitionGenerationCompletedSentinel(self._stream)))
        messages = list(handler.on_partition_complete_sentinel(PartitionCompleteSentinel(self._a_closed_partition)))

        expected_status_message = AirbyteMessage(
            type=MessageType.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(
                        name=self._stream.name,
                    ),
                    status=AirbyteStreamStatus.INCOMPLETE,
                ),
                emitted_at=1577836800000.0,
            ),
        )
        assert list(map(lambda message: message.trace.type, messages)) == [TraceType.ERROR, TraceType.STREAM_STATUS]
        assert messages[1] == expected_status_message

    @freezegun.freeze_time("2020-01-01T00:00:00")
    def test_handle_on_partition_complete_sentinel_yields_no_status_message_if_the_stream_is_not_done(self):
        stream_instances_to_read_from = [self._stream]
        partition = Mock(spec=Partition)
        log_message = Mock(spec=LogMessage)
        partition.to_slice.return_value = log_message
        partition.stream_name.return_value = _STREAM_NAME

        handler = ConcurrentReadProcessor(
            stream_instances_to_read_from,
            self._partition_enqueuer,
            self._thread_pool_manager,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )
        handler.start_next_partition_generator()

        sentinel = PartitionCompleteSentinel(partition)

        messages = list(handler.on_partition_complete_sentinel(sentinel))

        expected_messages = []
        assert messages == expected_messages
        partition.close.assert_called_once()

    @freezegun.freeze_time("2020-01-01T00:00:00")
    def test_on_record_no_status_message_no_repository_messge(self):
        stream_instances_to_read_from = [self._stream]
        partition = Mock(spec=Partition)
        log_message = Mock(spec=LogMessage)
        partition.to_slice.return_value = log_message
        partition.stream_name.return_value = _STREAM_NAME
        self._message_repository.consume_queue.return_value = []

        handler = ConcurrentReadProcessor(
            stream_instances_to_read_from,
            self._partition_enqueuer,
            self._thread_pool_manager,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )

        # Simulate a first record
        list(handler.on_record(self._record))

        messages = list(handler.on_record(self._record))

        expected_messages = [
            AirbyteMessage(
                type=MessageType.RECORD,
                record=AirbyteRecordMessage(
                    stream=_STREAM_NAME,
                    data=self._record_data,
                    emitted_at=1577836800000,
                ),
            )
        ]
        assert messages == expected_messages

    @freezegun.freeze_time("2020-01-01T00:00:00")
    def test_on_record_with_repository_messge(self):
        stream_instances_to_read_from = [self._stream]
        partition = Mock(spec=Partition)
        log_message = Mock(spec=LogMessage)
        partition.to_slice.return_value = log_message
        partition.stream_name.return_value = _STREAM_NAME
        slice_logger = Mock(spec=SliceLogger)
        slice_logger.should_log_slice_message.return_value = True
        slice_logger.create_slice_log_message.return_value = log_message
        self._message_repository.consume_queue.return_value = [
            AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=LogLevel.INFO, message="message emitted from the repository"))
        ]

        handler = ConcurrentReadProcessor(
            stream_instances_to_read_from,
            self._partition_enqueuer,
            self._thread_pool_manager,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )

        stream = Mock(spec=AbstractStream)
        stream.name = _STREAM_NAME
        stream.as_airbyte_stream.return_value = AirbyteStream(
            name=_STREAM_NAME,
            json_schema={},
            supported_sync_modes=[SyncMode.full_refresh],
        )

        # Simulate a first record
        list(handler.on_record(self._record))

        messages = list(handler.on_record(self._record))

        expected_messages = [
            AirbyteMessage(
                type=MessageType.RECORD,
                record=AirbyteRecordMessage(
                    stream=_STREAM_NAME,
                    data=self._record_data,
                    emitted_at=1577836800000,
                ),
            ),
            AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=LogLevel.INFO, message="message emitted from the repository")),
        ]
        assert messages == expected_messages
        assert handler._record_counter[_STREAM_NAME] == 2

    @freezegun.freeze_time("2020-01-01T00:00:00")
    def test_on_record_emits_status_message_on_first_record_no_repository_message(self):
        self._streams_currently_generating_partitions = [_STREAM_NAME]
        stream_instances_to_read_from = [self._stream]
        partition = Mock(spec=Partition)
        partition.stream_name.return_value = _STREAM_NAME

        handler = ConcurrentReadProcessor(
            stream_instances_to_read_from,
            self._partition_enqueuer,
            self._thread_pool_manager,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )

        messages = list(handler.on_record(self._record))

        expected_messages = [
            AirbyteMessage(
                type=MessageType.TRACE,
                trace=AirbyteTraceMessage(
                    type=TraceType.STREAM_STATUS,
                    emitted_at=1577836800000.0,
                    stream_status=AirbyteStreamStatusTraceMessage(
                        stream_descriptor=StreamDescriptor(name=_STREAM_NAME), status=AirbyteStreamStatus(AirbyteStreamStatus.RUNNING)
                    ),
                ),
            ),
            AirbyteMessage(
                type=MessageType.RECORD,
                record=AirbyteRecordMessage(
                    stream=_STREAM_NAME,
                    data=self._record_data,
                    emitted_at=1577836800000,
                ),
            ),
        ]
        assert messages == expected_messages

    @freezegun.freeze_time("2020-01-01T00:00:00")
    def test_on_record_emits_status_message_on_first_record_with_repository_message(self):
        stream_instances_to_read_from = [self._stream]
        partition = Mock(spec=Partition)
        log_message = Mock(spec=LogMessage)
        partition.to_slice.return_value = log_message
        partition.stream_name.return_value = _STREAM_NAME
        self._message_repository.consume_queue.return_value = [
            AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=LogLevel.INFO, message="message emitted from the repository"))
        ]

        handler = ConcurrentReadProcessor(
            stream_instances_to_read_from,
            self._partition_enqueuer,
            self._thread_pool_manager,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )

        stream = Mock(spec=AbstractStream)
        stream.name = _STREAM_NAME
        stream.as_airbyte_stream.return_value = AirbyteStream(
            name=_STREAM_NAME,
            json_schema={},
            supported_sync_modes=[SyncMode.full_refresh],
        )

        messages = list(handler.on_record(self._record))

        expected_messages = [
            AirbyteMessage(
                type=MessageType.TRACE,
                trace=AirbyteTraceMessage(
                    type=TraceType.STREAM_STATUS,
                    emitted_at=1577836800000.0,
                    stream_status=AirbyteStreamStatusTraceMessage(
                        stream_descriptor=StreamDescriptor(name=_STREAM_NAME), status=AirbyteStreamStatus(AirbyteStreamStatus.RUNNING)
                    ),
                ),
            ),
            AirbyteMessage(
                type=MessageType.RECORD,
                record=AirbyteRecordMessage(
                    stream=_STREAM_NAME,
                    data=self._record_data,
                    emitted_at=1577836800000,
                ),
            ),
            AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=LogLevel.INFO, message="message emitted from the repository")),
        ]
        assert messages == expected_messages

    @freezegun.freeze_time("2020-01-01T00:00:00")
    def test_on_exception_return_trace_message_and_on_stream_complete_return_stream_status(self):
        stream_instances_to_read_from = [self._stream, self._another_stream]

        handler = ConcurrentReadProcessor(
            stream_instances_to_read_from,
            self._partition_enqueuer,
            self._thread_pool_manager,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )

        handler.start_next_partition_generator()
        handler.on_partition(self._an_open_partition)
        list(handler.on_partition_generation_completed(PartitionGenerationCompletedSentinel(self._stream)))
        list(handler.on_partition_generation_completed(PartitionGenerationCompletedSentinel(self._another_stream)))

        another_stream = Mock(spec=AbstractStream)
        another_stream.name = _STREAM_NAME
        another_stream.as_airbyte_stream.return_value = AirbyteStream(
            name=_ANOTHER_STREAM_NAME,
            json_schema={},
            supported_sync_modes=[SyncMode.full_refresh],
        )

        exception = StreamThreadException(RuntimeError("Something went wrong"), _STREAM_NAME)

        exception_messages = list(handler.on_exception(exception))
        assert len(exception_messages) == 1
        assert "StreamThreadException" in exception_messages[0].trace.error.stack_trace

        assert list(handler.on_partition_complete_sentinel(PartitionCompleteSentinel(self._an_open_partition))) == [
            AirbyteMessage(
                type=MessageType.TRACE,
                trace=AirbyteTraceMessage(
                    type=TraceType.STREAM_STATUS,
                    emitted_at=1577836800000.0,
                    stream_status=AirbyteStreamStatusTraceMessage(
                        stream_descriptor=StreamDescriptor(name=_STREAM_NAME), status=AirbyteStreamStatus(AirbyteStreamStatus.INCOMPLETE)
                    ),
                ),
            )
        ]
        with pytest.raises(AirbyteTracedException):
            handler.is_done()

    @freezegun.freeze_time("2020-01-01T00:00:00")
    def test_given_underlying_exception_is_traced_exception_on_exception_return_trace_message_and_on_stream_complete_return_stream_status(self):
        stream_instances_to_read_from = [self._stream, self._another_stream]

        handler = ConcurrentReadProcessor(
            stream_instances_to_read_from,
            self._partition_enqueuer,
            self._thread_pool_manager,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )

        handler.start_next_partition_generator()
        handler.on_partition(self._an_open_partition)
        list(handler.on_partition_generation_completed(PartitionGenerationCompletedSentinel(self._stream)))
        list(handler.on_partition_generation_completed(PartitionGenerationCompletedSentinel(self._another_stream)))

        another_stream = Mock(spec=AbstractStream)
        another_stream.name = _STREAM_NAME
        another_stream.as_airbyte_stream.return_value = AirbyteStream(
            name=_ANOTHER_STREAM_NAME,
            json_schema={},
            supported_sync_modes=[SyncMode.full_refresh],
        )

        underlying_exception = AirbyteTracedException()
        exception = StreamThreadException(underlying_exception, _STREAM_NAME)

        exception_messages = list(handler.on_exception(exception))
        assert len(exception_messages) == 1
        assert "AirbyteTracedException" in exception_messages[0].trace.error.stack_trace

        assert list(handler.on_partition_complete_sentinel(PartitionCompleteSentinel(self._an_open_partition))) == [
            AirbyteMessage(
                type=MessageType.TRACE,
                trace=AirbyteTraceMessage(
                    type=TraceType.STREAM_STATUS,
                    emitted_at=1577836800000.0,
                    stream_status=AirbyteStreamStatusTraceMessage(
                        stream_descriptor=StreamDescriptor(name=_STREAM_NAME), status=AirbyteStreamStatus(AirbyteStreamStatus.INCOMPLETE)
                    ),
                ),
            )
        ]
        with pytest.raises(AirbyteTracedException):
            handler.is_done()

    def test_given_partition_completion_is_not_success_then_do_not_close_partition(self):
        stream_instances_to_read_from = [self._stream, self._another_stream]

        handler = ConcurrentReadProcessor(
            stream_instances_to_read_from,
            self._partition_enqueuer,
            self._thread_pool_manager,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )

        handler.start_next_partition_generator()
        handler.on_partition(self._an_open_partition)
        list(handler.on_partition_generation_completed(PartitionGenerationCompletedSentinel(self._stream)))

        list(handler.on_partition_complete_sentinel(PartitionCompleteSentinel(self._an_open_partition, not _IS_SUCCESSFUL)))

        assert self._an_open_partition.close.call_count == 0

    def test_given_partition_completion_is_not_success_then_do_not_close_partition(self):
        stream_instances_to_read_from = [self._stream, self._another_stream]

        handler = ConcurrentReadProcessor(
            stream_instances_to_read_from,
            self._partition_enqueuer,
            self._thread_pool_manager,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )

        handler.start_next_partition_generator()
        handler.on_partition(self._an_open_partition)
        list(handler.on_partition_generation_completed(PartitionGenerationCompletedSentinel(self._stream)))

        list(handler.on_partition_complete_sentinel(PartitionCompleteSentinel(self._an_open_partition, not _IS_SUCCESSFUL)))

        assert self._an_open_partition.close.call_count == 0

    def test_is_done_is_false_if_there_are_any_instances_to_read_from(self):
        stream_instances_to_read_from = [self._stream]

        handler = ConcurrentReadProcessor(
            stream_instances_to_read_from,
            self._partition_enqueuer,
            self._thread_pool_manager,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )

        assert not handler.is_done()

    def test_is_done_is_false_if_there_are_streams_still_generating_partitions(self):
        stream_instances_to_read_from = [self._stream]

        handler = ConcurrentReadProcessor(
            stream_instances_to_read_from,
            self._partition_enqueuer,
            self._thread_pool_manager,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )

        handler.start_next_partition_generator()

        assert not handler.is_done()

    def test_is_done_is_false_if_all_partitions_are_not_closed(self):
        stream_instances_to_read_from = [self._stream]

        handler = ConcurrentReadProcessor(
            stream_instances_to_read_from,
            self._partition_enqueuer,
            self._thread_pool_manager,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )

        handler.start_next_partition_generator()
        handler.on_partition(self._an_open_partition)
        handler.on_partition_generation_completed(PartitionGenerationCompletedSentinel(self._stream))

        assert not handler.is_done()

    def test_is_done_is_true_if_all_partitions_are_closed_and_no_streams_are_generating_partitions_and_none_are_still_to_run(self):
        stream_instances_to_read_from = []

        handler = ConcurrentReadProcessor(
            stream_instances_to_read_from,
            self._partition_enqueuer,
            self._thread_pool_manager,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )

        assert handler.is_done()

    @freezegun.freeze_time("2020-01-01T00:00:00")
    def test_start_next_partition_generator(self):
        stream_instances_to_read_from = [self._stream]
        handler = ConcurrentReadProcessor(
            stream_instances_to_read_from,
            self._partition_enqueuer,
            self._thread_pool_manager,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )

        status_message = handler.start_next_partition_generator()

        assert status_message == AirbyteMessage(
            type=MessageType.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                emitted_at=1577836800000.0,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(name=_STREAM_NAME), status=AirbyteStreamStatus(AirbyteStreamStatus.STARTED)
                ),
            ),
        )

        assert _STREAM_NAME in handler._streams_currently_generating_partitions
        self._thread_pool_manager.submit.assert_called_with(self._partition_enqueuer.generate_partitions, self._stream)
