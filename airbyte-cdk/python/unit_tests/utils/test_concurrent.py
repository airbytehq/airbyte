#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import time
from itertools import product
from unittest.mock import MagicMock

from airbyte_cdk.utils.concurrent import ConcurrentStreamReader


class Stream:
    max_workers = 5

    def stream_slices(self, **kwargs):
        yield from range(1, 11)

    def read_records(self, *, stream_slice, **kwargs):
        for record in range(1, 11):
            yield stream_slice, record
            # for thread context switching
            time.sleep(0.01)


def test_read_full_refresh():
    stream_instance = Stream()
    stream_instance.logger = MagicMock()
    records = []
    start_time = time.time()
    with ConcurrentStreamReader(stream_instance, MagicMock()) as reader:
        for record in reader:
            records.append(record)

    assert records == list(product(range(1, 11), range(1, 11)))
    assert 0 < time.time() - start_time < 0.25
