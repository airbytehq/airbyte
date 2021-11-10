#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys
import time

import backoff
import requests
from base_python.entrypoint import logger
from source_freshdesk.errors import FreshdeskRateLimited


def retry_connection_handler(**kwargs):
    """Retry helper, log each attempt"""

    def log_retry_attempt(details):
        _, exc, _ = sys.exc_info()
        logger.info(str(exc))
        logger.info(f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} more seconds then retrying...")

    def giveup_handler(exc):
        return exc.response is not None and 400 <= exc.response.status_code < 500

    return backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        jitter=None,
        on_backoff=log_retry_attempt,
        giveup=giveup_handler,
        **kwargs,
    )


def retry_after_handler(**kwargs):
    """Retry helper when we hit the call limit, sleeps for specific duration"""

    def sleep_on_ratelimit(_details):
        _, exc, _ = sys.exc_info()
        if isinstance(exc, FreshdeskRateLimited):
            retry_after = int(exc.response.headers["Retry-After"])
            logger.info(f"Rate limit reached. Sleeping for {retry_after} seconds")
            time.sleep(retry_after + 1)  # extra second to cover any fractions of second

    def log_giveup(_details):
        logger.error("Max retry limit reached")

    return backoff.on_exception(
        backoff.constant,
        FreshdeskRateLimited,
        jitter=None,
        on_backoff=sleep_on_ratelimit,
        on_giveup=log_giveup,
        interval=0,  # skip waiting part, we will wait in on_backoff handler
        **kwargs,
    )


class CallCredit:
    """Class to manage call credit balance"""

    def __init__(self, balance: int, reload_period: int = 60):
        self._max_balance = balance
        self._balance_reload_period = reload_period
        self._current_period_start = time.time()
        self._credits_consumed = 0

    def reset_period(self):
        self._current_period_start = time.time()
        self._credits_consumed = 0

    def consume(self, credit: int):
        # Reset time window if it has elapsed
        if time.time() > self._current_period_start + self._balance_reload_period:
            self.reset_period()

        if self._credits_consumed + credit >= self._max_balance:
            sleep_time = self._balance_reload_period - (time.time() - self._current_period_start)
            logger.trace(f"Reached call limit for this minute, wait for {sleep_time:.2f} seconds")
            time.sleep(max(1.0, sleep_time))
            self.reset_period()

        self._credits_consumed += credit
