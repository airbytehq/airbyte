# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from typing import Any, Dict
from unittest import TestCase
from unittest.mock import patch

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
_TOKEN_URL = "https://api-m.paypal.com/v1/oauth2/token"
_PRODUCTS_URL = "https://api-m.paypal.com/v1/catalogs/products"
_PRODUCTS_REQUEST = HttpRequest(url=_PRODUCTS_URL, query_params={"page_size": "20"})
_CONFIG: Dict[str, Any] = {
    "client_id": "a-client-id",
    "client_secret": "a-client-secret",
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-01-02T00:00:00Z",
    "is_sandbox": False,
}

_RATE_LIMIT_REACHED_RESPONSE = HttpResponse(
    json.dumps(
        {
            "name": "RATE_LIMIT_REACHED",
            "message": "The rate limit for the user, application, or token exceeds a predefined value.",
            "debug_id": "a-debug-id",
        }
    ),
    status_code=429,
)
_NOT_AUTHORIZED_RESPONSE = HttpResponse(
    json.dumps(
        {
            "name": "NOT_AUTHORIZED",
            "message": "Authorization failed due to insufficient permissions.",
            "debug_id": "a-debug-id",
        }
    ),
    status_code=403,
)
_PRODUCTS_RESPONSE = HttpResponse(json.dumps({"products": [{"id": "a-product-id"}]}))


def _mock_authentication(http_mocker: HttpMocker) -> None:
    http_mocker.post(
        HttpRequest(url=_TOKEN_URL, body="grant_type=client_credentials&Content-Type=application%2Fx-www-form-urlencoded"),
        HttpResponse(json.dumps({"access_token": "an-access-token", "expires_in": 3600})),
    )


def _read(stream_name: str, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(config=_CONFIG, catalog=catalog, state=None, path_to_yaml=str(_MANIFEST_PATH))
    return read(source, _CONFIG, catalog, None, expecting_exception)


class SharedErrorHandlerTest(TestCase):
    """
    Every stream except transactions uses the shared `#/definitions/error_handler`; `list_products` stands in for them.
    """

    @HttpMocker()
    def test_given_rate_limit_reached_when_read_then_wait_100_seconds_and_retry(self, http_mocker: HttpMocker) -> None:
        _mock_authentication(http_mocker)
        http_mocker.get(_PRODUCTS_REQUEST, [_RATE_LIMIT_REACHED_RESPONSE, _PRODUCTS_RESPONSE])

        with patch("airbyte_cdk.sources.streams.http.rate_limiting.time") as rate_limiting_time:
            output = _read("list_products")

        assert [record.record.data["id"] for record in output.records] == ["a-product-id"]
        assert not output.errors
        waits = [call.args[0] for call in rate_limiting_time.sleep.call_args_list]
        assert len(waits) == 1
        assert waits[0] >= 100

    @HttpMocker()
    def test_given_not_authorized_when_read_then_config_error_without_retry(self, http_mocker: HttpMocker) -> None:
        _mock_authentication(http_mocker)
        http_mocker.get(_PRODUCTS_REQUEST, _NOT_AUTHORIZED_RESPONSE)

        with patch("airbyte_cdk.sources.streams.http.rate_limiting.time") as rate_limiting_time:
            output = _read("list_products", expecting_exception=True)

        assert output.errors
        assert output.errors[0].trace.error.failure_type == FailureType.config_error
        http_mocker.assert_number_of_calls(_PRODUCTS_REQUEST, 1)
        rate_limiting_time.sleep.assert_not_called()
