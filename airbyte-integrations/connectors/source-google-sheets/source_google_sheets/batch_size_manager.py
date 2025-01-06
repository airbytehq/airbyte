#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import logging

logger = logging.getLogger("airbyte")

class BatchSizeManager:
    _instance = None

    def __new__(cls, initial_batch_size=200):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.batch_size = initial_batch_size
        return cls._instance

    def get_batch_size(self) -> int:
        return self._instance.batch_size

    def update_batch_size(self, new_batch_size: int) -> None:
        self._instance.batch_size = new_batch_size
        logger.info(f"Increasing number of records fetching due to rate limits. Current value: {self._instance.batch_size}")

    @classmethod
    def reset(cls):
        cls._instance = None
