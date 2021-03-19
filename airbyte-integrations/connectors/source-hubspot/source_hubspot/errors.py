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


class HubspotError(HTTPError):
    """
    Base error class.
    Subclassing HTTPError to avoid breaking existing code that expects only HTTPErrors.
    """


class HubspotTimeout(HubspotError):
    """502/504 HubSpot has processing limits in place to prevent a single client from causing degraded performance,
    and these responses indicate that those limits have been hit. You'll normally only see these timeout responses
    when making a large number of requests over a sustained period. If you get one of these responses,
    you should pause your requests for a few seconds, then retry.
    """


class HubspotInvalidAuth(HubspotError):
    """401 Unauthorized"""


class HubspotAccessDenied(HubspotError):
    """403 Forbidden"""


class HubspotRateLimited(HubspotError):
    """429 Rate Limit Reached"""
