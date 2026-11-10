# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_STREAM_NAME = "activity"
_COMPANY = "acme"
_API_KEY = "test_api_key"
_CONFIG = {"company": _COMPANY, "api_key": _API_KEY}
_URL = f"https://{_COMPANY}.hellobaton.com/api/activity"
_NEXT_PAGE_URL = f"{_URL}?page=2&page_size=100"


def _request(extra_query_params=None) -> HttpRequest:
    return HttpRequest(
        url=_URL,
        query_params={"api_key": _API_KEY, "page_size": "100", **(extra_query_params or {})},
        headers={"api-key": _API_KEY},
    )


def _page(record_ids, next_url=None) -> HttpResponse:
    body = {"count": 3, "next": next_url, "previous": None, "results": [{"id": record_id} for record_id in record_ids]}
    return HttpResponse(body=json.dumps(body), status_code=200)


def _read(expecting_exception: bool = False):
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), config=_CONFIG, catalog=catalog, expecting_exception=expecting_exception)


class TestActivityStream(TestCase):
    # All streams share the same requester, paginator and error handler, so this covers them too.

    @HttpMocker()
    def test_read_sends_api_key_header_and_follows_next_page(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request(), _page([1, 2], next_url=_NEXT_PAGE_URL))
        http_mocker.get(_request({"page": "2"}), _page([3]))

        output = _read()

        assert [record.record.data["id"] for record in output.records] == [1, 2, 3]
        assert not output.errors

    @HttpMocker()
    def test_unknown_workspace_404_is_config_error(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request(), HttpResponse(body="<title>Baton Page Not Found</title>", status_code=404))

        output = _read(expecting_exception=True)

        assert output.records == []
        error = output.errors[0].trace.error
        assert error.failure_type == FailureType.config_error
        assert error.message == (
            f"Baton workspace 'https://{_COMPANY}.hellobaton.com' was not found (HTTP 404). "
            f"Set 'company' to your workspace subdomain only, e.g. 'acme' for https://acme.hellobaton.com."
        )
