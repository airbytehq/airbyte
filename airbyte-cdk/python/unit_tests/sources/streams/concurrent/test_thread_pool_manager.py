#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from concurrent.futures import Future, ThreadPoolExecutor
from unittest import TestCase
from unittest.mock import Mock, patch

from airbyte_cdk.sources.concurrent_source.thread_pool_manager import ThreadPoolManager

_SLEEP_TIME = 2


class ThreadPoolManagerTest(TestCase):
    def setUp(self):
        self._threadpool = Mock(spec=ThreadPoolExecutor)
        self._thread_pool_manager = ThreadPoolManager(self._threadpool, Mock(), max_concurrent_tasks=1, sleep_time=_SLEEP_TIME)
        self._fn = lambda x: x
        self._arg = "arg"

    def test_submit_calls_underlying_thread_pool(self):
        self._thread_pool_manager.submit(self._fn, self._arg)
        self._threadpool.submit.assert_called_with(self._fn, self._arg)

        assert len(self._thread_pool_manager._futures) == 1

    def test_submit_too_many_concurrent_tasks(self):
        future = Mock(spec=Future)
        future.exception.return_value = None
        future.done.side_effect = [False, True]

        with patch("time.sleep") as sleep_mock:
            self._thread_pool_manager._futures = [future]
            self._thread_pool_manager.submit(self._fn, self._arg)
            self._threadpool.submit.assert_called_with(self._fn, self._arg)
            sleep_mock.assert_called_with(_SLEEP_TIME)

            assert len(self._thread_pool_manager._futures) == 1

    def test_submit_task_previous_task_failed(self):
        future = Mock(spec=Future)
        future.exception.return_value = RuntimeError
        future.done.side_effect = [False, True]

        self._thread_pool_manager._futures = [future]

        with self.assertRaises(RuntimeError):
            self._thread_pool_manager.submit(self._fn, self._arg)

    def test_shutdown(self):
        self._thread_pool_manager.shutdown()
        self._threadpool.shutdown.assert_called_with(wait=False, cancel_futures=True)

    def test_is_done_is_false_if_not_all_futures_are_done(self):
        future = Mock(spec=Future)
        future.done.return_value = False

        self._thread_pool_manager._futures = [future]

        assert not self._thread_pool_manager.is_done()

    def test_is_done_is_true_if_all_futures_are_done(self):
        future = Mock(spec=Future)
        future.done.return_value = True

        self._thread_pool_manager._futures = [future]

        assert self._thread_pool_manager.is_done()

    def test_threadpool_shutdown_if_errors(self):
        future = Mock(spec=Future)
        future.exception.return_value = RuntimeError

        self._thread_pool_manager._futures = [future]

        with self.assertRaises(RuntimeError):
            self._thread_pool_manager.check_for_errors_and_shutdown()
        self._threadpool.shutdown.assert_called_with(wait=False, cancel_futures=True)

    def test_check_for_errors_and_shutdown_raises_error_if_futures_are_not_done(self):
        future = Mock(spec=Future)
        future.exception.return_value = None
        future.done.return_value = False

        self._thread_pool_manager._futures = [future]

        with self.assertRaises(RuntimeError):
            self._thread_pool_manager.check_for_errors_and_shutdown()
        self._threadpool.shutdown.assert_called_with(wait=False, cancel_futures=True)

    def test_check_for_errors_and_shutdown_does_not_raise_error_if_futures_are_done(self):
        future = Mock(spec=Future)
        future.exception.return_value = None
        future.done.return_value = True

        self._thread_pool_manager._futures = [future]

        self._thread_pool_manager.check_for_errors_and_shutdown()
        self._threadpool.shutdown.assert_called_with(wait=False, cancel_futures=True)
