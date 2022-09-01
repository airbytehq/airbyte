#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Union

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class JsonDecoder(Decoder, JsonSchemaMixin):
    """
    Decoder strategy that returns the json-encoded content of a response, if any.
    """

    options: InitVar[Mapping[str, Any]]

    def decode(self, response: requests.Response) -> Union[Mapping[str, Any], List]:
        return response.json() or {}
