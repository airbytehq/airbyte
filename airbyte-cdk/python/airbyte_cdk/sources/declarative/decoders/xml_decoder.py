#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
import xmltodict
import requests
from xml.parsers.expat import ExpatError
from dataclasses import InitVar, dataclass
from typing import Any, Generator, Mapping
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder

logger = logging.getLogger("airbyte")


@dataclass
class XmlDecoder(Decoder):
    """
    Decoder strategy that parses the XML content of the resopnse, and converts it to a dict.
    """

    parameters: InitVar[Mapping[str, Any]]

    def is_stream_response(self) -> bool:
        return False

    def decode(self, response: requests.Response) -> Generator[Mapping[str, Any], None, None]:
        body_xml = response.text
        try:
            body_json = dict(xmltodict.parse(body_xml))
            if not isinstance(body_json, list):
                body_json = [body_json]
            if len(body_json) == 0:
                yield {}
            else:
                yield from body_json
        except ExpatError:
            logger.warning(f"Response cannot be parsed from XML: {response.status_code=}, {response.text=}")
            yield {}
