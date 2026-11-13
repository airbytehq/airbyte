# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from unit_tests.conftest import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_API_KEY = "test_api_key"
_CONFIG = {"api_key": _API_KEY}
_BASE_URL = "https://api.secoda.co"
_STREAM_PATHS = {
    "tables": "/table/tables/",
    "terms": "/dictionary/terms/",
    "collections": "/collection/collections/",
}


def _request(url: str) -> HttpRequest:
    return HttpRequest(url=url, headers={"Authorization": f"Bearer {_API_KEY}"}, body="page_size=1")


def _page(record_ids, next_url=None) -> HttpResponse:
    body = {"links": {"next": next_url, "previous": None}, "results": [{"id": record_id} for record_id in record_ids]}
    return HttpResponse(body=json.dumps(body), status_code=200)


def _read(stream_name: str, expecting_exception: bool = False):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), config=_CONFIG, catalog=catalog, expecting_exception=expecting_exception)


@pytest.mark.parametrize("stream_name", list(_STREAM_PATHS))
def test_read_sends_bearer_token_and_follows_links_next_until_none(stream_name: str) -> None:
    url = f"{_BASE_URL}{_STREAM_PATHS[stream_name]}"
    next_url = f"{url}?page=2"
    with HttpMocker() as http_mocker:
        http_mocker.get(_request(url), _page(["a", "b"], next_url=next_url))
        http_mocker.get(_request(next_url), _page(["c"]))

        output = _read(stream_name)

    assert [record.record.data["id"] for record in output.records] == ["a", "b", "c"]
    assert not output.errors


@pytest.mark.parametrize("stream_name", list(_STREAM_PATHS))
def test_500_fails_the_sync_as_config_error_without_retrying(stream_name: str) -> None:
    request = _request(f"{_BASE_URL}{_STREAM_PATHS[stream_name]}")
    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(body=json.dumps({"detail": "boom"}), status_code=500))

        output = _read(stream_name, expecting_exception=True)

        http_mocker.assert_number_of_calls(request, 1)

    assert output.records == []
    assert output.errors[-1].trace.error.failure_type == FailureType.config_error
