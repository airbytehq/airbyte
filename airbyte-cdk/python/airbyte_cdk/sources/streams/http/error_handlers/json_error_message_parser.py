#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Optional

import requests
from airbyte_cdk.sources.streams.http.error_handlers import ErrorMessageParser
from airbyte_cdk.sources.utils.types import JsonType


class JsonErrorMessageParser(ErrorMessageParser):
    def _try_get_error(self, value: Optional[JsonType]) -> Optional[str]:
        if isinstance(value, str):
            return value
        elif isinstance(value, list):
            # Using filter to avoid generating the intermediate list
            errors = filter(None, map(self._try_get_error, value))
            return ", ".join(errors)
        elif isinstance(value, dict):
            # Check keys sequentially and return the first non-None error message
            for key in (
                "message",
                "messages",
                "error",
                "errors",
                "failures",
                "failure",
                "detail",
                "err",
                "error_message",
                "msg",
                "reason",
                "status_message",
            ):
                if key in value:
                    return self._try_get_error(value[key])
        return None

    def parse_response_error_message(self, response: requests.Response) -> Optional[str]:
        """
        Parses the raw response object from a failed request into a user-friendly error message.

        :param response:
        :return: A user-friendly message that indicates the cause of the error
        """
        try:
            body = response.json()
            return self._try_get_error(body)
        except requests.exceptions.JSONDecodeError:
            return None
