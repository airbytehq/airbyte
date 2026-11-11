# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import time
from pathlib import Path

import pytest

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


CONFIG = {
    "api_key": "test-key",
    "query": "airbyte OR data",
    "language": "en",
    "country": "us",
    "nullable": ["description", "content"],
    "in": ["title", "description"],
    "sortby": "publishedAt",
    "top_headlines_topic": "technology",
    "top_headlines_query": "climate",
    "start_date": "2024-01-01 00:00:00",
    "end_date": "2024-01-10 00:00:00",
}
END = "2024-01-10T00:00:00Z"
QUOTA_MESSAGE = (
    "GNews daily request quota has been exceeded (or the subscription has expired). "
    "The quota resets at 00:00 UTC; wait for the reset, reduce the sync frequency or "
    "upgrade your GNews plan (https://gnews.io/pricing)."
)


def request_for(stream_name: str, start: str, end: str = END) -> HttpRequest:
    params = {
        "token": "test-key",
        "lang": "en",
        "country": "us",
        "nullable": "description,content",
        "from": start,
        "to": end,
    }
    if stream_name == "search":
        params.update(q="airbyte OR data", **{"in": "title,description", "sortby": "publishedAt"})
    else:
        params.update(topic="technology", q="climate")
    return HttpRequest(f"https://gnews.io/api/v4/{stream_name.replace('_', '-')}", query_params=params)


def article(timestamp: str) -> dict:
    return {
        "title": "Example article",
        "description": "News description",
        "content": "News content",
        "url": f"https://example.com/{timestamp}",
        "image": "https://example.com/image.png",
        "publishedAt": timestamp,
        "source": {"name": "Example", "url": "https://example.com"},
    }


def response_for(records: list[dict]) -> HttpResponse:
    return HttpResponse(json.dumps({"totalArticles": len(records), "articles": records}))


def read_stream(stream_name: str, cursor: str | None = None, failure: bool = False) -> EntrypointOutput:
    state = StateBuilder().with_stream_state(stream_name, {"publishedAt": cursor}).build() if cursor else []
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    source = YamlDeclarativeSource(
        path_to_yaml=str(Path(__file__).parents[2] / "manifest.yaml"),
        config=CONFIG,
        catalog=catalog,
        state=state,
    )
    return read(source, config=CONFIG, catalog=catalog, state=state, expecting_exception=failure)


@pytest.mark.parametrize("empty", [False, True])
def test_weekly_slices(stream_name: str, http_mocker: HttpMocker, empty: bool) -> None:
    requests = [
        request_for(stream_name, "2024-01-01T00:00:00Z", "2024-01-07T23:59:59Z"),
        request_for(stream_name, "2024-01-08T00:00:00Z"),
    ]
    records = [] if empty else [article("2024-01-02T00:00:00Z"), article("2024-01-09T00:00:00Z")]
    for index, request in enumerate(requests):
        http_mocker.get(request, response_for([] if empty else [records[index]]))

    output = read_stream(stream_name)

    assert output.errors == []
    assert sorted((record.record.data for record in output.records), key=lambda record: record["url"]) == records
    for request in requests:
        http_mocker.assert_number_of_calls(request, 1)


def test_legacy_cursor(stream_name: str, http_mocker: HttpMocker) -> None:
    request = request_for(stream_name, "2024-01-05T12:00:00Z")
    records = [article("2024-01-06T00:00:00Z"), article("2024-01-09T00:00:00Z")]
    http_mocker.get(request, response_for(records))

    output = read_stream(stream_name, cursor="2024-01-05T12:00:00Z")

    assert output.errors == []
    assert [record.record.data for record in output.records] == records
    assert output.most_recent_state.stream_state.publishedAt == "2024-01-09T00:00:00Z"
    http_mocker.assert_number_of_calls(request, 1)


@pytest.mark.parametrize(
    "status, failure_type, message",
    [
        (
            400,
            FailureType.config_error,
            "GNews rejected the request as malformed. Check the query syntax, date format and other parameters. Response: ['invalid query']",
        ),
        (
            401,
            FailureType.config_error,
            "GNews rejected the API key. Please verify the API key in your GNews dashboard (https://gnews.io/dashboard).",
        ),
        (403, FailureType.transient_error, QUOTA_MESSAGE),
    ],
)
def test_failures(stream_name: str, http_mocker: HttpMocker, status: int, failure_type: FailureType, message: str) -> None:
    request = request_for(stream_name, "2024-01-05T12:00:00Z")
    http_mocker.get(request, HttpResponse(json.dumps({"errors": ["invalid query"]}), status_code=status))

    output = read_stream(stream_name, cursor="2024-01-05T12:00:00Z", failure=True)

    assert output.records == []
    assert output.errors
    stream_errors = [error.trace.error for error in output.errors if error.trace.error.stream_descriptor is not None]
    assert len(stream_errors) == 1
    assert stream_errors[0].stream_descriptor.name == stream_name
    assert stream_errors[0].failure_type == failure_type
    assert stream_errors[0].message == message
    http_mocker.assert_number_of_calls(request, 1)


def test_rate_limit_retry(stream_name: str, http_mocker: HttpMocker, monkeypatch: pytest.MonkeyPatch) -> None:
    request = request_for(stream_name, "2024-01-05T12:00:00Z")
    records = [article("2024-01-09T00:00:00Z")]
    http_mocker.get(request, [HttpResponse('{"errors":["rate limited"]}', status_code=429), response_for(records)])
    monkeypatch.setattr(time, "sleep", lambda _: None)

    output = read_stream(stream_name, cursor="2024-01-05T12:00:00Z")

    assert output.errors == []
    assert [record.record.data for record in output.records] == records
    http_mocker.assert_number_of_calls(request, 2)
