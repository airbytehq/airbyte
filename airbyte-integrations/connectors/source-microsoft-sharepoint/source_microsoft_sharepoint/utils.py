# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


import time
from datetime import datetime
from enum import Enum
from http import HTTPStatus

from airbyte_cdk import AirbyteTracedException, FailureType
from airbyte_cdk.sources.file_based.remote_file import RemoteFile


class SearchScope(Enum):
    OWN_DRIVES = "OWN_DRIVES"
    SHARED_ITEMS = "SHARED_ITEMS"
    BOTH = "BOTH"


class MicrosoftSharePointRemoteFile(RemoteFile):
    download_url: str


def filter_http_urls(files, logger):
    for file in files:
        if file.download_url.startswith("http") and not file.download_url.startswith("https"):  # ignore-https-check
            logger.error(f"Cannot open file {file.uri}. The URL returned by SharePoint is not secure.")
        else:
            yield file


def execute_query_with_retry(obj, max_retries=5, initial_retry_after=5, max_retry_after=300, max_total_wait_time=600):
    """
    Executes a query with retry logic on encountering specific HTTP errors.

    This function attempts to execute `obj.execute_query()` method, applying exponential backoff
    retry logic for HTTP status codes 429 (Too Many Requests) and 503 (Service Unavailable). It
    respects the 'Retry-After' header from the response, if present.

    Parameters:
        obj (object): The object that has the `execute_query` method to be executed.
        max_retries (int): Maximum number of retry attempts. Defaults to 5.
        initial_retry_after (int): Initial waiting time (in seconds) before the first retry. Defaults to 5 seconds.
        max_retry_after (int): Maximum waiting time (in seconds) between retries. Defaults to 300 seconds.
        max_total_wait_time (int): Maximum total waiting time (in seconds) for all retries. Defaults to 600 seconds.

    Raises:
        AirbyteTracedException: If the maximum total wait time or the maximum number of retries is exceeded.

    Returns:
        The result of `obj.execute_query()` if successful within the retry constraints.
    """
    retries = 0
    start_time = datetime.now()
    retry_after = initial_retry_after

    while retries < max_retries:
        try:
            return obj.execute_query()
        except Exception as ex:
            if hasattr(ex, "response") and ex.response.status_code in (HTTPStatus.TOO_MANY_REQUESTS, HTTPStatus.SERVICE_UNAVAILABLE):
                current_time = datetime.now()
                elapsed_time = (current_time - start_time).total_seconds()

                retry_after_header = ex.response.headers.get("Retry-After", None)
                if retry_after_header:
                    retry_after = int(retry_after_header)

                if elapsed_time + retry_after > max_total_wait_time:
                    message = (
                        f"Maximum total wait time of {max_total_wait_time} seconds exceeded for execute_query. "
                        f"The latest response status code is {ex.response.status_code}."
                    )
                    if retry_after_header:
                        message += f" Retry-After header: {retry_after_header}"
                    raise AirbyteTracedException(message, message, failure_type=FailureType.system_error)

                time.sleep(retry_after)
                retries += 1
                retry_after = min(retry_after * 2, max_retry_after)  # Double the wait time for next retry, up to a max limit
            else:
                # Re-raise exceptions that are not related to rate limits or service availability
                raise AirbyteTracedException.from_exception(ex, message="Caught unexpected exception")

    message = f"Maximum number of retries of {max_retries} exceeded for execute_query."
    raise AirbyteTracedException(message, message, failure_type=FailureType.system_error)
