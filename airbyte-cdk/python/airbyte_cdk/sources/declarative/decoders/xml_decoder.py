#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
import xmltodict
from xml.parsers.expat import ExpatError
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
        body_xml = response.content

        try:
            body_json = xmltodict.parse(body_xml)
            if not isinstance(body_json, list):
                body_json = [body_json]
            if len(body_json) == 0:
                yield {}
            else:
                yield from body_json
        except ExpatError:
            logger.warning(f"Response cannot be parsed from XML: {response.status_code=}, {response.text=}")
            yield {}
