# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json

import pytest
from requests import Response

from airbyte_cdk.utils.traced_exception import AirbyteTracedException


def _create_response(status_code: int, content: str = "", content_type: str = "application/json") -> Response:
    response = Response()
    response.status_code = status_code
    response._content = content.encode("utf-8")
    response.headers["Content-Type"] = content_type
    return response


def _create_jsonl_response(records: list[dict]) -> Response:
    content = "\n".join(json.dumps(r) for r in records)
    return _create_response(200, content, "application/json")


@pytest.mark.parametrize(
    "status_code,expected_message_fragment",
    [
        pytest.param(304, "Dataset is not ready, please contact infor member services", id="http_304_not_ready"),
        pytest.param(202, "Dataset is not ready, try again later", id="http_202_not_ready"),
        pytest.param(500, "Unexpected status code: 500", id="http_500_unexpected"),
        pytest.param(403, "Unexpected status code: 403", id="http_403_unexpected"),
    ],
)
def test_decode_error_status_raises_traced_exception(components_module, status_code, expected_message_fragment):
    """Verify that non-200 status codes raise AirbyteTracedException instead of NameError."""
    FlexibleDecoder = components_module.FlexibleDecoder
    decoder = FlexibleDecoder(parameters={})
    response = _create_response(status_code, content="error body")

    with pytest.raises(AirbyteTracedException) as exc_info:
        list(decoder.decode(response))
    assert expected_message_fragment in exc_info.value.message


def test_decode_success_yields_records(components_module):
    """Verify that a 200 response with JSONL content is decoded correctly."""
    FlexibleDecoder = components_module.FlexibleDecoder
    decoder = FlexibleDecoder(parameters={})
    records = [{"id": "1", "name": "test"}, {"id": "2", "name": "test2"}]
    response = _create_jsonl_response(records)

    result = list(decoder.decode(response))

    assert len(result) == 2
    assert result[0]["raw_data"] == {"id": "1", "name": "test"}
    assert result[1]["raw_data"] == {"id": "2", "name": "test2"}
    assert "raw_data_string" in result[0]


def test_decode_octet_stream_yields_records(components_module):
    """Verify that application/octet-stream content type is decoded as JSONL."""
    FlexibleDecoder = components_module.FlexibleDecoder
    decoder = FlexibleDecoder(parameters={})
    records = [{"id": "1", "name": "test"}]
    content = "\n".join(json.dumps(r) for r in records)
    response = _create_response(200, content, "application/octet-stream")

    result = list(decoder.decode(response))

    assert len(result) == 1
    assert result[0]["raw_data"] == {"id": "1", "name": "test"}


def test_decode_unsupported_content_type_raises_value_error(components_module):
    """Verify that an unsupported Content-Type raises ValueError."""
    FlexibleDecoder = components_module.FlexibleDecoder
    decoder = FlexibleDecoder(parameters={})
    response = _create_response(200, content="some text", content_type="text/plain")

    with pytest.raises(ValueError, match="Unsupported or unrecognized Content-Type"):
        list(decoder.decode(response))
