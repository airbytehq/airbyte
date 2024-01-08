import json
from typing import Optional, Union

import aiohttp
import requests

from airbyte_cdk.sources.utils.types import JsonType


class HttpError(Exception):
    def __init__(
        self,
        error: Union[requests.HTTPError, aiohttp.ClientResponseError],
        response: Optional[aiohttp.ClientResponse] = None,
    ):
        self.error = error

        self.response = (
            response if isinstance(response, aiohttp.ClientResponse) else error.response
        )
        self._response_error: Optional[JsonType] = None

    @property
    def status_code(self) -> Optional[int]:
        if isinstance(self.error, requests.HTTPError):
            return self.error.response.status_code if self.error.response else None
        elif isinstance(self.error, aiohttp.ClientResponseError):
            return self.error.status

    @property
    def message(self) -> str:
        if isinstance(self.error, requests.HTTPError):
            return str(self.error)
        elif isinstance(self.error, aiohttp.ClientResponseError):
            return self.error.message

    @property
    def error_response(self) -> JsonType:
        # This returns a uniform response object for further introspection
        if isinstance(self.error, requests.HTTPError):
            return self.error.response.json()
        elif isinstance(self.error, aiohttp.ClientResponseError):
            return self._response_error

    @classmethod
    def parse_response_error_message(
        cls, response: Union[requests.Response, aiohttp.ClientResponseError]
    ) -> Optional[str]:
        if isinstance(response, requests.Response):
            return cls._parse_sync_response_error(response)
        else:
            return cls._parse_async_response_error(response)

    @classmethod
    def _parse_sync_response_error(cls, response: requests.Response) -> Optional[str]:
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

    @classmethod
    def _parse_async_response_error(
        cls, response: aiohttp.ClientResponseError
    ) -> Optional[str]:
        try:
            if (
                hasattr(response, "_response_error")
                and response._response_error is not None
            ):
                return cls._try_get_error(response)  # type: ignore  # https://github.com/aio-libs/aiohttp/issues/3248
            else:
                raise NotImplementedError(
                    "`_response_error` is expected but was not set on the response; `set_response_error` should be used prior to processing the exception"
                )
        except json.JSONDecodeError:
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

    async def set_response_error(self):
        if self._response is None:
            return
        try:
            error_json = await self._response.json()
        except (json.JSONDecodeError, aiohttp.ContentTypeError):
            error_json = None
        except Exception as exc:
            raise NotImplementedError(f"Unexpected!!!!!!!! {exc}")  # TODO
            self.logger.error(f"Unable to get error json from response: {exc}")
            error_json = None

        text = await self._response.text()
        exception._response_error = (  # type: ignore  # https://github.com/aio-libs/aiohttp/issues/3248
            error_json or text
        )
