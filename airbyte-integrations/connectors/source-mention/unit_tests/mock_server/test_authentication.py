# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server test for the credentials the connector sends to the Mention API.

Mention only accepts `Authorization: Bearer <token>`; a bare token is answered with
`401 invalid_token`. Every stream shares one requester, so a read of `mention` (which
walks `account_me` -> `alert` -> `mention`) pins the header on each kind of request.
"""

import json
from typing import Any, Dict, Optional
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_API_KEY = "mention_test_token"
_CONFIG = {"api_key": _API_KEY, "stats_start_date": "2026-09-01T00:00:00Z"}
_URL_BASE = "https://api.mention.net/api"
_ACCOUNT_ID = "acc_1"


def _request(path: str, query_params: Optional[Dict[str, str]] = None) -> HttpRequest:
    return HttpRequest(
        url=f"{_URL_BASE}{path}",
        query_params=query_params,
        headers={"Authorization": f"Bearer {_API_KEY}"},
    )


def _response(body: Dict[str, Any]) -> HttpResponse:
    return HttpResponse(body=json.dumps(body), status_code=200)


class TestAuthentication(TestCase):
    @HttpMocker()
    def test_every_request_sends_the_api_key_as_a_bearer_token(self, http_mocker: HttpMocker) -> None:
        account_request = _request("/accounts/me")
        alerts_page_1_request = _request(f"/accounts/{_ACCOUNT_ID}/alerts", {"limit": "100"})
        alerts_page_2_request = _request(f"/accounts/{_ACCOUNT_ID}/alerts", {"limit": "100", "cursor": "page_2"})
        mentions_alert_1_request = _request(f"/accounts/{_ACCOUNT_ID}/alerts/alert_1/mentions", {"limit": "1000"})
        mentions_alert_2_request = _request(f"/accounts/{_ACCOUNT_ID}/alerts/alert_2/mentions", {"limit": "1000"})

        http_mocker.get(account_request, _response({"account": {"id": _ACCOUNT_ID}}))
        http_mocker.get(
            alerts_page_1_request,
            _response({"alerts": [{"id": "alert_1"}], "_links": {"more": {"params": {"cursor": "page_2"}}}}),
        )
        http_mocker.get(alerts_page_2_request, _response({"alerts": [{"id": "alert_2"}], "_links": {}}))
        http_mocker.get(mentions_alert_1_request, _response({"mentions": [{"id": "mention_1"}, {"id": "mention_2"}], "_links": {}}))
        http_mocker.get(mentions_alert_2_request, _response({"mentions": [{"id": "mention_3"}], "_links": {}}))

        catalog = CatalogBuilder().with_stream("mention", SyncMode.full_refresh).build()
        output = read(get_source(_CONFIG), _CONFIG, catalog)

        assert output.errors == []
        assert [record.record.data["id"] for record in output.records] == ["mention_1", "mention_2", "mention_3"]
        for request in (alerts_page_1_request, alerts_page_2_request, mentions_alert_1_request, mentions_alert_2_request):
            http_mocker.assert_number_of_calls(request, 1)
