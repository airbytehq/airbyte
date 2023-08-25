#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock, call

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, AirbyteRecordMessage, Level, SyncMode
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.concurrent.synchronous_full_refresh_reader import SyncrhonousFullRefreshReader
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from unit_tests.sources.concurrent.utils import ConcurrentCdkTestCase


class SynchronousFullRefreshReaderTestCase(ConcurrentCdkTestCase):
    _NO_CURSOR_FIELD = None
    _DEFAULT_INTERNAL_CONFIG = InternalConfig()
    _STREAM_NAME = "STREAM"

    def setUp(self):
        self._logger = Mock()
        self._logger.isEnabledFor.return_value = False

    def test_full_refresh_read_a_single_slice_with_debug(self):
        self._logger.isEnabledFor.return_value = True
        reader = SyncrhonousFullRefreshReader()

        partition = {"partition": 1}
        partitions = [partition]

        records = [
            {"id": 1, "partition": 1},
            {"id": 2, "partition": 1},
        ]
        records_per_partition = [records]

        expected_records = [
            AirbyteMessage(
                type=MessageType.LOG,
                log=AirbyteLogMessage(
                    level=Level.INFO,
                    message='slice:{"partition": 1}',
                ),
            ),
            *records,
        ]

        stream = self.mock_stream(self._STREAM_NAME, partitions, records_per_partition)

        actual_records = list(reader.read_stream(stream, self._NO_CURSOR_FIELD, self._logger, self._DEFAULT_INTERNAL_CONFIG))

        assert expected_records == actual_records

    def test_full_refresh_read_a_single_slice(self):
        reader = SyncrhonousFullRefreshReader()

        partition = {"partition": 1}
        partitions = [partition]

        records = [
            {"id": 1, "partition": 1},
            {"id": 2, "partition": 1},
        ]
        records_per_partition = [records]

        expected_records = [*records]

        stream = self.mock_stream(self._STREAM_NAME, partitions, records_per_partition)

        actual_records = list(reader.read_stream(stream, self._NO_CURSOR_FIELD, self._logger, self._DEFAULT_INTERNAL_CONFIG))

        assert expected_records == actual_records

        expected_read_records_calls = [call(stream_slice=partition, sync_mode=SyncMode.full_refresh, cursor_field=self._NO_CURSOR_FIELD)]

        stream.read_records.assert_has_calls(expected_read_records_calls)

    def test_full_refresh_read_a_two_slices(self):
        reader = SyncrhonousFullRefreshReader()

        partition1 = {"partition": 1}
        partition2 = {"partition": 2}
        partitions = [partition1, partition2]

        records_partition_1 = [
            {"id": 1, "partition": 1},
            {"id": 2, "partition": 1},
        ]
        records_partition_2 = [
            {"id": 3, "partition": 2},
            {"id": 4, "partition": 2},
        ]
        records_per_partition = [records_partition_1, records_partition_2]

        expected_records = [
            *records_partition_1,
            *records_partition_2,
        ]

        stream = self.mock_stream(self._STREAM_NAME, partitions, records_per_partition)

        actual_records = list(reader.read_stream(stream, self._NO_CURSOR_FIELD, self._logger, self._DEFAULT_INTERNAL_CONFIG))

        assert expected_records == actual_records

        expected_read_records_calls = [
            call(stream_slice=partition1, sync_mode=SyncMode.full_refresh, cursor_field=self._NO_CURSOR_FIELD),
            call(stream_slice=partition2, sync_mode=SyncMode.full_refresh, cursor_field=self._NO_CURSOR_FIELD),
        ]

        stream.read_records.assert_has_calls(expected_read_records_calls)

    def test_only_read_up_to_limit(self):
        reader = SyncrhonousFullRefreshReader()

        internal_config = InternalConfig(_limit=1)

        partition = {"partition": 1}
        partitions = [partition]

        records = [
            {"id": 1, "partition": 1},
            {"id": 2, "partition": 1},
        ]
        records_per_partition = [records]

        expected_records = records[:-1]

        stream = self.mock_stream(self._STREAM_NAME, partitions, records_per_partition)

        actual_records = list(reader.read_stream(stream, self._NO_CURSOR_FIELD, self._logger, internal_config))

        assert expected_records == actual_records

        expected_read_records_calls = [call(stream_slice=partition, sync_mode=SyncMode.full_refresh, cursor_field=self._NO_CURSOR_FIELD)]

        stream.read_records.assert_has_calls(expected_read_records_calls)

    def test_limit_only_considers_data(self):
        reader = SyncrhonousFullRefreshReader()

        internal_config = InternalConfig(_limit=2)

        partition = {"partition": 1}
        partitions = [partition]

        records = [
            AirbyteMessage(
                type=MessageType.LOG,
                log=AirbyteLogMessage(
                    level=Level.INFO,
                    message="A_LOG_MESSAGE",
                ),
            ),
            {"id": 1, "partition": 1},
            AirbyteMessage(
                type=MessageType.LOG,
                log=AirbyteLogMessage(
                    level=Level.INFO,
                    message="ANOTHER_LOG_MESSAGE",
                ),
            ),
            AirbyteMessage(
                type=MessageType.RECORD,
                record=AirbyteRecordMessage(
                    data={"id": 2, "partition": 1},
                    stream=self._STREAM_NAME,
                    emitted_at=1,
                ),
            ),
            {"id": 2, "partition": 1},
        ]

        records_per_partition = [records]
        expected_records = records[:-1]

        stream = self.mock_stream(self._STREAM_NAME, partitions, records_per_partition)

        actual_records = list(reader.read_stream(stream, self._NO_CURSOR_FIELD, self._logger, internal_config))

        assert expected_records == actual_records

        expected_read_records_calls = [call(stream_slice=partition, sync_mode=SyncMode.full_refresh, cursor_field=self._NO_CURSOR_FIELD)]

        stream.read_records.assert_has_calls(expected_read_records_calls)
