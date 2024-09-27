#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
import xmltodict
from dataclasses import InitVar, dataclass
from typing import Any, Generator, Mapping

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from orjson import orjson

logger = logging.getLogger("airbyte")


@dataclass
class XmlDecoder(Decoder):
    """
    Decoder strategy that parses the XML content of the resopnse, and converts it to a JSON object.
    """

    parameters: InitVar[Mapping[str, Any]]

    def is_stream_response(self) -> bool:
        return False

    def decode(self, response: requests.Response) -> Generator[Mapping[str, Any], None, None]:
        pass
