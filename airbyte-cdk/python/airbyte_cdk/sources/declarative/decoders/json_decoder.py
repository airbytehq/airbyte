#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Union

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder


@dataclass
class JsonDecoder(Decoder):
    """
    Decoder strategy that returns the json-encoded content of a response, if any.
    """

    parameters: InitVar[Mapping[str, Any]]

    def decode(self, response: requests.Response) -> Union[Mapping[str, Any], List]:
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            return {}
