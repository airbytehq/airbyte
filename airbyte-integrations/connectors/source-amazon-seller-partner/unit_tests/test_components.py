#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import gzip
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import requests


# Ensure the connector's components module is importable
sys.path.append(str(Path(__file__).parent.parent))

from components import GzipXmlDecoder


def _make_response(content: bytes) -> requests.Response:
    """Helper to create a mock requests.Response with the given content."""
    response = MagicMock(spec=requests.Response)
    response.content = content
    return response


def _gzip_bytes(text: str) -> bytes:
    return gzip.compress(text.encode("iso-8859-1"))


VALID_XML_SINGLE = (
    '<?xml version="1.0"?><AmazonEnvelope><Message><OrderReport><OrderId>123</OrderId></OrderReport></Message></AmazonEnvelope>'
)

VALID_XML_MULTI = (
    '<?xml version="1.0"?>'
    "<AmazonEnvelope>"
    "<Message><OrderReport><OrderId>123</OrderId></OrderReport></Message>"
    "<Message><OrderReport><OrderId>456</OrderId></OrderReport></Message>"
    "</AmazonEnvelope>"
)


@pytest.mark.parametrize(
    "content,expected_order_ids",
    [
        pytest.param(
            _gzip_bytes(VALID_XML_SINGLE),
            ["123"],
            id="gzipped_single_message",
        ),
        pytest.param(
            _gzip_bytes(VALID_XML_MULTI),
            ["123", "456"],
            id="gzipped_multiple_messages",
        ),
        pytest.param(
            VALID_XML_SINGLE.encode("iso-8859-1"),
            ["123"],
            id="uncompressed_single_message",
        ),
    ],
)
def test_gzip_xml_decoder_decode_valid_xml(content, expected_order_ids):
    """Test that valid XML responses (gzipped and uncompressed) are decoded correctly."""
    decoder = GzipXmlDecoder(parameters={})
    response = _make_response(content)

    results = list(decoder.decode(response))

    assert [r.get("OrderId") for r in results] == expected_order_ids


@pytest.mark.parametrize(
    "content",
    [
        pytest.param(
            gzip.compress(b"this is not valid xml <><><>"),
            id="gzipped_invalid_xml",
        ),
        pytest.param(
            b"<<<not xml at all>>>",
            id="uncompressed_invalid_content",
        ),
        pytest.param(
            gzip.compress(b""),
            id="gzipped_empty_content",
        ),
    ],
)
def test_gzip_xml_decoder_decode_invalid_xml_does_not_raise(content):
    """
    Test that malformed content yields no records instead of raising an error.

    This covers the bug reported in https://github.com/airbytehq/oncall/issues/11734:
    Before the fix, the except block referenced self.name which does not exist on
    GzipXmlDecoder, causing AttributeError to mask the original XML parsing error.
    """
    decoder = GzipXmlDecoder(parameters={})
    response = _make_response(content)

    # Before the fix, this would raise:
    #   AttributeError: 'GzipXmlDecoder' object has no attribute 'name'
    results = list(decoder.decode(response))

    assert results == []


def test_gzip_xml_decoder_has_no_name_attribute():
    """
    Verify GzipXmlDecoder does not have a 'name' attribute.
    Documents the root cause of the bug - self.name never existed.
    """
    decoder = GzipXmlDecoder(parameters={})

    assert not hasattr(decoder, "name")
