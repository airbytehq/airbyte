import json
from typing import Optional, Union

import aiohttp
import requests

from airbyte_cdk.sources.utils.types import JsonType


class HttpError(Exception):
    def __init__(
        self,
        requests_error: Optional[requests.RequestException] = None,
        aiohttp_error: Optional[aiohttp.ClientResponseError] = None,
        error_message: Optional[str] = None,
    ):
        assert (
            requests_error or aiohttp_error and not (requests_error and aiohttp_error)
        ), "requests_error xor aiohttp_error must be supplied"
        self._requests_error = requests_error
        self._aiohttp_error = aiohttp_error
        self._aiohttp_response_json = None
        self._aiohttp_response_content = None
        self._aiohttp_response_text = None
        self._aiohttp_response = None
        self.error_message = error_message

    @property
    def status_code(self) -> Optional[int]:
        if self._requests_error and self._requests_error.response:
            return self._requests_error.response.status_code
        elif self._aiohttp_error:
            return self._aiohttp_error.status
        return 0

    @property
    def message(self) -> str:
        if self._requests_error:
            return str(self._requests_error)
        elif self._aiohttp_error:
            return self.error_message
        else:
            return ""

    @property
    def content(self) -> Optional[bytes]:
        if self._requests_error and self._requests_error.response:
            return self._requests_error.response.content
        elif self._aiohttp_error:
            return self._aiohttp_response_content
        return b""

    @property
    def text(self) -> Optional[str]:
        if self._requests_error and self._requests_error.response:
            return self._requests_error.response.text
        elif self._aiohttp_error:
            return self._aiohttp_response_text
        return ""

    def json(self) -> Optional[JsonType]:
        if self._requests_error and self._requests_error.response:
            return self._requests_error.response.json()
        elif self._aiohttp_error:
            return self._aiohttp_response_json
        return ""

    @property
    def request(self) -> Optional[Union[requests.Request, aiohttp.RequestInfo]]:
        if self._requests_error and self._requests_error.response:
            return self._requests_error.request
        elif self._aiohttp_error:
            return self._aiohttp_error.request_info

    @property
    def response(self) -> Optional[Union[requests.Response, aiohttp.ClientResponse]]:
        if self._requests_error and self._requests_error.response:
            return self._requests_error.response
        elif self._aiohttp_error:
            return self._aiohttp_response

    @property
    def url(self) -> str:
        if self._requests_error and self._requests_error.request:
            return self._requests_error.request.url or ""
        elif self._aiohttp_error:
            return str(self._aiohttp_error.request_info.url)
        return ""

    @property
    def reason(self) -> Optional[str]:
        if self._requests_error and self._requests_error.request:
            return self._requests_error.response.reason
        elif self._aiohttp_error:
            return self._aiohttp_error.message
        return ""

    @classmethod
    def parse_response_error_message(cls, response: requests.Response) -> Optional[str]:
        """
        Parses the raw response object from a failed request into a user-friendly error message.
        By default, this method tries to grab the error message from JSON responses by following common API patterns. Override to parse differently.

        :param response:
        :return: A user-friendly message that indicates the cause of the error
        """
        try:
            return cls._try_get_error(response.json())
        except requests.exceptions.JSONDecodeError:
            return None

    def parse_error_message(self) -> Optional[str]:
        """
        Parses the raw response object from a failed request into a user-friendly error message.
        By default, this method tries to grab the error message from JSON responses by following common API patterns. Override to parse differently.

        :param response:
        :return: A user-friendly message that indicates the cause of the error
        """
        if self._requests_error and self._requests_error.response:
            return self.parse_response_error_message(self._requests_error.response)
        elif self._aiohttp_error:
            try:
                return self._try_get_error(self._aiohttp_response_json)
            except requests.exceptions.JSONDecodeError:
                return None
        return None

    @classmethod
    def _try_get_error(cls, value: Optional[JsonType]) -> Optional[str]:
        # default logic to grab error from common fields
        if isinstance(value, str):
            return value
        elif isinstance(value, list):
            errors_in_value = [cls._try_get_error(v) for v in value]
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
            return cls._try_get_error(new_value)
        return None

    # Async utils

    async def set_response_data(self, response: aiohttp.ClientResponse):
        try:
            response_json = await response.json()
        except (json.JSONDecodeError, aiohttp.ContentTypeError):
            response_json = None
        except Exception as exc:
            raise NotImplementedError(f"Unexpected!!!!!!!! {exc}")  # TODO
            self.logger.error(f"Unable to get error json from response: {exc}")
            response_json = None

        text = await response.text()  # This fixed a test
        self._aiohttp_response = response
        self._aiohttp_response_json = response_json or text
        self._aiohttp_response_content = await response.content.read()
        self._aiohttp_response_text = text
