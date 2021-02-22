"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sys

import backoff
from base_python.entrypoint import logger  # FIXME (Eugene K): register logger as standard python logger
from facebook_business.exceptions import FacebookRequestError

FACEBOOK_UNKNOWN_ERROR_CODE = 99


class FacebookAPIException(Exception):
    """General class for all API errors"""


class JobTimeoutException(Exception):
    """Scheduled job timed out"""


def retry_pattern(backoff_type, exception, **wait_gen_kwargs):
    def log_retry_attempt(details):
        _, exc, _ = sys.exc_info()
        logger.info(str(exc))
        logger.info(f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} more seconds then retrying...")

    def should_retry_api_error(exc):
        if isinstance(exc, FacebookRequestError):
            return exc.api_transient_error() or exc.api_error_subcode() == FACEBOOK_UNKNOWN_ERROR_CODE
        return False

    return backoff.on_exception(
        backoff_type,
        exception,
        jitter=None,
        on_backoff=log_retry_attempt,
        giveup=lambda exc: not should_retry_api_error(exc),
        **wait_gen_kwargs,
    )


def deep_merge(a, b):
    """Merge two values, with `b` taking precedence over `a`."""
    if isinstance(a, dict) and isinstance(b, dict):
        # set of all keys in both dictionaries
        keys = set(a.keys()) | set(b.keys())

        return {key: deep_merge(a.get(key), b.get(key)) for key in keys}
    elif isinstance(a, list) and isinstance(b, list):
        return [*a, *b]
    else:
        return a if b is None else b
