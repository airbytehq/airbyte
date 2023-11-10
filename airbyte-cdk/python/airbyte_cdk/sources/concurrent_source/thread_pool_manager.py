#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
import time
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, Callable, List


class ThreadPoolManager:
    """
    Wrapper to abstract away the threadpool and the logic to wait for pending tasks to be completed.
    """

    DEFAULT_SLEEP_TIME = 0.1
    DEFAULT_MAX_QUEUE_SIZE = 10_000

    def __init__(
        self,
        threadpool: ThreadPoolExecutor,
        logger: logging.Logger,
        max_concurrent_tasks: int = DEFAULT_MAX_QUEUE_SIZE,
        sleep_time: float = DEFAULT_SLEEP_TIME,
    ):
        """
        :param threadpool: The threadpool to use
        :param logger: The logger to use
        :param max_concurrent_tasks: The maximum number of tasks that can be pending at the same time
        :param sleep_time: How long to sleep if there are too many pending tasks
        """
        self._threadpool = threadpool
        self._logger = logger
        self._max_concurrent_tasks = max_concurrent_tasks
        self._sleep_time = sleep_time
        self._futures: List[Future[Any]] = []

    def submit(self, function: Callable[..., Any], *args: Any) -> None:
        # Submit a task to the threadpool, waiting if there are too many pending tasks
        self._wait_while_too_many_pending_futures(self._futures)
        self._futures.append(self._threadpool.submit(function, *args))

    def _wait_while_too_many_pending_futures(self, futures: List[Future[Any]]) -> None:
        # Wait until the number of pending tasks is < self._max_concurrent_tasks
        while True:
            self._prune_futures(futures)
            if len(futures) < self._max_concurrent_tasks:
                break
            self._logger.info("Main thread is sleeping because the task queue is full...")
            time.sleep(self._sleep_time)

    def _prune_futures(self, futures: List[Future[Any]]) -> None:
        """
        Take a list in input and remove the futures that are completed. If a future has an exception, it'll raise and kill the stream
        operation.

        Pruning this list safely relies on the assumptions that only the main thread can modify the list of futures.
        """
        if len(futures) < self._max_concurrent_tasks:
            return

        for index in reversed(range(len(futures))):
            future = futures[index]
            optional_exception = future.exception()
            if optional_exception:
                exception = RuntimeError(f"Failed reading with error: {optional_exception}")
                self._stop_and_raise_exception(exception)

            if future.done():
                futures.pop(index)

    def shutdown(self) -> None:
        self._threadpool.shutdown(wait=False, cancel_futures=True)

    def is_done(self) -> bool:
        return all([f.done() for f in self._futures])

    def check_for_errors_and_shutdown(self) -> None:
        """
        Check if any of the futures have an exception, and raise it if so. If all futures are done, shutdown the threadpool.
        If the futures are not done, raise an exception.
        :return:
        """
        exceptions_from_futures = [f for f in [future.exception() for future in self._futures] if f is not None]
        if exceptions_from_futures:
            exception = RuntimeError(f"Failed reading with errors: {exceptions_from_futures}")
            self._stop_and_raise_exception(exception)
        else:
            futures_not_done = [f for f in self._futures if not f.done()]
            if futures_not_done:
                exception = RuntimeError(f"Failed reading with futures not done: {futures_not_done}")
                self._stop_and_raise_exception(exception)
            else:
                self.shutdown()

    def _stop_and_raise_exception(self, exception: BaseException) -> None:
        self.shutdown()
        raise exception
