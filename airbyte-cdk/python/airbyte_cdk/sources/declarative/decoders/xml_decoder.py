#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
from dataclasses import InitVar, dataclass
from typing import Any, Generator, Mapping, MutableMapping
from xml.parsers.expat import ExpatError

import requests
import xmltodict
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder

logger = logging.getLogger("airbyte")


@dataclass
class XmlDecoder(Decoder):
    """
    XmlDecoder is a decoder strategy that parses the XML content of the resopnse, and converts it to a dict.

    This class handles XML attributes by prefixing them with an '@' symbol and represents XML text content by using the '#text' key if the element has attributes or the element name/tag. It does not currently support XML namespace declarations.

    Example XML Input:
    <root>
        <location id="123">
            San Francisco
        </location>
        <item id="1" category="books">
            <name>Book Title 1</name>
            <price>10.99</price>
        </item>
        <item id="2" category="electronics">
            <name>Gadget</name>
            <price>299.99</price>
            <description>A useful gadget</description>
        </item>
    </root>

    Converted Output:
    {
        "root": {
            "location: {
                "@id": "123,
                "#text": "San Francisco"
            },
            "item": [
              {
                "@id": "1",
                "@category": "books",
                "name": "Book Title 1",
                "price": "10.99"
              },
              {
                "@id": "2",
                "@category": "electronics",
                "name": "Gadget",
                "price": "299.99",
                "description": "A useful gadget"
              }
            ]
        }
    }

    Notes:
        - Attributes of an XML element are prefixed with an '@' symbol in the dictionary output.
        - Text content of an XML element is handled in two different ways, depending on whether
          the element has attributes.
                - If the element has attributes, the text content will be
                  represented by the "#text" key.
                - If the element does not have any attributes, the text content will be
                  represented by element name.
        - Namespace declarations are not supported in the current implementation.
    """

    parameters: InitVar[Mapping[str, Any]]

    def is_stream_response(self) -> bool:
        return False

    def decode(self, response: requests.Response) -> Generator[MutableMapping[str, Any], None, None]:
        body_xml = response.text
        try:
            body_json = xmltodict.parse(body_xml)
            if not isinstance(body_json, list):
                body_json = [body_json]
            if len(body_json) == 0:
                yield {}
            else:
                yield from body_json
        except ExpatError as exc:
            logger.warning(f"Response cannot be parsed from XML: {response.status_code=}, {response.text=}, {exc=}")
            yield {}
