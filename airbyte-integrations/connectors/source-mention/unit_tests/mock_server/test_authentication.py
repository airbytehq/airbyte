# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for how `source-mention` authenticates.

The Mention API only accepts `Authorization: Bearer <access token>`; a bare token in
that header is answered with `401 invalid_token`. Every mocked request below pins the
header, so a read only produces records when each request carries the Bearer scheme.
"""

import json
from typing import Any, Dict, List, Optional
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from mock_server.config import ConfigBuilder
from mock_server.request_builder import MentionRequestBuilder


_ACCESS_TOKEN = "test-access-token"
_ACCOUNT_ID = "account-1"
_PAGE_SIZE = 100


def _read(stream_name: str) -> EntrypointOutput:
    config = ConfigBuilder().with_api_key(_ACCESS_TOKEN).build()
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config), config, catalog, expecting_exception=False)


def _account_me_response() -> HttpResponse:
    return HttpResponse(body=json.dumps({"account": {"id": _ACCOUNT_ID, "name": "Test Account"}}), status_code=200)


def _alerts_response(alert_ids: List[str], next_cursor: Optional[str] = None) -> HttpResponse:
    """A page of alerts; like the Mention API, it always carries `_links` and only adds `more` when another page exists."""
    href = f"/api/accounts/{_ACCOUNT_ID}/alerts"
    body: Dict[str, Any] = {
        "alerts": [{"id": alert_id, "name": f"Alert {alert_id}"} for alert_id in alert_ids],
        "_links": {"self": {"href": href}},
    }
    if next_cursor:
        body["_links"]["more"] = {"href": href, "params": {"cursor": next_cursor}}
    return HttpResponse(body=json.dumps(body), status_code=200)


class TestAuthentication(TestCase):
    @HttpMocker()
    def test_alert_read_sends_bearer_token_on_parent_and_every_page(self, http_mocker: HttpMocker) -> None:
        account_me_request = MentionRequestBuilder.account_me_endpoint().with_access_token(_ACCESS_TOKEN).build()
        first_page_request = (
            MentionRequestBuilder.alerts_endpoint(_ACCOUNT_ID).with_access_token(_ACCESS_TOKEN).with_limit(_PAGE_SIZE).build()
        )
        second_page_request = (
            MentionRequestBuilder.alerts_endpoint(_ACCOUNT_ID)
            .with_access_token(_ACCESS_TOKEN)
            .with_limit(_PAGE_SIZE)
            .with_cursor("cursor-page-2")
            .build()
        )
        http_mocker.get(account_me_request, _account_me_response())
        http_mocker.get(first_page_request, _alerts_response(["alert-1", "alert-2"], next_cursor="cursor-page-2"))
        http_mocker.get(second_page_request, _alerts_response(["alert-3"]))

        output = _read("alert")

        assert [record.record.data["id"] for record in output.records] == ["alert-1", "alert-2", "alert-3"]
        assert output.errors == []
        http_mocker.assert_number_of_calls(account_me_request, 1)
        http_mocker.assert_number_of_calls(first_page_request, 1)
        http_mocker.assert_number_of_calls(second_page_request, 1)
