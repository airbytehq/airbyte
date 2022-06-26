#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from itertools import product
from unittest.mock import MagicMock

from airbyte_cdk.utils.concurrent import ConcurrentStreamReader


class Stream:
    max_workers = 5

    def stream_slices(self, **kwargs):
        yield from range(1, 20)

    def read_records(self, *, stream_slice, **kwargs):
        for record in range(1, 20):
            yield stream_slice, record


def test_read_full_refresh():
    stream_instance = Stream()
    stream_instance.logger = MagicMock()
    records = []
    with ConcurrentStreamReader(stream_instance, MagicMock()) as reader:
        for record in reader:
            records.append(record)

    assert records == list(product(range(1, 20), range(1, 20)))
