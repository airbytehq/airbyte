# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import time
from concurrent.futures import Future
from typing import Any, List


class Throttler:
    """
    A throttler that waits until the number of concurrent tasks is below a certain threshold.
    """

    def __init__(self, futures_list: List[Future[Any]], sleep_time: float, max_concurrent_tasks: int):
        """
        :param futures_list: The list of futures to monitor
        :param sleep_time: How long to sleep if there are too many pending tasks
        :param max_concurrent_tasks: The maximum number of tasks that can be pending at the same time
        """
        self._futures_list = futures_list
        self._sleep_time = sleep_time
        self._max_concurrent_tasks = max_concurrent_tasks

    def wait_and_acquire(self) -> None:
        while len(self._futures_list) >= self._max_concurrent_tasks:
            time.sleep(self._sleep_time)
