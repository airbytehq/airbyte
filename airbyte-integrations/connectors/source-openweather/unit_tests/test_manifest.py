# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import time
from pathlib import Path
from typing import Any, Iterator
from unittest.mock import patch

import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS
from unit_tests.conftest import get_source


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
_CONFIG = {
    "appid": "test-appid",
    "lat": "45.76",
    "lon": "4.83",
}
_COMPOSITE_ERROR_HANDLER_TYPE = "Composite" + "ErrorHandler"
_ONECALL_REQUEST = HttpRequest(
    url="https://api.openweathermap.org/data/3.0/onecall",
    query_params=ANY_QUERY_PARAMS,
)
_ONECALL_RESPONSE = {
    "lat": 45.76,
    "lon": 4.83,
    "timezone": "Europe/Paris",
    "timezone_offset": 3600,
}


def _manifest() -> dict[str, Any]:
    return yaml.safe_load(_MANIFEST_PATH.read_text())


def _walk_nodes(value: Any) -> Iterator[Any]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk_nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_nodes(child)


def test_manifest_has_no_composite_error_handler():
    assert not any(node.get("type") == _COMPOSITE_ERROR_HANDLER_TYPE for node in _walk_nodes(_manifest()) if isinstance(node, dict))


def test_onecall_uses_single_default_error_handler():
    error_handler = _manifest()["definitions"]["streams"]["onecall"]["retriever"]["requester"]["error_handler"]

    assert error_handler == {
        "type": "DefaultErrorHandler",
        "response_filters": [{"type": "HttpResponseFilter", "http_codes": [500], "action": "RETRY"}],
    }


def test_onecall_retries_server_error():
    catalog = CatalogBuilder().with_stream("onecall", SyncMode.full_refresh).build()

    with HttpMocker() as http_mocker:
        http_mocker.get(
            _ONECALL_REQUEST,
            [
                HttpResponse(body='{"error":"server error"}', status_code=500),
                HttpResponse(body=json.dumps(_ONECALL_RESPONSE)),
            ],
        )
        with patch.object(time, "sleep"):
            output = read(get_source(_CONFIG, catalog=catalog), config=_CONFIG, catalog=catalog)

    assert len(output.records) == 1
    assert output.errors == [], output.get_formatted_error_message()
    http_mocker.assert_number_of_calls(_ONECALL_REQUEST, 2)
