import logging
import requests
from enum import Enum
from typing import Any, Mapping, Optional
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from airbyte_cdk.models import FailureType

class ResponseAction(Enum):

    SUCCESS = "SUCCESS"
    RETRY = "RETRY"
    FAIL = "FAIL"
    IGNORE = "IGNORE"

class HttpErrorHandler():

    error_mapping: Mapping[int, Mapping[str, Any]] = {
        400: { "action": ResponseAction.FAIL, "failure_type": FailureType.config_error },
        401: { "action": ResponseAction.FAIL, "failure_type": FailureType.config_error },
        403: { "action": ResponseAction.FAIL, "failure_type": FailureType.config_error },
        404: { "action": ResponseAction.FAIL, "failure_type": FailureType.system_error },
        429: { "action": ResponseAction.RETRY, "failure_type": FailureType.transient_error },
        500: { "action": ResponseAction.RETRY, "failure_type": FailureType.transient_error },
        502: { "action": ResponseAction.RETRY, "failure_type": FailureType.transient_error },
        503: { "action": ResponseAction.RETRY, "failure_type": FailureType.transient_error },
    }

    def __init__(
            self,
            logger: logging.Logger,
        ) -> None:
        self._logger = logger

        # Are these checks pointless? Custom error mapping would be set in __post_init__ anyway
        if len(self.error_mapping) == 0:
            raise ValueError("Error mapping is empty")

        for status_code, error_data in self.error_mapping:
            if not isinstance(status_code, int):
                raise ValueError("Error mapping key must be an integer to represent the HTTP status code")
            if "action" not in error_data:
                raise ValueError("Error mapping is missing required 'action' key")
            if "failure_type" not in error_data:
                raise ValueError("Error mapping is missing reqquired 'failure_type'")

        self._error_mapping = self.error_mapping


    def validate_response(self, response: requests.Response) -> None:
        response_status = self.error_mapping.get(response.status_code, None)

        if not response_status:
            raise ValueError(f"Unexpected status code: {response.status_code}")

        if response_status.action == ResponseAction.FAIL:
            error_message = (
                response_status.get("error_message") or f"Request to {response.request.url} failed with status code {response.status_code} and error message {self.parse_response_error_message(response)}"
            )
            raise AirbyteTracedException(
                internal_message=error_message,
                message=error_message,
                failure_type=response_status.failure_type
            )

        elif response_status.action == ResponseAction.IGNORE:
            self._logger.info(
                f"Ignoring response for failed request with HTTP status {response.status_code} with error message {self.parse_response_error_message(response)}"
            )

        return response

    @classmethod
    def parse_response_error_message(cls, response: requests.Response) -> Optional[str]:
        """
        Parses the raw response object from a failed request into a user-friendly error message.
        By default, this method tries to grab the error message from JSON responses by following common API patterns. Override to parse differently.

        :param response:
        :return: A user-friendly message that indicates the cause of the error
        """
        # default logic to grab error from common fields
        def _try_get_error(value: Any) -> Any:
            if isinstance(value, str):
                return value
            elif isinstance(value, list):
                error_list = [_try_get_error(v) for v in value]
                return ", ".join(v for v in error_list if v is not None)
            elif isinstance(value, dict):
                new_value = (
                    value.get("message")
                    or value.get("messages")
                    or value.get("error")
                    or value.get("errors")
                    or value.get("failures")
                    or value.get("failure")
                    or value.get("details")
                    or value.get("detail")
                )
                return _try_get_error(new_value)
            return None

        try:
            body = response.json()
            error = _try_get_error(body)
            return str(error) if error else None
        except requests.exceptions.JSONDecodeError:
            return None

    def should_retry(self, response: requests.Response) -> bool:
        return self._error_mapping[response.status_code].get("action", None) == ResponseAction.RETRY if response.status_code in self._error_mapping else False

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """
        Override this method to dynamically determine backoff time e.g: by reading the X-Retry-After header.

        This method is called only if should_backoff() returns True for the input request.

        :param response:
        :return how long to backoff in seconds. The return value may be a floating point number for subsecond precision. Returning None defers backoff
        to the default backoff behavior (e.g using an exponential algorithm).
        """
        return None

    def error_message(self, response: requests.Response) -> str:
        """
        Override this method to specify a custom error message which can incorporate the HTTP response received

        :param response: The incoming HTTP response from the partner API
        :return:
        """
        return ""
