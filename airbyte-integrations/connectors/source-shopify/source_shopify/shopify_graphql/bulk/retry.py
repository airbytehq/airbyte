# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from functools import wraps
from time import sleep
from typing import Any, Callable, Final, Optional, Tuple, Type

from source_shopify.utils import LOGGER

from .exceptions import ShopifyBulkExceptions

BULK_RETRY_ERRORS: Final[Tuple] = (
    ShopifyBulkExceptions.BulkJobBadResponse,
    ShopifyBulkExceptions.BulkJobError,
)


def bulk_retry_on_exception(more_exceptions: Optional[Tuple[Type[Exception], ...]] = None) -> Callable:
    """
    A decorator to retry a function when specified exceptions are raised.

    :param more_exceptions: A tuple of exception types to catch.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            current_retries = 0
            while True:
                try:
                    return func(self, *args, **kwargs)
                except BULK_RETRY_ERRORS or more_exceptions as ex:
                    current_retries += 1
                    if current_retries > self._job_max_retries:
                        LOGGER.error("Exceeded retry limit. Giving up.")
                        raise
                    else:
                        LOGGER.warning(
                            f"Stream `{self.http_client.name}`: {ex}. Retrying {current_retries}/{self._job_max_retries} after {self._job_backoff_time} seconds."
                        )
                        sleep(self._job_backoff_time)
                except ShopifyBulkExceptions.BulkJobCreationFailedConcurrentError:
                    if self._concurrent_attempt == self._concurrent_max_retry:
                        message = f"The BULK Job couldn't be created at this time, since another job is running."
                        LOGGER.error(message)
                        raise ShopifyBulkExceptions.BulkJobConcurrentError(message)

                    self._concurrent_attempt += 1
                    LOGGER.warning(
                        f"Stream: `{self.http_client.name}`, the BULK concurrency limit has reached. Waiting {self._concurrent_interval} sec before retry, attempt: {self._concurrent_attempt}.",
                    )
                    sleep(self._concurrent_interval)
                except ShopifyBulkExceptions.BulkJobRedirectToOtherShopError:
                    LOGGER.warning(
                        f"Stream: `{self.http_client.name}`, the `shop name` differs from the provided in `input configuration`. Switching to the `{self._tools.shop_name_from_url(self.base_url)}`.",
                    )

        return wrapper

    return decorator
