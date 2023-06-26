#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any

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


class InvalidStartDateConfigError(Exception):
    """Raises when the User inputs wrong or invalid `start_date` in inout configuration"""

    def __init__(self, actual_value: Any, message: str):
        super().__init__(
            f"The value for `start_date` entered `{actual_value}` is ivalid and could not be processed.\nPlease use the real date/time value.\nFull message: {message}"
        )
