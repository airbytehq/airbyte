# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import time
from pathlib import Path

import pytest
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_CONNECTOR_DIR = Path(__file__).parent.parent
_SEARCH_URL = "https://gnews.io/api/v4/search"
_TOP_HEADLINES_URL = "https://gnews.io/api/v4/top-headlines"
_QUOTA_ERROR = (
    "GNews API returned 403 Forbidden: the daily request quota for this API key has been reached "
    "(it resets at 00:00 UTC) or the subscription has expired. Wait for the quota reset or check "
    "your GNews plan, then retry the sync."
)
_CONFIG = {
    "api_key": "key",
    "query": "airbyte",
    "language": "en",
    "country": "us",
    "nullable": ["description"],
    "in": ["title"],
    "sortby": "publishedAt",
    "top_headlines_topic": "technology",
    "top_headlines_query": "climate",
    "start_date": "2024-01-01 00:00:00",
    "end_date": "2024-01-10 00:00:00",
}
_FULL_REFRESH_SLICES = [
    ("2024-01-01T00:00:00Z", "2024-01-07T23:59:59Z"),
    ("2024-01-08T00:00:00Z", "2024-01-10T00:00:00Z"),
]


def _request(stream_name: str, from_time: str, to_time: str) -> HttpRequest:
    query_params = {
        "token": "key",
        "lang": "en",
        "country": "us",
        "nullable": "description",
        "from": from_time,
        "to": to_time,
    }
    if stream_name == "search":
        query_params.update({"q": "airbyte", "in": "title", "sortby": "publishedAt"})
        url = _SEARCH_URL
    else:
        query_params.update({"topic": "technology", "q": "climate"})
        url = _TOP_HEADLINES_URL
    return HttpRequest(url, query_params=query_params)


def _response(*published_at: str) -> HttpResponse:
    return HttpResponse(
        json.dumps(
            {
                "totalArticles": len(published_at),
                "articles": [
                    {
                        "title": f"Article {index}",
                        "url": f"https://example.com/{index}",
                        "publishedAt": timestamp,
                    }
                    for index, timestamp in enumerate(published_at)
                ],
            }
        ),
        status_code=200,
    )


def _read_stream(
    stream_name: str,
    config: dict = _CONFIG,
    sync_mode: SyncMode = SyncMode.full_refresh,
    state=None,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    source = get_source(config=config, state=state)
    return read(source, config=config, catalog=catalog, expecting_exception=expecting_exception)


def _error_text(output: EntrypointOutput) -> str:
    return " ".join(
        [
            str(getattr(error.trace.error, "message", "") or "") + " " + str(getattr(error.trace.error, "internal_message", "") or "")
            for error in output.errors
        ]
        + [entry.log.message for entry in output.logs]
    )


@pytest.fixture
def http_mocker():
    with HttpMocker() as mocker:
        yield mocker


def test_search_full_refresh_requests_every_date_slice(http_mocker: HttpMocker):
    requests = [_request("search", start, end) for start, end in _FULL_REFRESH_SLICES]
    http_mocker.get(requests[0], _response("2024-01-02T00:00:00Z"))
    http_mocker.get(requests[1], _response("2024-01-09T00:00:00Z"))

    output = _read_stream("search")

    assert output.errors == []
    assert sorted(record.record.data["publishedAt"] for record in output.records) == [
        "2024-01-02T00:00:00Z",
        "2024-01-09T00:00:00Z",
    ]
    for request in requests:
        http_mocker.assert_number_of_calls(request, 1)


def test_top_headlines_full_refresh_requests_every_date_slice(http_mocker: HttpMocker):
    requests = [_request("top_headlines", start, end) for start, end in _FULL_REFRESH_SLICES]
    http_mocker.get(requests[0], _response("2024-01-02T00:00:00Z"))
    http_mocker.get(requests[1], _response("2024-01-09T00:00:00Z"))

    output = _read_stream("top_headlines")

    assert output.errors == []
    assert sorted(record.record.data["publishedAt"] for record in output.records) == [
        "2024-01-02T00:00:00Z",
        "2024-01-09T00:00:00Z",
    ]
    for request in requests:
        http_mocker.assert_number_of_calls(request, 1)


def test_429_retries_then_emits_record(http_mocker: HttpMocker, monkeypatch: pytest.MonkeyPatch):
    config = {**_CONFIG, "end_date": "2024-01-03 00:00:00"}
    request = _request("search", "2024-01-01T00:00:00Z", "2024-01-03T00:00:00Z")
    http_mocker.get(
        request,
        [
            HttpResponse('{"error":"rate limited"}', status_code=429),
            _response("2024-01-02T00:00:00Z"),
        ],
    )
    sleeps = []
    monkeypatch.setattr(time, "sleep", sleeps.append)

    output = _read_stream("search", config=config)

    assert output.errors == []
    assert len(output.records) == 1
    assert [sleep for sleep in sleeps if sleep >= 0.5] == [2.0]
    http_mocker.assert_number_of_calls(request, 2)


def test_403_retries_with_constant_backoff_then_emits_record(http_mocker: HttpMocker, monkeypatch: pytest.MonkeyPatch):
    config = {**_CONFIG, "end_date": "2024-01-03 00:00:00"}
    request = _request("search", "2024-01-01T00:00:00Z", "2024-01-03T00:00:00Z")
    http_mocker.get(
        request,
        [
            HttpResponse('{"errors":["daily quota exceeded"]}', status_code=403),
            _response("2024-01-02T00:00:00Z"),
        ],
    )
    sleeps = []
    monkeypatch.setattr(time, "sleep", sleeps.append)

    output = _read_stream("search", config=config)

    assert output.errors == []
    assert len(output.records) == 1
    assert [sleep for sleep in sleeps if sleep >= 0.5] == [2.0]
    http_mocker.assert_number_of_calls(request, 2)


def test_403_on_every_attempt_reports_quota_error(http_mocker: HttpMocker, monkeypatch: pytest.MonkeyPatch):
    config = {**_CONFIG, "end_date": "2024-01-03 00:00:00"}
    request = _request("search", "2024-01-01T00:00:00Z", "2024-01-03T00:00:00Z")
    forbidden = HttpResponse('{"errors":["daily quota exceeded"]}', status_code=403)
    http_mocker.get(request, [forbidden] * 6)
    monkeypatch.setattr(time, "sleep", lambda _: None)

    output = _read_stream("search", config=config, expecting_exception=True)

    assert output.errors
    assert _QUOTA_ERROR in _error_text(output)
    http_mocker.assert_number_of_calls(request, 6)


@pytest.mark.parametrize("stream_name", ["search", "top_headlines"])
def test_incremental_state_starts_at_cursor_and_advances(stream_name: str, http_mocker: HttpMocker):
    state_timestamp = "2024-01-05T12:00:00Z"
    state = StateBuilder().with_stream_state(stream_name, {"publishedAt": state_timestamp}).build()
    request = _request(stream_name, state_timestamp, "2024-01-10T00:00:00Z")
    http_mocker.get(request, _response("2024-01-06T00:00:00Z", "2024-01-09T00:00:00Z"))

    output = _read_stream(stream_name, sync_mode=SyncMode.incremental, state=state)

    assert output.errors == []
    assert [record.record.data["publishedAt"] for record in output.records] == [
        "2024-01-06T00:00:00Z",
        "2024-01-09T00:00:00Z",
    ]
    assert output.most_recent_state.stream_state.publishedAt == "2024-01-09T00:00:00Z"
    http_mocker.assert_number_of_calls(request, 1)


def test_manifest_does_not_use_custom_components():
    manifest = (_CONNECTOR_DIR / "manifest.yaml").read_text()
    assert "class_name" not in manifest
    assert not (_CONNECTOR_DIR / "components.py").exists()
