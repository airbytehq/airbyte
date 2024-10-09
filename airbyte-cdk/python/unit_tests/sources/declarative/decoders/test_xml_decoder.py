#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import pytest
import requests
from airbyte_cdk.sources.declarative.decoders import XmlDecoder


@pytest.mark.parametrize(
        "response_body, expected",
        [
            (
                "<item name=\"item_1\"></item>",
                {"item": {"@name": "item_1"}}
            ),
            (
                "<data><item name=\"item_1\">Item 1</item><item name=\"item_2\">Item 2</item></data>",
                {"data": {"item": [{"@name": "item_1", "#text": "Item 1"}, {"@name": "item_2", "#text": "Item 2"}]}}
            ),
            (
                None,
                {}
            ),
            (
                "<item name=\"item_1\">",
                {}
            ),
            (
                "<item xmlns:ns=\"https://airbyte.io\"><ns:id>1</ns:id><ns:name>Item 1</ns:name></item>",
                {'item': {'@xmlns:ns': 'https://airbyte.io', 'ns:id': '1', 'ns:name': 'Item 1'}}
            )
        ],
        ids=["one_element_response", "multi_element_response", "empty_response", "malformed_xml_response", "xml_with_namespace_response"]
)
def test_xml_decoder(requests_mock, response_body, expected):
    requests_mock.register_uri("GET", "https://airbyte.io/", text=response_body)
    response = requests.get("https://airbyte.io/")
    assert next(XmlDecoder(parameters={}).decode(response)) == expected
