#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Optional

import requests
from airbyte_cdk.sources.utils.types import JsonType


def parse_response_error_message(response: requests.Response) -> Optional[str]:
    """
    Parses the raw response object from a failed request into a user-friendly error message.
    By default, this method tries to grab the error message from JSON responses by following common API patterns. Override to parse differently.

    :param response:
    :return: A user-friendly message that indicates the cause of the error
    """

    # default logic to grab error from common fields
    def _try_get_error(value: Optional[JsonType]) -> Optional[str]:
        if isinstance(value, str):
            return value
        elif isinstance(value, list):
            errors_in_value = [_try_get_error(v) for v in value]
            return ", ".join(v for v in errors_in_value if v is not None)
        elif isinstance(value, dict):
            new_value = (
                value.get("message")
                or value.get("messages")
                or value.get("error")
                or value.get("errors")
                or value.get("failures")
                or value.get("failure")
                or value.get("detail")
            )
            return _try_get_error(new_value)
        return None

    try:
        body = response.json()
        return _try_get_error(body)
    except requests.exceptions.JSONDecodeError:
        return None
