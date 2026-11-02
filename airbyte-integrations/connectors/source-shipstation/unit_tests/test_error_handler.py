"""Tests for ShipStation error handling."""

import json
from pathlib import Path
from typing import Any
from unittest import TestCase
from unittest.mock import patch

import pytest
import yaml

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONFIG = {"username": "user", "password": "pass", "start_date": "2024-01-01T00:00:00Z"}
_MANIFEST_PATH = Path(__file__).parents[1] / "manifest.yaml"
_STREAM_NAMES = [
    "carriers",
    "customers",
    "fulfillments",
    "marketplaces",
    "orders",
    "products",
    "shipments",
    "stores",
    "users",
    "warehouses",
    "webhooks",
]


@pytest.mark.parametrize("stream_name", _STREAM_NAMES)
def test_stream_uses_default_error_handler(stream_name: str) -> None:
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    error_handler = manifest["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]

    assert error_handler == {
        "type": "DefaultErrorHandler",
        "backoff_strategies": [{"type": "WaitTimeFromHeader", "header": "X-Rate-Limit-Reset"}],
    }


def test_manifest_has_no_composite_error_handler() -> None:
    assert "CompositeErrorHandler" not in _MANIFEST_PATH.read_text()


def _read_stream(stream_name: str) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), config=_CONFIG, catalog=catalog)


def _assert_rate_limited_request_waits_for_header_and_reads_records(
    stream_name: str, request: HttpRequest, response_body: Any, http_mocker: HttpMocker
) -> None:
    http_mocker.get(
        request,
        [
            HttpResponse(body='{"message": "Too Many Requests"}', status_code=429, headers={"X-Rate-Limit-Reset": "7"}),
            HttpResponse(body=json.dumps(response_body), status_code=200),
        ],
    )

    with patch("time.sleep") as mocked_sleep:
        output = _read_stream(stream_name)

    assert len(output.records) == 1
    assert output.errors == []
    http_mocker.assert_number_of_calls(request, 2)
    assert any(call.args and call.args[0] == pytest.approx(7, abs=1) for call in mocked_sleep.call_args_list)


class ErrorHandlerTest(TestCase):
    @HttpMocker()
    def test_users_retry_after_rate_limit(self, http_mocker: HttpMocker) -> None:
        _assert_rate_limited_request_waits_for_header_and_reads_records(
            "users",
            HttpRequest("https://ssapi.shipstation.com/users", query_params={"showInactive": "true"}),
            [{"userId": "u1"}],
            http_mocker,
        )

    @HttpMocker()
    def test_carriers_retry_after_rate_limit(self, http_mocker: HttpMocker) -> None:
        _assert_rate_limited_request_waits_for_header_and_reads_records(
            "carriers",
            HttpRequest("https://ssapi.shipstation.com/carriers"),
            [{"code": "ups", "shippingProviderId": 1}],
            http_mocker,
        )
