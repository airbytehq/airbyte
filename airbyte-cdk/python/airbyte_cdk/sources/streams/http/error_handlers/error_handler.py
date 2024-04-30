# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Mapping, Optional, Tuple, Union

import requests
from airbyte_cdk.models import FailureType

from .response_action import ResponseAction


@dataclass
class ErrorHandler(ABC):
    """
    Abstract base class to determine how to handle a failed HTTP request.
    """

    @abstractmethod
    def interpret_response(
        self, response: Optional[Union[requests.Response, Exception]]
    ) -> Tuple[Optional[ResponseAction], Optional[FailureType], Optional[str]]:
        """
        Interpret the response or exception and return the corresponding response action, failure type, and error message.

        :param response: The HTTP response object or exception raised during the request.
        :return: A tuple containing the response action, failure type, and error message.
        """
        pass
