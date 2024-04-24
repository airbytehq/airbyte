import logging
import requests
from enum import Enum
from typing import Any, Mapping
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
        self._error_mapping = self.error_mapping

    def should_retry(self, response: requests.Response) -> bool:
        return self._error_mapping[response.status_code]["action"] == ResponseAction.RETRY if response.status_code in self._error_mapping else False

    def validate_response(self, response: requests.Response) -> None:
        if response.status_code not in self.error_mapping:
            raise ValueError(f"Unexpected status code: {response.status_code}")



        pass

    def _interpret_response_status(self, response: requests.Response) -> ResponseAction:
