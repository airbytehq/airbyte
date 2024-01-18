# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from unittest.mock import patch

from airbyte_cdk.sources.concurrent_source.throttler import Throttler


@patch('time.sleep', side_effect=lambda _: None)
@patch('airbyte_cdk.sources.concurrent_source.throttler.len', side_effect=[1, 1, 0])
def test_throttler(sleep_mock, len_mock):
    throttler = Throttler([], 0.1, 1)
    throttler.wait_and_acquire()
    assert sleep_mock.call_count == 3
