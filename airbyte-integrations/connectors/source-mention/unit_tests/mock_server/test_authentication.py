# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"api_key": "test-key", "stats_start_date": "2026-09-01T00:00:00Z"}
API = "https://api.mention.net/api"
# The Mention API only accepts the access token as an OAuth2 bearer token.
AUTH_HEADERS = {"Authorization": "Bearer test-key"}

ACCOUNT_URL = f"{API}/accounts/me"
ALERTS_URL = f"{API}/accounts/acc1/alerts"
MENTIONS_URLS = {alert_id: f"{ALERTS_URL}/{alert_id}/mentions" for alert_id in ("al1", "al2")}

ACCOUNT_REQUEST = HttpRequest(ACCOUNT_URL, headers=AUTH_HEADERS)
ALERTS_REQUEST = HttpRequest(ALERTS_URL, query_params={"limit": "100"}, headers=AUTH_HEADERS)
MENTIONS_REQUESTS = {
    alert_id: HttpRequest(url, query_params={"limit": "1000"}, headers=AUTH_HEADERS) for alert_id, url in MENTIONS_URLS.items()
}


def read_stream(stream_name: str) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(
        path_to_yaml=str(Path(__file__).parents[2] / "manifest.yaml"),
        config=CONFIG,
        catalog=catalog,
        state=[],
    )
    return read(source, config=CONFIG, catalog=catalog)


@pytest.mark.parametrize(
    "stream_name, expected_ids, expected_urls",
    [
        ("account_me", ["acc1"], {ACCOUNT_URL}),
        ("alert", ["al1", "al2"], {ACCOUNT_URL, ALERTS_URL}),
        ("mention", ["m1", "m2"], {ACCOUNT_URL, ALERTS_URL, *MENTIONS_URLS.values()}),
    ],
)
def test_read_sends_api_key_as_bearer_token(
    http_mocker: HttpMocker, stream_name: str, expected_ids: list[str], expected_urls: set[str]
) -> None:
    http_mocker.get(ACCOUNT_REQUEST, HttpResponse(json.dumps({"account": {"id": "acc1"}})))
    http_mocker.get(ALERTS_REQUEST, HttpResponse(json.dumps({"alerts": [{"id": "al1"}, {"id": "al2"}], "_links": {}})))
    http_mocker.get(MENTIONS_REQUESTS["al1"], HttpResponse(json.dumps({"mentions": [{"id": "m1"}], "_links": {}})))
    http_mocker.get(MENTIONS_REQUESTS["al2"], HttpResponse(json.dumps({"mentions": [{"id": "m2"}], "_links": {}})))

    output = read_stream(stream_name)

    assert output.errors == []
    assert sorted(record.record.data["id"] for record in output.records) == expected_ids
    sent = http_mocker._mocker.request_history
    assert {request.url.split("?")[0] for request in sent} == expected_urls
    assert {request.headers["Authorization"] for request in sent} == {"Bearer test-key"}
