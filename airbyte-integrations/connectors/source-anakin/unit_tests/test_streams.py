# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import (
    YamlDeclarativeSource,
)
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder
from requests_mock import ANY, Mocker

_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
_URL = "https://api.anakin.io/v1"
_CONFIG = {"api_key": "ask_test"}
_UNEXPECTED_REQUEST = {
    "status_code": 400,
    "json": {"error": "The test did not expect this request."},
}


@pytest.fixture(autouse=True)
def isolated_http(
    requests_mock: Mocker, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # The CDK caches parent-stream responses in a SQLite file. Keep that file out of `unit_tests/` and out of other tests.
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
    # Registered first, so the mocks of each test take precedence.
    requests_mock.register_uri(ANY, ANY, **_UNEXPECTED_REQUEST)


def _read(
    stream: str,
    config: dict,
    sync_mode: SyncMode = SyncMode.full_refresh,
    state: list | None = None,
) -> EntrypointOutput:
    source = YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=CatalogBuilder().build(),
        config=config,
        state=state or StateBuilder().build(),
    )
    return read(
        source, config, CatalogBuilder().with_stream(stream, sync_mode).build(), state
    )


def _records(output: EntrypointOutput) -> list:
    return [message.record.data for message in output.records]


def test_monitors(requests_mock: Mocker) -> None:
    requests_mock.get(
        f"{_URL}/monitors",
        json={"monitors": [{"id": "m1", "url": "https://example.com"}, {"id": "m2"}]},
    )

    output = _read("monitors", _CONFIG)

    assert output.errors == []
    assert [r["id"] for r in _records(output)] == ["m1", "m2"]
    assert requests_mock.last_request.headers["X-API-Key"] == "ask_test"


def test_invalid_api_key_is_a_config_error(requests_mock: Mocker) -> None:
    requests_mock.get(
        f"{_URL}/monitors", status_code=401, json={"error": "unauthorized"}
    )

    output = _read("monitors", _CONFIG)

    assert output.errors
    assert output.errors[0].trace.error.failure_type == FailureType.config_error


def test_monitor_changes_incremental(requests_mock: Mocker) -> None:
    requests_mock.get(
        f"{_URL}/monitors", json={"monitors": [{"id": "m1"}, {"id": "m2"}]}
    )
    requests_mock.get(
        f"{_URL}/monitors/m1/changes",
        json={
            "changes": [
                {"id": "c2", "monitorId": "m1", "changedAt": "2026-03-02T10:00:00.5Z"},
                {"id": "c1", "monitorId": "m1", "changedAt": "2026-03-01T10:00:00Z"},
            ]
        },
    )
    requests_mock.get(f"{_URL}/monitors/m2/changes", json={"changes": []})

    first = _read("monitor_changes", _CONFIG, SyncMode.incremental)
    assert first.errors == []
    assert sorted(r["id"] for r in _records(first)) == ["c1", "c2"]

    state = (
        StateBuilder()
        .with_stream_state(
            "monitor_changes", first.most_recent_state.stream_state.__dict__
        )
        .build()
    )
    second = _read("monitor_changes", _CONFIG, SyncMode.incremental, state)
    assert second.errors == []
    # Changes older than the saved cursor are filtered out.
    assert "c1" not in [r["id"] for r in _records(second)]


def test_search_results_one_request_per_query(requests_mock: Mocker) -> None:
    def respond(request, context):
        body = request.json()
        return {
            "id": "s1",
            "results": [
                {"url": f"https://r{i}.example", "title": body["prompt"]}
                for i in range(body["limit"])
            ],
        }

    requests_mock.post(f"{_URL}/search", json=respond)
    config = {
        **_CONFIG,
        "search_queries": ["first query", "second query"],
        "search_limit": 2,
    }

    output = _read("search_results", config)

    assert output.errors == []
    records = _records(output)
    assert len(records) == 4
    assert {r["query"] for r in records} == {"first query", "second query"}
    assert all(r["synced_at"] for r in records)
    assert [
        h.json() for h in requests_mock.request_history if h.path == "/v1/search"
    ] == [
        {"prompt": "first query", "limit": 2},
        {"prompt": "second query", "limit": 2},
    ]


def test_search_results_without_queries_makes_no_requests(
    requests_mock: Mocker,
) -> None:
    output = _read("search_results", _CONFIG)

    assert output.errors == []
    assert _records(output) == []
    assert not [h for h in requests_mock.request_history if h.path == "/v1/search"]


_SCRAPE_RESPONSE = {
    "id": "job_1",
    "status": "completed",
    "url": "https://example.com",
    "html": "<html></html>",
    "cleanedHtml": "<div></div>",
    "markdown": "# Example",
    "cached": False,
}


def test_scraped_pages_drops_html_by_default(requests_mock: Mocker) -> None:
    requests_mock.post(f"{_URL}/url-scraper/scrape", json=_SCRAPE_RESPONSE)
    config = {
        **_CONFIG,
        "urls": ["https://example.com"],
        "country": "gb",
        "use_browser": True,
    }

    output = _read("scraped_pages", config)

    assert output.errors == []
    [record] = _records(output)
    assert record["markdown"] == "# Example"
    assert record["requested_url"] == "https://example.com"
    assert record.get("html") is None and record.get("cleanedHtml") is None
    assert requests_mock.last_request.json() == {
        "url": "https://example.com",
        "country": "gb",
        "useBrowser": True,
        "generateJson": False,
    }


def test_scraped_pages_keeps_html_when_requested(requests_mock: Mocker) -> None:
    requests_mock.post(f"{_URL}/url-scraper/scrape", json=_SCRAPE_RESPONSE)
    config = {**_CONFIG, "urls": ["https://example.com"], "include_html": True}

    [record] = _records(_read("scraped_pages", config))

    assert record["html"] == "<html></html>"
    assert record["cleanedHtml"] == "<div></div>"


def test_scraped_pages_retries_unfinished_scrape(
    requests_mock: Mocker, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("time.sleep", lambda _: None)
    requests_mock.post(
        f"{_URL}/url-scraper/scrape",
        [
            {"status_code": 202, "json": {"id": "job_1", "status": "processing"}},
            {"json": _SCRAPE_RESPONSE},
        ],
    )

    output = _read("scraped_pages", {**_CONFIG, "urls": ["https://example.com"]})

    assert output.errors == []
    assert [r["status"] for r in _records(output)] == ["completed"]
