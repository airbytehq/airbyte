#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Union

import requests


@dataclass
class Decoder:
    """Decoder strategy to transform a requests.Response into a Mapping[str, Any]"""

    @abstractmethod
    def decode(self, response: requests.Response) -> Union[Mapping[str, Any], list]:
        """Decodes a requests.Response into a Mapping[str, Any] or an array
        :param response: the response to decode
        :return: Mapping or array describing the response
        """
