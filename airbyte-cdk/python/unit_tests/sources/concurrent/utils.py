#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from unittest import TestCase
from unittest.mock import Mock


class ConcurrentCdkTestCase(TestCase):
    def mock_stream(self, name: str, partitions, records_per_partition, *, available=True, debug_log=False):
        stream = Mock()
        stream.name = name
        stream.get_json_schema.return_value = {}
        stream.generate_partitions.return_value = iter(partitions)
        stream.stream_slices.return_value = iter(partitions)
        stream.read_records.side_effect = [iter(records) for records in records_per_partition]
        stream.logger.isEnabledFor.return_value = debug_log
        if available:
            stream.check_availability.return_value = True, None
        else:
            stream.check_availability.return_value = False, "A reason why the stream is unavailable"
        return stream
