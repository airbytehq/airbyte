# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import time
from pathlib import Path
from typing import Any, Iterator
from unittest.mock import patch

import pytest
import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
_CONFIG = {
    "username": "api-key",
    "password": "",
    "organization_name": "testorg",
    "start_date": "2024-01-01T00:00:00Z",
}
_COMPOSITE_ERROR_HANDLER_TYPE = "Composite" + "ErrorHandler"
_STREAM_NAMES = [
    "customers",
    "products",
    "products_stock",
    "orders",
    "backorders",
    "returns",
    "purchaseorders",
    "locations",
    "warehouses",
    "users",
    "suppliers",
    "tags",
    "templates",
    "vatgroups",
    "stats",
]


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


@pytest.mark.parametrize("stream_name", _STREAM_NAMES)
def test_streams_use_single_default_error_handler(stream_name: str):
    error_handler = _manifest()["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]

    assert error_handler["type"] == "DefaultErrorHandler"
    assert error_handler["max_retries"] == 3
    assert error_handler["backoff_strategies"] == [{"type": "ExponentialBackoffStrategy", "factor": 2}]
    assert error_handler["response_filters"] == [
        {
            "type": "HttpResponseFilter",
            "action": "RATE_LIMITED",
            "http_codes": [429],
            "error_message": "Rate limits hit...Retrying",
        }
    ]


def test_customers_retries_rate_limit_response():
    request = HttpRequest(url="https://testorg.picqer.com/api/v1/customers")
    records = [{"idcustomer": 1}, {"idcustomer": 2}]

    with HttpMocker() as http_mocker:
        http_mocker.get(
            request,
            [
                HttpResponse(body='{"error":"rate limited"}', status_code=429),
                HttpResponse(body=json.dumps(records)),
            ],
        )
        catalog = CatalogBuilder().with_stream("customers", SyncMode.full_refresh).build()
        with patch.object(time, "sleep"):
            output = read(get_source(_CONFIG, catalog=catalog), config=_CONFIG, catalog=catalog)

    assert len(output.records) == 2
    assert [message.record.data for message in output.records] == records
    assert output.errors == [], output.get_formatted_error_message()
    http_mocker.assert_number_of_calls(request, 2)
