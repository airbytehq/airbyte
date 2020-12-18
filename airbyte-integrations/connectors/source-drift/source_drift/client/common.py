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

import collections
import functools
from typing import Iterator
from urllib.parse import parse_qs, urlparse

import requests


class ServerError(Exception):
    """Server respond with error"""


class APIError(Exception):
    """Base class for API errors""" ""


class ValidationError(APIError):
    """Provided data has failed validation"""


class AuthError(APIError):
    """Token is wrong or expired"""


class NotFoundError(APIError):
    """Object not found"""


class RateLimitError(APIError):
    """API calls reached allowed limit"""


def cursor_paginator(request, start_index: int = None, per_page: int = 100, params: dict = None) -> Iterator[dict]:
    """Paginator that use cursor offset to navigate"""
    params = params or {}
    index = start_index
    while True:
        result = request(params={**params, "next": index, "limit": per_page})
        if isinstance(result["data"], collections.abc.Sequence):
            yield from result["data"]
        else:
            yield result["data"]
        index = result.get("pagination", {}).get("next")
        if not index:
            break


def next_url_paginator(request, start_index: int = None, per_page: int = 100, params: dict = None) -> Iterator[dict]:
    """Paginator that use next url to navigate"""
    params = params or {}
    size = per_page
    index = start_index
    while True:
        result = request(params={**params, "index": index, "size": size})
        if isinstance(result["data"], collections.abc.Sequence):
            yield from result["data"]
        else:
            yield result["data"]

        next_url = result["data"].get("next")
        if not next_url:
            break

        # parse url to unify request command
        next_url = urlparse(next_url)
        next_params = parse_qs(next_url.query)
        index = next_params.get("index", [None])[0]
        size = next_params.get("size", [None])[0]


def exception_from_code(code: int, message: str) -> Exception:
    """ Map response code to exception class"""
    mapping = {
        400: ValidationError,
        401: AuthError,
        403: AuthError,
        429: RateLimitError,
        404: NotFoundError,
        500: ServerError,
        502: ServerError,
        503: ServerError,
        504: ServerError,
    }

    return mapping.get(code, APIError)(code, message)


def _parsed_response(func):
    """ Decorator to check response status and parse its body"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            response = func(*args, **kwargs)
            result = response.json() if response.text else {}
            if not response.ok:
                msg = result  # fallback to the whole response
                if "error" in result:
                    msg = result["error"].get("message", result)
                # multiple errors? grab all of them
                elif "errors" in result:
                    msg = result["errors"]
                raise exception_from_code(response.status_code, msg)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as err:
            raise ServerError(err.request.status_code, "Connection Error") from err

        return result

    return wrapper
