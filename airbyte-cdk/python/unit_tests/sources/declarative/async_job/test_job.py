# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import time
from datetime import timedelta
from unittest import TestCase

from airbyte_cdk.sources.declarative.async_job.job import AsyncJob
from airbyte_cdk.sources.declarative.async_job.status import AsyncJobStatus
from airbyte_cdk.sources.declarative.types import StreamSlice

_AN_API_JOB_ID = "an api job id"
_ANY_STREAM_SLICE = StreamSlice(partition={}, cursor_slice={})
_A_VERY_BIG_TIMEOUT = timedelta(days=999999999)
_IMMEDIATELY_TIMED_OUT = timedelta(microseconds=1)


class AsyncJobTest(TestCase):
    def test_given_timer_is_not_out_when_status_then_return_actual_status(self) -> None:
        job = AsyncJob(_AN_API_JOB_ID, _ANY_STREAM_SLICE, _A_VERY_BIG_TIMEOUT)
        assert job.status() == AsyncJobStatus.RUNNING

    def test_given_timer_is_out_when_status_then_return_timed_out(self) -> None:
        job = AsyncJob(_AN_API_JOB_ID, _ANY_STREAM_SLICE, _IMMEDIATELY_TIMED_OUT)
        time.sleep(0.001)
        assert job.status() == AsyncJobStatus.TIMED_OUT

    def test_given_status_is_terminal_when_update_status_then_stop_timer(self) -> None:
        """
        This test will become important once we will print stats associated with jobs. As for now, we stop the timer but do not return any
        metrics regarding the timer so it is not useful.
        """
        pass
