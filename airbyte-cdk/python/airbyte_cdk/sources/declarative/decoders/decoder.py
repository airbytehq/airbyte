#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, List, Mapping, Union

import requests

DECODED_RESPONSE_TYPE = Union[Mapping[str, Any], List[dict[str, Any]]]


@dataclass
class Decoder:
    """
    Decoder strategy to transform a requests.Response into a Mapping[str, Any]
    """

    @abstractmethod
    def decode(self, response: requests.Response) -> DECODED_RESPONSE_TYPE:
        """
        Decodes a requests.Response into a Mapping[str, Any] or an array
        :param response: the response to decode
        :return: Mapping or array describing the response
        """
        pass
