#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import gzip

import pytest
import requests
from components import GzipXmlDecoder


def _make_response(content: bytes, gzip_compress: bool = True) -> requests.Response:
    """Helper to create a mock requests.Response with the given content."""
    response = requests.Response()
    response.status_code = 200
    if gzip_compress:
        response._content = gzip.compress(content)
    else:
        response._content = content
    return response


VALID_XML = b"""<?xml version="1.0" encoding="iso-8859-1"?>
<AmazonEnvelope>
    <Message>
        <OrderReport>
            <AmazonOrderID>123-456</AmazonOrderID>
        </OrderReport>
    </Message>
    <Message>
        <OrderReport>
            <AmazonOrderID>789-012</AmazonOrderID>
        </OrderReport>
    </Message>
</AmazonEnvelope>
"""

VALID_XML_NO_MESSAGES = b"""<?xml version="1.0" encoding="iso-8859-1"?>
<AmazonEnvelope>
    <Header>
        <DocumentVersion>1.01</DocumentVersion>
    </Header>
</AmazonEnvelope>
"""


@pytest.mark.parametrize(
    "content,gzip_compress,expected_count,expected_first_order_id",
    [
        pytest.param(VALID_XML, True, 2, "123-456", id="valid_gzipped_xml"),
        pytest.param(VALID_XML, False, 2, "123-456", id="valid_uncompressed_xml_fallback"),
        pytest.param(VALID_XML_NO_MESSAGES, True, 0, None, id="valid_xml_no_messages"),
        pytest.param(b"<<<not valid xml>>>", True, 0, None, id="unparseable_xml_no_attribute_error"),
        pytest.param(b"", True, 0, None, id="empty_content"),
    ],
)
def test_gzip_xml_decoder_decode(content, gzip_compress, expected_count, expected_first_order_id):
    """Test GzipXmlDecoder.decode() handles valid XML, invalid XML, and edge cases.

    The 'unparseable_xml_no_attribute_error' case covers the exact bug from oncall issue 11734:
    previously this path raised AttributeError (self.name) and used 'return []' in a generator.
    """
    decoder = GzipXmlDecoder(parameters={})
    response = _make_response(content, gzip_compress=gzip_compress)
    records = list(decoder.decode(response))
    assert len(records) == expected_count
    if expected_first_order_id is not None:
        assert records[0]["AmazonOrderID"] == expected_first_order_id
