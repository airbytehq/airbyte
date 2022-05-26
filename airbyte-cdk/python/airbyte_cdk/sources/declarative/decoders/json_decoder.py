#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder


class JsonDecoder(Decoder):
    def decode(self, response: requests.Response) -> Mapping[str, Any]:
        return response.json()
