# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from abc import ABC, abstractmethod
from typing import Optional, Union

import requests

from .response_models import ErrorResolution


class ErrorHandler(ABC):
    """
    Abstract base class to determine how to handle a failed HTTP request.
    """

    @abstractmethod
    def interpret_response(self, response: Optional[Union[requests.Response, Exception]]) -> ErrorResolution:
        """
        Interpret the response or exception and return the corresponding response action, failure type, and error message.

        :param response: The HTTP response object or exception raised during the request.
        :return: A tuple containing the response action, failure type, and error message.
        """
        pass
