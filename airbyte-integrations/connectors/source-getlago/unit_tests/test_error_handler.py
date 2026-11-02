# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from typing import Any, Dict
from unittest import TestCase
from unittest.mock import patch

import yaml
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_BASE_URL = "https://api.getlago.com/api/v1"
_CONFIG = {"api_key": "test-key"}
_CUSTOMER_ID = "customer-external-id"
_SUBSCRIPTION_ID = "subscription-external-id"
_MAX_RETRIES = 5
_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"

_CUSTOMERS_REQUEST = HttpRequest(
    url=f"{_BASE_URL}/customers",
    query_params={"per_page": "100"},
)
_SUBSCRIPTIONS_REQUEST = HttpRequest(
    url=f"{_BASE_URL}/subscriptions",
    query_params={
        "external_customer_id": _CUSTOMER_ID,
        "per_page": "100",
    },
)
_CURRENT_USAGE_REQUEST = HttpRequest(
    url=f"{_BASE_URL}/customers/{_CUSTOMER_ID}/current_usage",
    query_params={"external_subscription_id": _SUBSCRIPTION_ID},
)
_PAST_USAGE_REQUEST = HttpRequest(
    url=f"{_BASE_URL}/customers/{_CUSTOMER_ID}/past_usage",
    query_params={
        "external_subscription_id": _SUBSCRIPTION_ID,
        "per_page": "100",
    },
)


def _response(body: Dict[str, Any], status_code: int = 200) -> HttpResponse:
    return HttpResponse(body=json.dumps(body), status_code=status_code)


def _mock_parent_chain(http_mocker: HttpMocker) -> None:
    http_mocker.get(
        _CUSTOMERS_REQUEST,
        _response(
            {
                "customers": [{"external_id": _CUSTOMER_ID}],
                "meta": {"next_page": None},
            }
        ),
    )
    http_mocker.get(
        _SUBSCRIPTIONS_REQUEST,
        _response(
            {
                "subscriptions": [
                    {
                        "external_customer_id": _CUSTOMER_ID,
                        "external_id": _SUBSCRIPTION_ID,
                    }
                ],
                "meta": {"next_page": None},
            }
        ),
    )


def _read(stream_name: str, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(
        get_source(config=_CONFIG),
        _CONFIG,
        catalog,
        expecting_exception=expecting_exception,
    )


@patch("time.sleep", lambda _: None)
class TestGetLagoErrorHandler(TestCase):
    @HttpMocker()
    def test_current_usage_405_no_active_subscription_is_ignored(self, http_mocker: HttpMocker) -> None:
        _mock_parent_chain(http_mocker)
        http_mocker.get(
            _CURRENT_USAGE_REQUEST,
            _response(
                {
                    "status": 405,
                    "error": "Method Not Allowed",
                    "code": "no_active_subscription",
                },
                status_code=405,
            ),
        )

        output = _read("customer_usage")

        assert output.records == []
        assert output.errors == []
        http_mocker.assert_number_of_calls(_CURRENT_USAGE_REQUEST, 1)

    @HttpMocker()
    def test_past_usage_405_no_active_subscription_is_ignored(self, http_mocker: HttpMocker) -> None:
        _mock_parent_chain(http_mocker)
        http_mocker.get(
            _PAST_USAGE_REQUEST,
            _response(
                {
                    "status": 405,
                    "error": "Method Not Allowed",
                    "code": "no_active_subscription",
                },
                status_code=405,
            ),
        )

        output = _read("customer_usage_past")

        assert output.records == []
        assert output.errors == []
        http_mocker.assert_number_of_calls(_PAST_USAGE_REQUEST, 1)

    @HttpMocker()
    def test_current_usage_405_with_other_code_is_not_ignored(self, http_mocker: HttpMocker) -> None:
        _mock_parent_chain(http_mocker)
        http_mocker.get(
            _CURRENT_USAGE_REQUEST,
            _response(
                {"status": 405, "error": "Method Not Allowed", "code": "not_allowed"},
                status_code=405,
            ),
        )

        output = _read("customer_usage", expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(_CURRENT_USAGE_REQUEST, 1)

    @HttpMocker()
    def test_current_usage_500_is_retried_then_succeeds(self, http_mocker: HttpMocker) -> None:
        _mock_parent_chain(http_mocker)
        http_mocker.get(
            _CURRENT_USAGE_REQUEST,
            [
                HttpResponse(body="", status_code=500),
                _response({"customer_usage": {"amount_cents": 100, "currency": "USD"}}),
            ],
        )

        output = _read("customer_usage")

        assert len(output.records) == 1
        assert output.errors == []
        http_mocker.assert_number_of_calls(_CURRENT_USAGE_REQUEST, 2)

    @HttpMocker()
    def test_persistent_current_usage_500_stops_after_max_retries(self, http_mocker: HttpMocker) -> None:
        _mock_parent_chain(http_mocker)
        http_mocker.get(_CURRENT_USAGE_REQUEST, HttpResponse(body="", status_code=500))

        output = _read("customer_usage", expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(_CURRENT_USAGE_REQUEST, _MAX_RETRIES + 1)

    def test_usage_streams_use_default_error_handlers(self) -> None:
        manifest_text = _MANIFEST_PATH.read_text()
        manifest = yaml.safe_load(manifest_text)

        for stream_name in ("customer_usage", "customer_usage_past"):
            assert (
                manifest["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]["type"] == "DefaultErrorHandler"
            )
        assert "Composite" + "ErrorHandler" not in manifest_text
