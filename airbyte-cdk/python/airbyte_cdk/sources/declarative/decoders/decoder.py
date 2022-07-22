#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Mapping

import requests


class Decoder(ABC):
    """
    Decoder strategy to transform a requests.Response into a Mapping[str, Any]
    """

    @abstractmethod
    def decode(self, response: requests.Response) -> Mapping[str, Any]:
        """
        Decodes a requests.Response into a Mapping[str, Any]
        :param response: the response to decode
        :return: Mapping describing the response
        """
        pass
