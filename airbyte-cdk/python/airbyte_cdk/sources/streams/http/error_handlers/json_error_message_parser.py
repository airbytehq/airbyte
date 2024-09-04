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
            errors_in_value = [self._try_get_error(v) for v in value]
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
                or value.get("err")
                or value.get("error_message")
                or value.get("msg")
                or value.get("reason")
                or value.get("status_message")
            )
            return self._try_get_error(new_value)
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
