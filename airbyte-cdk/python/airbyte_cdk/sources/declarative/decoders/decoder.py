#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any

from airbyte_cdk.sources.declarative.response import Response


class Decoder(ABC):
    @abstractmethod
    def decode(self, response: Any) -> Response:
        pass
