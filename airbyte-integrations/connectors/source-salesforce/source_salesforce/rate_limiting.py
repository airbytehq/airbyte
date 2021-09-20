#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


import sys

import backoff
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException
from requests import codes, exceptions

TRANSIENT_EXCEPTIONS = (
    DefaultBackoffException,
    exceptions.ConnectTimeout,
    exceptions.ReadTimeout,
    exceptions.ConnectionError,
    exceptions.HTTPError,
)

logger = AirbyteLogger()


def default_backoff_handler(max_tries: int, factor: int, **kwargs):
    def log_retry_attempt(details):
        _, exc, _ = sys.exc_info()
        logger.info(str(exc))
        logger.info(f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} seconds then retrying...")

    def should_give_up(exc):
        give_up = exc.response is not None and exc.response.status_code != codes.too_many_requests and 400 <= exc.response.status_code < 500

        # Salesforce can return an error with a limit using a 403 code error.
        if exc.response is not None and exc.response.status_code == codes.forbidden:
            error_data = exc.response.json()[0]
            if error_data.get("errorCode", "") == "REQUEST_LIMIT_EXCEEDED":
                give_up = False

        if give_up:
            logger.info(f"Giving up for returned HTTP status: {exc.response.status_code}")
        return give_up

    return backoff.on_exception(
        backoff.expo,
        TRANSIENT_EXCEPTIONS,
        jitter=None,
        on_backoff=log_retry_attempt,
        giveup=should_give_up,
        max_tries=max_tries,
        factor=factor,
        **kwargs,
    )
