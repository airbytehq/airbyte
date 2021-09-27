#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


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
