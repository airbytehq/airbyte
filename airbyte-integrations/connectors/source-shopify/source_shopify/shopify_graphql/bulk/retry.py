# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
from functools import wraps
from time import sleep
from typing import Any, Callable, Final, Optional, Tuple, Type

from .exceptions import ShopifyBulkExceptions

BULK_RETRY_ERRORS: Final[Tuple] = (
    ShopifyBulkExceptions.BulkJobBadResponse,
    ShopifyBulkExceptions.BulkJobError,
)


def bulk_retry_on_exception(logger: logging.Logger, more_exceptions: Optional[Tuple[Type[Exception], ...]] = None) -> Callable:
    """
    A decorator to retry a function when specified exceptions are raised.

    :param logger: Number of times to retry.
    :param more_exceptions: A tuple of exception types to catch.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            # mandatory class attributes
            max_retries = self._job_max_retries
            stream_name = self.stream_name
            backoff_time = self._job_backoff_time

            current_retries = 0
            while True:
                try:
                    return func(self, *args, **kwargs)
                except BULK_RETRY_ERRORS or more_exceptions as ex:
                    current_retries += 1
                    if current_retries > max_retries:
                        logger.error("Exceeded retry limit. Giving up.")
                        raise
                    else:
                        logger.warning(
                            f"Stream `{stream_name}`: {ex}. Retrying {current_retries}/{max_retries} after {backoff_time} seconds."
                        )
                        sleep(backoff_time)
                except ShopifyBulkExceptions.BulkJobCreationFailedConcurrentError:
                    if self._concurrent_attempt == self._concurrent_max_retry:
                        message = f"The BULK Job couldn't be created at this time, since another job is running."
                        logger.error(message)
                        raise ShopifyBulkExceptions.BulkJobConcurrentError(message)

                    self._concurrent_attempt += 1
                    logger.warning(
                        f"Stream: `{self.stream_name}`, the BULK concurrency limit has reached. Waiting {self._concurrent_interval} sec before retry, attempt: {self._concurrent_attempt}.",
                    )
                    sleep(self._concurrent_interval)

        return wrapper

    return decorator
