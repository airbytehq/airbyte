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

from requests import HTTPError


class FreshdeskError(HTTPError):
    """
    Base error class.
    Subclassing HTTPError to avoid breaking existing code that expects only HTTPErrors.
    """


class FreshdeskBadRequest(FreshdeskError):
    """Most 40X and 501 status codes"""


class FreshdeskUnauthorized(FreshdeskError):
    """401 Unauthorized"""


class FreshdeskAccessDenied(FreshdeskError):
    """403 Forbidden"""


class FreshdeskNotFound(FreshdeskError):
    """404"""


class FreshdeskRateLimited(FreshdeskError):
    """429 Rate Limit Reached"""


class FreshdeskServerError(FreshdeskError):
    """50X errors"""
