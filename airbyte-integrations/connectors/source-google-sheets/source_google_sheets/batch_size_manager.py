#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Optional, Union

import requests
from requests.status_codes import codes as status_codes

logger = logging.getLogger("airbyte")


class BatchSizeManager:
    _instance = None
    RATE_LIMIT_INCREASE = 100

    def __new__(cls, initial_batch_size=200):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.row_batch_size = initial_batch_size
        return cls._instance

    def get_batch_size(self) -> int:
        return self._instance.row_batch_size

    def increase_row_batch_size(self, response_or_exception: Optional[Union[requests.Response, Exception]]) -> None:
        if response_or_exception.status_code == status_codes.TOO_MANY_REQUESTS and self._instance.row_batch_size < 1000:
            self._instance.row_batch_size += BatchSizeManager.RATE_LIMIT_INCREASE
            logger.info(f"Increasing number of records fetching due to rate limits. Current value: {self._instance.row_batch_size}")

    @classmethod
    def reset(cls):
        cls._instance = None
