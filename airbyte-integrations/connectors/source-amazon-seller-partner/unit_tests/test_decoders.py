# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import gzip
from unittest.mock import MagicMock

import pytest
from components import GzipXmlDecoder

from airbyte_cdk.utils.traced_exception import AirbyteTracedException


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
    ],
)
def test_gzip_xml_decoder_decode(xml_content, compress, expected_order_ids):
    """Test GzipXmlDecoder.decode() with valid XML inputs."""
    decoder = GzipXmlDecoder(parameters={})
    response = _make_response(xml_content, compress=compress)
    results = list(decoder.decode(response))
    assert [r.get("AmazonOrderID") for r in results] == expected_order_ids


def test_gzip_xml_decoder_raises_traced_exception_on_invalid_xml():
    """Non-empty malformed XML raises AirbyteTracedException with system_error."""
    decoder = GzipXmlDecoder(parameters={})
    response = _make_response(INVALID_XML, compress=True)
    with pytest.raises(AirbyteTracedException) as exc_info:
        list(decoder.decode(response))
    assert exc_info.value.failure_type.value == "system_error"
    assert "not valid XML" in exc_info.value.message
    assert INVALID_XML[:200] in exc_info.value.internal_message


@pytest.mark.parametrize(
    "content",
    [
        pytest.param("", id="empty_string"),
        pytest.param("   ", id="whitespace_only"),
        pytest.param("\n\t\n", id="newlines_and_tabs"),
    ],
)
def test_gzip_xml_decoder_yields_nothing_for_empty_document(content):
    """Empty or whitespace-only documents yield no records and do not raise."""
    decoder = GzipXmlDecoder(parameters={})
    response = _make_response(content, compress=True)
    results = list(decoder.decode(response))
    assert results == []


@pytest.mark.parametrize(
    "content",
    [
        pytest.param("", id="empty_uncompressed"),
        pytest.param("  \n  ", id="whitespace_uncompressed"),
    ],
)
def test_gzip_xml_decoder_yields_nothing_for_empty_uncompressed_document(content):
    """Empty uncompressed documents (BadGzipFile fallback) yield no records."""
    decoder = GzipXmlDecoder(parameters={})
    response = _make_response(content, compress=False)
    results = list(decoder.decode(response))
    assert results == []
