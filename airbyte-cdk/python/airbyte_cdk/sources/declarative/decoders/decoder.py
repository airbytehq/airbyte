#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Mapping

import requests
from airbyte_cdk.sources.declarative.cdk_jsonschema import JsonSchemaMixin


class Decoder(ABC, JsonSchemaMixin):
    @abstractmethod
    def decode(self, response: requests.Response) -> Mapping[str, Any]:
        pass
