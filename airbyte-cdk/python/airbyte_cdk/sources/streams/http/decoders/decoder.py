#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from abc import ABC, abstractmethod
from typing import Any, List, Mapping, Union

import requests


class Decoder(ABC):
    """
    Decoder strategy to transform a requests.Response into a Mapping[str, Any]
    """

    @abstractmethod
    def decode(self, response: requests.Response) -> Union[Mapping[str, Any], List]:
        """
        Decodes a requests.Response into a Mapping[str, Any] or an array
        :param response: the response to decode
        :return: Mapping or array describing the response
        """
        pass

    @abstractmethod
    def is_valid_response(self, response: requests.Response) -> bool:
        """
        Validates the response to determine if it is valid
        :param response: the response to validate
        :return: True if the response is valid, False otherwise
        """
        pass

    @abstractmethod
    def validate_response(self, response: requests.Response) -> None:
        """
        Validates the response to determine if it is valid
        :param response: the response to validate
        :return: None
        """
        pass
