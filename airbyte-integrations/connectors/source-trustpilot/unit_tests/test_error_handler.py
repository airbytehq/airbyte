# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from typing import Any
from unittest import TestCase
from unittest.mock import patch

import pytest
import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


_CONFIG = {
    "credentials": {"auth_type": "apikey", "client_id": "test-key"},
    "business_units": ["mybiz"],
    "start_date": "2024-01-01T00:00:00Z",
}
_MANIFEST_PATH = Path(__file__).parents[1] / "manifest.yaml"
_MANIFEST = yaml.safe_load(_MANIFEST_PATH.read_text())
_ERROR_MESSAGE = "Credentails might be expired, please validate"
_PRIVATE_REVIEWS_ERROR_MESSAGE = "Business account needs oauth flow, refer documentation for more details"


def _find_error_handlers(node: Any) -> list[dict[str, Any]]:
    if isinstance(node, dict):
        found = [node["error_handler"]] if "error_handler" in node else []
        return found + [handler for value in node.values() for handler in _find_error_handlers(value)]
    if isinstance(node, list):
        return [handler for value in node for handler in _find_error_handlers(value)]
    return []


def test_every_error_handler_is_a_default_error_handler() -> None:
    error_handlers = _find_error_handlers(_MANIFEST)

    assert len(error_handlers) == 3
    assert {handler["type"] for handler in error_handlers} == {"DefaultErrorHandler"}


@pytest.mark.parametrize(
    ("stream_name", "error_message"),
    [
        ("configured_business_units", _ERROR_MESSAGE),
        ("private_reviews", _PRIVATE_REVIEWS_ERROR_MESSAGE),
        ("business_units", _ERROR_MESSAGE),
    ],
)
def test_stream_uses_expected_default_error_handler(stream_name: str, error_message: str) -> None:
    error_handler = _MANIFEST["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]

    assert error_handler == {
        "type": "DefaultErrorHandler",
        "response_filters": [
            {
                "type": "HttpResponseFilter",
                "action": "IGNORE",
                "http_codes": [400, 403, 404],
                "error_message": error_message,
            }
        ],
    }


def _read_stream(stream_name: str) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), config=_CONFIG, catalog=catalog)


class ErrorHandlerTest(TestCase):
    @HttpMocker()
    def test_business_units_403_is_ignored(self, http_mocker: HttpMocker) -> None:
        request = HttpRequest(
            "https://api.trustpilot.com/v1/business-units/all",
            query_params={"perPage": "1000"},
        )
        http_mocker.get(request, HttpResponse(body='{"message": "forbidden"}', status_code=403))

        with patch("time.sleep"):
            output = _read_stream("business_units")

        assert output.records == []
        assert output.errors == []
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_configured_business_units_403_is_ignored(self, http_mocker: HttpMocker) -> None:
        request = HttpRequest(
            "https://api.trustpilot.com/v1/business-units/find",
            query_params={"name": "mybiz"},
        )
        http_mocker.get(request, HttpResponse(body='{"message": "forbidden"}', status_code=403))

        with patch("time.sleep"):
            output = _read_stream("configured_business_units")

        assert output.records == []
        assert output.errors == []
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_business_units_reads_records(self, http_mocker: HttpMocker) -> None:
        request = HttpRequest(
            "https://api.trustpilot.com/v1/business-units/all",
            query_params={"perPage": "1000"},
        )
        record = {"id": "business-unit-1", "name": "mybiz"}
        http_mocker.get(request, HttpResponse(body=json.dumps({"businessUnits": [record]}), status_code=200))

        with patch("time.sleep"):
            output = _read_stream("business_units")

        assert len(output.records) == 1
        assert output.errors == []
        http_mocker.assert_number_of_calls(request, 1)
