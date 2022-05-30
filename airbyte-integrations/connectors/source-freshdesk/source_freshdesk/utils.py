#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import time

from airbyte_cdk.entrypoint import logger


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
            logger.info(f"Reached call limit for this minute, wait for {sleep_time:.2f} seconds")
            time.sleep(max(1.0, sleep_time))
            self.reset_period()

        self._credits_consumed += credit
