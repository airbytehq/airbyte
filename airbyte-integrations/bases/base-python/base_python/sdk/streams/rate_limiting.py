import sys
import time

import backoff
from base_python.logger import AirbyteLogger
from requests import exceptions
from base_python.sdk.streams.exceptions import DefaultBackoffException, UserDefinedBackoffException

TRANSIENT_EXCEPTIONS = (DefaultBackoffException, exceptions.ConnectTimeout, exceptions.ReadTimeout, exceptions.ConnectionError)

# TODO inject singleton logger?
logger = AirbyteLogger()


def default_backoff_handler(max_tries: int, factor: int, **kwargs):
    def log_retry_attempt(details):
        _, exc, _ = sys.exc_info()
        logger.info(str(exc))
        logger.info(f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} seconds then retrying...")

    def should_give_up(exc):
        # If a 4XX error makes it this far, it means it was unexpected and probably consistent, so we shouldn't back off
        return exc.response is not None and 400 <= exc.response.status_code < 500

    return backoff.on_exception(
        backoff.expo,
        TRANSIENT_EXCEPTIONS,
        jitter=None,
        on_backoff=log_retry_attempt,
        giveup=should_give_up,
        max_tries=max_tries,
        factor=factor,
        **kwargs
    )


def user_defined_backoff_handler(max_tries: int, **kwargs):
    def sleep_on_ratelimit(details):
        _, exc, _ = sys.exc_info()
        if isinstance(exc, UserDefinedBackoffException):
            retry_after = exc.backoff
            logger.info(f"Retrying. Sleeping for {retry_after} seconds")
            time.sleep(retry_after + 1)  # extra second to cover any fractions of second

    def log_give_up(details):
        _, exc, _ = sys.exc_info()
        logger.error(f"Max retry limit reached. Request: {exc.request}, Response: {exc.response}")

    return backoff.on_exception(
        backoff.constant,
        UserDefinedBackoffException,
        interval=0,  # skip waiting, we'll wait in on_backoff handler
        on_backoff=sleep_on_ratelimit,
        on_giveup=log_give_up,
        jitter=None,
        max_tries=max_tries,
        **kwargs
    )
