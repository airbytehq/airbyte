# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for how source-mention authenticates against the Mention API.

The Mention API only accepts `Authorization: Bearer <access_token>`. A request
whose header carries the bare token is rejected with
`401 {"error":"invalid_token"}`. These tests serve responses only to requests
that carry the Bearer header, so a regression to a bare-token header makes the
read fail.
"""

import json
from unittest import TestCase

import pytest

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_API_KEY = "test-access-token"
_CONFIG = {"api_key": _API_KEY, "stats_start_date": "2026-09-01T00:00:00Z"}
_BASE_URL = "https://api.mention.net/api"
_ACCOUNT_ID = "12345_abcdef"
_BEARER_HEADERS = {"Authorization": f"Bearer {_API_KEY}"}


def _json_response(body: dict) -> HttpResponse:
    return HttpResponse(body=json.dumps(body), status_code=200)


def _read(stream_name: str, config: dict = _CONFIG):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config=config), config, catalog)


@pytest.mark.parametrize(
    "configured_api_key",
    [
        pytest.param(_API_KEY, id="bare_token"),
        # Users who worked around the missing prefix by typing "Bearer <token>" must keep working.
        pytest.param(f"Bearer {_API_KEY}", id="token_with_bearer_prefix"),
    ],
)
def test_account_me_sends_single_bearer_prefix_and_emits_account(configured_api_key: str) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(f"{_BASE_URL}/accounts/me", headers=_BEARER_HEADERS),
            _json_response({"account": {"id": _ACCOUNT_ID, "name": "Airbyte"}}),
        )

        output = _read("account_me", {**_CONFIG, "api_key": configured_api_key})

    assert [record.record.data["id"] for record in output.records] == [_ACCOUNT_ID]
    assert not output.errors


class TestBearerAuthentication(TestCase):

    @HttpMocker()
    def test_alert_sends_bearer_token_on_parent_and_child_requests(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequest(f"{_BASE_URL}/accounts/me", headers=_BEARER_HEADERS),
            _json_response({"account": {"id": _ACCOUNT_ID, "name": "Airbyte"}}),
        )
        http_mocker.get(
            HttpRequest(
                f"{_BASE_URL}/accounts/{_ACCOUNT_ID}/alerts",
                query_params={"limit": "100"},
                headers=_BEARER_HEADERS,
            ),
            _json_response({"alerts": [{"id": 1, "name": "alert one"}, {"id": 2, "name": "alert two"}], "_links": {}}),
        )

        output = _read("alert")

        assert [record.record.data["id"] for record in output.records] == [1, 2]
        assert not output.errors
