#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Mapping

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import DECODED_RESPONSE_TYPE, Decoder


@dataclass
class JsonDecoder(Decoder):
    """
    Decoder strategy that returns the json-encoded content of a response, if any.
    """

    parameters: InitVar[Mapping[str, Any]]

    def decode(self, response: requests.Response) -> DECODED_RESPONSE_TYPE:
        try:
            decoded_data: DECODED_RESPONSE_TYPE = response.json()
            return decoded_data
        except requests.exceptions.JSONDecodeError:
            return {}
