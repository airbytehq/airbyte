# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import gzip
from unittest.mock import MagicMock

import pytest
from components import GzipXmlDecoder


VALID_XML_SINGLE_MESSAGE = """<?xml version="1.0" encoding="iso-8859-1"?>
<AmazonEnvelope>
    <Message>
        <OrderReport>
            <AmazonOrderID>123-456</AmazonOrderID>
        </OrderReport>
    </Message>
</AmazonEnvelope>"""

VALID_XML_MULTIPLE_MESSAGES = """<?xml version="1.0" encoding="iso-8859-1"?>
<AmazonEnvelope>
    <Message>
        <OrderReport>
            <AmazonOrderID>111</AmazonOrderID>
        </OrderReport>
    </Message>
    <Message>
        <OrderReport>
            <AmazonOrderID>222</AmazonOrderID>
        </OrderReport>
    </Message>
</AmazonEnvelope>"""

INVALID_XML = "<<<this is not valid xml>>>"


def _make_response(content: str, compress: bool = True) -> MagicMock:
    """Create a mock response with optionally gzip-compressed content."""
    encoded = content.encode("iso-8859-1")
    response = MagicMock()
    response.content = gzip.compress(encoded) if compress else encoded
    return response


@pytest.mark.parametrize(
    "xml_content,compress,expected_order_ids",
    [
        pytest.param(VALID_XML_SINGLE_MESSAGE, True, ["123-456"], id="valid_xml_single_message"),
        pytest.param(VALID_XML_MULTIPLE_MESSAGES, True, ["111", "222"], id="valid_xml_multiple_messages"),
        pytest.param(VALID_XML_SINGLE_MESSAGE, False, ["123-456"], id="uncompressed_fallback"),
        pytest.param(
            INVALID_XML,
            True,
            [],
            id="invalid_xml_yields_no_records_oncall_11734",
        ),
    ],
)
def test_gzip_xml_decoder_decode(xml_content, compress, expected_order_ids):
    """Test GzipXmlDecoder.decode() with various inputs.

    The 'invalid_xml_yields_no_records_oncall_11734' case covers the exact bug:
    before the fix, decode() raised AttributeError because the except block
    referenced self.name (does not exist) and used return [] in a generator.
    """
    decoder = GzipXmlDecoder(parameters={})
    response = _make_response(xml_content, compress=compress)
    results = list(decoder.decode(response))
    assert [r.get("AmazonOrderID") for r in results] == expected_order_ids
