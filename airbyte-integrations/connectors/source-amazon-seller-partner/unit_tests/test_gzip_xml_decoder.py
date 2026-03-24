#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import gzip
from unittest.mock import MagicMock

import pytest

from components import GzipXmlDecoder


def _make_response(content: bytes, is_gzipped: bool = True) -> MagicMock:
    """Create a mock requests.Response with the given content."""
    response = MagicMock()
    response.content = gzip.compress(content) if is_gzipped else content
    return response


VALID_XML_MULTI = (
    '<?xml version="1.0" encoding="iso-8859-1"?>'
    "<AmazonEnvelope>"
    "<Message><OrderReport><OrderId>123</OrderId></OrderReport></Message>"
    "<Message><OrderReport><OrderId>456</OrderId></OrderReport></Message>"
    "</AmazonEnvelope>"
)

VALID_XML_SINGLE = (
    '<?xml version="1.0" encoding="iso-8859-1"?>'
    "<AmazonEnvelope>"
    "<Message><OrderReport><OrderId>789</OrderId></OrderReport></Message>"
    "</AmazonEnvelope>"
)

INVALID_XML = "this is not xml <><><"


@pytest.mark.parametrize(
    "content,is_gzipped,expected_count,expected_first_order_id",
    [
        pytest.param(
            VALID_XML_MULTI.encode("iso-8859-1"), True, 2, "123",
            id="gzipped_multi_message",
        ),
        pytest.param(
            VALID_XML_SINGLE.encode("iso-8859-1"), True, 1, "789",
            id="gzipped_single_message",
        ),
        pytest.param(
            VALID_XML_MULTI.encode("iso-8859-1"), False, 2, "123",
            id="uncompressed_multi_message",
        ),
    ],
)
def test_decode_valid_xml(content, is_gzipped, expected_count, expected_first_order_id):
    """Verify that valid XML content is decoded into the expected number of records."""
    decoder = GzipXmlDecoder(parameters={})
    response = _make_response(content, is_gzipped=is_gzipped)
    records = list(decoder.decode(response))
    assert len(records) == expected_count
    assert records[0]["OrderId"] == expected_first_order_id


@pytest.mark.parametrize(
    "content,is_gzipped",
    [
        pytest.param(INVALID_XML.encode("iso-8859-1"), True, id="gzipped_invalid_xml"),
        pytest.param(INVALID_XML.encode("iso-8859-1"), False, id="uncompressed_invalid_xml"),
        pytest.param(b"", False, id="empty_content"),
    ],
)
def test_decode_invalid_xml_does_not_raise_attribute_error(content, is_gzipped):
    """
    Regression test for https://github.com/airbytehq/oncall/issues/11734

    When XML parsing fails, the decoder must NOT raise AttributeError
    from referencing a non-existent `self.name`. It should log a warning
    and yield zero records.
    """
    decoder = GzipXmlDecoder(parameters={})
    response = _make_response(content, is_gzipped=is_gzipped)
    # Before the fix, this raised: AttributeError: 'GzipXmlDecoder' object has no attribute 'name'
    records = list(decoder.decode(response))
    assert records == []


def test_decoder_has_no_name_attribute():
    """Verify that GzipXmlDecoder does not have a 'name' attribute -- the root cause of the bug."""
    decoder = GzipXmlDecoder(parameters={})
    assert not hasattr(decoder, "name")


def test_is_stream_response_returns_false():
    decoder = GzipXmlDecoder(parameters={})
    assert decoder.is_stream_response() is False
