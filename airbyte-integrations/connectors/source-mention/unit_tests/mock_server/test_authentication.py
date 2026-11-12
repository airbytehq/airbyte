# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for authentication on `source-mention`.

The Mention API expects `Authorization: Bearer <access token>` and answers `401
invalid_token` otherwise. Every stream uses the shared `base_requester`, so these
tests read the root `account_me` stream and its `alert` substream through the real
`read` entrypoint and only serve data to requests carrying the Bearer header.
"""

from typing import Any, Dict

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from unit_tests.conftest import get_source


_TOKEN = "test-mention-token"
_BASE_URL = "https://api.mention.net/api"
_INVALID_TOKEN_BODY = {"error": "invalid_token", "error_description": "The access token provided is invalid."}


def _config(api_key: str) -> Dict[str, Any]:
    return {"api_key": api_key, "stats_start_date": "2026-09-01T00:00:00Z"}


def _bearer_only(body: Dict[str, Any]):
    """Behave like the Mention API: serve `body` only to correctly authenticated requests."""

    def _callback(request, context):
        if request.headers.get("Authorization") == f"Bearer {_TOKEN}":
            context.status_code = 200
            return body
        context.status_code = 401
        return _INVALID_TOKEN_BODY

    return _callback


# Users who worked around the bug by typing "Bearer <token>" into the API Key field must keep working.
_API_KEYS = pytest.mark.parametrize("api_key", [_TOKEN, f"Bearer {_TOKEN}"], ids=["raw_token", "token_with_bearer_prefix"])


@_API_KEYS
def test_account_me_sends_bearer_token_and_emits_account(requests_mock, api_key: str) -> None:
    requests_mock.get(f"{_BASE_URL}/accounts/me", json=_bearer_only({"account": {"id": "acc-1", "name": "Acme"}}))
    config = _config(api_key)

    output = read(get_source(config), config, CatalogBuilder().with_stream("account_me", SyncMode.full_refresh).build())

    assert [record.record.data["id"] for record in output.records] == ["acc-1"]
    assert not output.errors
    assert [request.headers["Authorization"] for request in requests_mock.request_history] == [f"Bearer {_TOKEN}"]


@_API_KEYS
def test_alert_substream_sends_bearer_token_on_parent_and_child_requests(requests_mock, api_key: str) -> None:
    requests_mock.get(f"{_BASE_URL}/accounts/me", json=_bearer_only({"account": {"id": "acc-1"}}))
    requests_mock.get(
        f"{_BASE_URL}/accounts/acc-1/alerts?limit=100",
        complete_qs=True,
        json=_bearer_only({"alerts": [{"id": "alert-1"}, {"id": "alert-2"}], "_links": {}}),
    )
    config = _config(api_key)

    output = read(get_source(config), config, CatalogBuilder().with_stream("alert", SyncMode.full_refresh).build())

    assert [record.record.data["id"] for record in output.records] == ["alert-1", "alert-2"]
    assert not output.errors
    assert [(request.path, request.headers["Authorization"]) for request in requests_mock.request_history] == [
        ("/api/accounts/me", f"Bearer {_TOKEN}"),
        ("/api/accounts/acc-1/alerts", f"Bearer {_TOKEN}"),
    ]
