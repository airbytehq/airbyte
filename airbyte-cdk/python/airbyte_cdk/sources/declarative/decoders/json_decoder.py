#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder


class JsonDecoder(Decoder):
    """
    Decoder strategy that returns the json-encoded content of a response, if any.
    """

    def decode(self, response: requests.Response) -> Mapping[str, Any]:
        return response.json() or {}
