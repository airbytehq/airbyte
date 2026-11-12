# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from collections.abc import Callable
from urllib.parse import parse_qsl, urlsplit

import pytest
from conftest import get_source
from requests_mock import Mocker
from requests_mock.request import _RequestObjectProxy
from requests_mock.response import _Context

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_API_URL = "https://api.mention.net/api"
_TOKEN = "test-mention-token"
_ACCOUNT_URL = f"{_API_URL}/accounts/me"
_ALERTS_URL = f"{_API_URL}/accounts/account-1/alerts"


def _authenticated_response(payload: dict) -> Callable[[_RequestObjectProxy, _Context], dict]:
    def respond(request: _RequestObjectProxy, context: _Context) -> dict:
        if request.headers.get("Authorization") != f"Bearer {_TOKEN}":
            context.status_code = 401
            return {"error": "invalid_token", "error_description": "The access token provided is invalid."}
        return payload

    return respond


@pytest.mark.parametrize(
    "stream_name, expected_ids",
    [
        ("account_me", ["account-1"]),
        ("alert", ["alert-1", "alert-2"]),
        ("mention", ["mention-1", "mention-2", "mention-3"]),
    ],
)
def test_read_authenticates_parent_streams_partitions_and_pages(requests_mock: Mocker, stream_name: str, expected_ids: list[str]) -> None:
    config = {"api_key": _TOKEN, "stats_start_date": "2026-09-01T00:00:00Z"}
    responses = [
        (_ACCOUNT_URL, {"account": {"id": "account-1"}}),
        (
            f"{_ALERTS_URL}?limit=100",
            {"alerts": [{"id": "alert-1"}], "_links": {"more": {"params": {"cursor": "next-alert"}}}},
        ),
        (f"{_ALERTS_URL}?limit=100&cursor=next-alert", {"alerts": [{"id": "alert-2"}], "_links": {}}),
        (
            f"{_ALERTS_URL}/alert-1/mentions?limit=1000",
            {"mentions": [{"id": "mention-1"}], "_links": {"more": {"params": {"cursor": "next-mention"}}}},
        ),
        (f"{_ALERTS_URL}/alert-1/mentions?limit=1000&cursor=next-mention", {"mentions": [{"id": "mention-2"}], "_links": {}}),
        (f"{_ALERTS_URL}/alert-2/mentions?limit=1000", {"mentions": [{"id": "mention-3"}], "_links": {}}),
    ]
    for url, payload in responses:
        requests_mock.get(url, json=_authenticated_response(payload), complete_qs=True)

    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    output = read(get_source(config, catalog), config=config, catalog=catalog)

    assert [request.headers.get("Authorization") for request in requests_mock.request_history] == [
        f"Bearer {_TOKEN}"
    ] * requests_mock.call_count
    # Concurrent partitions may interleave records, but must not lose or duplicate any.
    assert sorted(record.record.data["id"] for record in output.records) == expected_ids
    assert not output.errors
    expected_urls = [url for url, _ in responses]
    if stream_name == "account_me":
        expected_urls = expected_urls[:1]
    elif stream_name == "alert":
        expected_urls = expected_urls[:3]
    else:
        # The account is read by both the alert parent and the mention partition router.
        expected_urls.append(_ACCOUNT_URL)
    assert sorted((request.path, sorted(parse_qsl(urlsplit(request.url).query))) for request in requests_mock.request_history) == sorted(
        (urlsplit(url).path, sorted(parse_qsl(urlsplit(url).query))) for url in expected_urls
    )
