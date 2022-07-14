#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Mapping

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder


@dataclass
class JsonDecoder(Decoder):
    def decode(self, response: requests.Response) -> Mapping[str, Any]:
        return response.json()
