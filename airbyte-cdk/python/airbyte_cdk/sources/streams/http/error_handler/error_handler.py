import requests
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple, Optional
from .response_action import ResponseAction
from airbyte_cdk.models import FailureType

@dataclass
class ErrorHandler(ABC):
    """
    Determines how to handle a failed HTTP request.
    """

    @abstractmethod
    def interpret_response(self, response: Optional[requests.Response], exception: Optional[Exception]) -> Optional[Tuple[ResponseAction, FailureType, str]]:
        """
        Interpret the response or exception and return the corresponding response action, failure type, and error message.

        :param response: The HTTP response object.
        :param exception: The exception raised during the request.
        :return: A tuple containing the response action, failure type, and error message.
        :raises ValueError: If both response and exception are provided or if the error is not mapped.
        """
        pass
