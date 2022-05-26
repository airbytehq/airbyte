#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Mapping

import requests


class Decoder(ABC):
    @abstractmethod
    def decode(self, response: requests.Response) -> Mapping[str, Any]:
        pass
