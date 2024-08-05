#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Optional

import requests
from airbyte_cdk.sources.utils.types import JsonType

from .error_message_parser import ErrorMessageParser


class JsonErrorMessageParser(ErrorMessageParser):
    def _try_get_error(self, value: Optional[JsonType]) -> Optional[str]:
        if isinstance(value, str):
            return value
        elif isinstance(value, list):
            return ", ".join(filter(None, map(self._try_get_error, value)))
        elif isinstance(value, dict):
            for key in ["message", "messages", "error", "errors", "failures", "failure", "detail"]:
                if new_value := value.get(key):
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
