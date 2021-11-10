#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from requests import HTTPError


class ZendeskError(HTTPError):
    """
    Base error class.
    Subclassing HTTPError to avoid breaking existing code that expects only HTTPErrors.
    """


class ZendeskTimeout(ZendeskError):
    """502/504 Zendesk has processing limits in place to prevent a single client from causing degraded performance,
    and these responses indicate that those limits have been hit. You'll normally only see these timeout responses
    when making a large number of requests over a sustained period. If you get one of these responses,
    you should pause your requests for a few seconds, then retry.
    """


class ZendeskInvalidAuth(ZendeskError):
    """401 Unauthorized"""


class ZendeskAccessDenied(ZendeskError):
    """403 Forbidden"""


class ZendeskRateLimited(ZendeskError):
    """429 Rate Limit Reached"""
