# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests of the Grades.com manifest: auth, the v1 cursor, per-business partitioning, incremental request
parameters, the review-text flag, rate limiting and skipped businesses. No network: every request is mocked."""

import json
from pathlib import Path
from typing import Any, Mapping, Optional

import pytest
import yaml
from freezegun import freeze_time

from airbyte_cdk import YamlDeclarativeSource
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
_BASE = "https://app.grades.com/api/v1"
_KEY = "gk_live_unit_test_key_not_real"
_A = "11111111-1111-1111-1111-111111111111"
_B = "22222222-2222-2222-2222-222222222222"
_NOW = "2026-11-09T12:00:00Z"


def _config(**extra: Any) -> dict:
    return {"api_key": _KEY, **extra}


def _json(body: Any, status: int = 200, headers: Optional[Mapping[str, str]] = None) -> HttpResponse:
    return HttpResponse(json.dumps(body), status, headers or {})


def _company(uuid: str, name: str) -> dict:
    return {"uuid": uuid, "name": name, "slug": name.lower(), "timezone": "America/New_York", "hq_company": None}


def _companies(http: HttpMocker, *companies: dict) -> None:
    http.get(
        HttpRequest(f"{_BASE}/companies", query_params={"limit": "100"}),
        _json({"data": list(companies), "meta": {"count": len(companies), "next_cursor": None, "has_more": False}}),
    )


def _read(stream: str, config: dict, sync_mode: SyncMode = SyncMode.full_refresh, state: Optional[list] = None):
    catalog = CatalogBuilder().with_stream(stream, sync_mode).build()
    state = state if state is not None else StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_MANIFEST_PATH), catalog=catalog, config=config, state=state)
    return entrypoint_read(source, config, catalog, state)


def _review(uuid: str, published_at: str, **extra: Any) -> dict:
    return {
        "uuid": uuid,
        "source": "google",
        "rating": 5,
        "text": "Great visit",
        "title": "Five stars",
        "author": "Jane D.",
        "published_at": published_at,
        "response_text": None,
        "response_date": None,
        **extra,
    }


@pytest.fixture(scope="module")
def manifest() -> Mapping[str, Any]:
    with _MANIFEST_PATH.open() as handle:
        return yaml.safe_load(handle)


@freeze_time(_NOW)
def test_locations_follow_the_v1_cursor_and_send_the_bearer_key() -> None:
    with HttpMocker() as http:
        first = HttpRequest(f"{_BASE}/companies", query_params={"limit": "100"}, headers={"Authorization": f"Bearer {_KEY}"})
        second = HttpRequest(f"{_BASE}/companies", query_params={"limit": "100", "cursor": "page2"})
        http.get(first, _json({"data": [_company(_A, "Alpha")], "meta": {"next_cursor": "page2", "has_more": True}}))
        http.get(second, _json({"data": [_company(_B, "Beta")], "meta": {"next_cursor": None, "has_more": False}}))

        output = _read("locations", _config())

    assert [r.record.data["uuid"] for r in output.records] == [_A, _B]
    assert not output.errors


@freeze_time(_NOW)
def test_company_uuids_limit_the_partitions() -> None:
    with HttpMocker() as http:
        _companies(http, _company(_A, "Alpha"), _company(_B, "Beta"))
        http.get(
            HttpRequest(f"{_BASE}/companies/{_A}/sources"),
            _json({"data": [{"driver": "google", "display_name": "Google", "active": True}], "meta": {"count": 1}}),
        )

        output = _read("sources", _config(company_uuids=[_A]))

    assert [(r.record.data["company_uuid"], r.record.data["driver"]) for r in output.records] == [(_A, "google")]


@freeze_time(_NOW)
def test_reviews_incremental_sends_the_publish_date_window_and_emits_state() -> None:
    with HttpMocker() as http:
        _companies(http, _company(_A, "Alpha"))
        page1 = HttpRequest(
            f"{_BASE}/companies/{_A}/reviews",
            query_params={
                "sort": "oldest",
                "include_removed": "true",
                "start_date": "2026-01-01",
                "end_date": "2026-11-09",
                "limit": "100",
            },
        )
        page2 = HttpRequest(
            f"{_BASE}/companies/{_A}/reviews",
            query_params={
                "sort": "oldest",
                "include_removed": "true",
                "start_date": "2026-01-01",
                "end_date": "2026-11-09",
                "limit": "100",
                "cursor": "next",
            },
        )
        http.get(page1, _json({"data": [_review("r1", "2026-03-01T10:00:00Z")], "meta": {"next_cursor": "next", "has_more": True}}))
        http.get(
            page2,
            _json(
                {
                    "data": [_review("r2", "2026-10-01T10:00:00Z", removed_at="2026-10-20T00:00:00Z")],
                    "meta": {"next_cursor": None, "has_more": False},
                }
            ),
        )

        output = _read("reviews", _config(start_date="2026-01-01"), SyncMode.incremental)

    records = [r.record.data for r in output.records]
    assert [r["uuid"] for r in records] == ["r1", "r2"]
    assert all(r["company_uuid"] == _A for r in records)
    assert records[0]["text"] == "Great visit"
    assert output.state_messages, "an incremental read emits state"
    assert not output.errors


@freeze_time(_NOW)
def test_reviews_without_text_when_the_flag_is_off() -> None:
    with HttpMocker() as http:
        _companies(http, _company(_A, "Alpha"))
        http.get(
            HttpRequest(
                f"{_BASE}/companies/{_A}/reviews",
                query_params={
                    "sort": "oldest",
                    "include_removed": "true",
                    "start_date": "2026-06-01",
                    "end_date": "2026-11-09",
                    "limit": "100",
                },
            ),
            _json({"data": [_review("r1", "2026-07-01T10:00:00Z")], "meta": {"next_cursor": None}}),
        )

        output = _read("reviews", _config(start_date="2026-06-01", include_review_text=False))

    assert output.records, " | ".join([str(e)[:3000] for e in output.errors] + [m.log.message for m in output.logs[-6:]])
    data = output.records[0].record.data
    assert data.get("text") is None and data.get("title") is None
    assert data["rating"] == 5 and data["author"] == "Jane D."


@freeze_time(_NOW)
def test_review_replies_keep_only_reply_fields() -> None:
    with HttpMocker() as http:
        _companies(http, _company(_A, "Alpha"))
        http.get(
            HttpRequest(
                f"{_BASE}/companies/{_A}/reviews",
                query_params={"sort": "oldest", "include_removed": "true", "has_company_response": "true", "limit": "100"},
            ),
            _json(
                {
                    "data": [
                        _review(
                            "r1",
                            "2026-07-01T10:00:00Z",
                            response_text="Thanks!",
                            response_date="2026-07-02T09:00:00Z",
                            response_author="Alpha",
                        )
                    ],
                    "meta": {"next_cursor": None},
                }
            ),
        )

        output = _read("review_replies", _config())

    data = output.records[0].record.data
    assert data["review_uuid"] == "r1" and data["response_text"] == "Thanks!"
    assert "text" not in data and "uuid" not in data and "author" not in data


@freeze_time(_NOW)
def test_429_waits_for_retry_after_then_succeeds() -> None:
    with HttpMocker() as http:
        _companies(http, _company(_A, "Alpha"))
        http.get(
            HttpRequest(f"{_BASE}/companies/{_A}/stats"),
            [
                _json({"title": "Too Many Requests", "status": 429}, 429, {"Retry-After": "1"}),
                _json({"data": {"total": 3, "average_rating": 4.67, "ratings": {"5": 2, "4": 1}}, "meta": {}}),
            ],
        )

        output = _read("review_stats", _config())

    assert [r.record.data["total"] for r in output.records] == [3]
    assert not output.errors


@freeze_time(_NOW)
def test_a_business_without_the_feature_is_skipped_not_failed() -> None:
    with HttpMocker() as http:
        _companies(http, _company(_A, "Alpha"), _company(_B, "Beta"))
        http.get(
            HttpRequest(f"{_BASE}/companies/{_A}/stats"),
            _json({"title": "Payment Required", "status": 402, "code": "plan_upgrade_required"}, 402),
        )
        http.get(HttpRequest(f"{_BASE}/companies/{_B}/stats"), _json({"data": {"total": 1, "average_rating": 5.0}, "meta": {}}))

        output = _read("review_stats", _config())

    assert [r.record.data["company_uuid"] for r in output.records] == [_B]
    assert not output.errors


@freeze_time(_NOW)
def test_missing_scope_fails_as_a_config_error() -> None:
    with HttpMocker() as http:
        http.get(
            HttpRequest(f"{_BASE}/companies", query_params={"limit": "100"}),
            _json({"title": "Forbidden", "status": 403, "required_scopes": ["companies:read"]}, 403),
        )

        output = _read("locations", _config())

    assert output.errors
    assert "scope" in output.errors[-1].trace.error.message


@freeze_time(_NOW)
def test_daily_stats_one_request_per_day_and_location_rows() -> None:
    with HttpMocker() as http:
        _companies(http, _company(_A, "Alpha"))
        for day in ("2026-11-07", "2026-11-08", "2026-11-09"):
            http.get(
                HttpRequest(f"{_BASE}/companies/{_A}/locations/stats", query_params={"from": day, "to": day}),
                _json(
                    {
                        "data": {
                            "totals": {},
                            "locations": [
                                {
                                    "location": {"uuid": _A, "name": "Alpha", "is_hq": True},
                                    "reviews_total": 40,
                                    "rating_average": 4.5,
                                    "new_reviews": 1,
                                    "new_rating_average": 5.0,
                                    "responded": 1,
                                    "response_rate": 1.0,
                                    "unanswered_negative": 0,
                                    "pending_agent_actions": 2,
                                    "rank": None,
                                    "rating_distribution": {"5": 1},
                                }
                            ],
                        },
                        "meta": {},
                    }
                ),
            )

        output = _read("review_stats_daily", _config(stats_start_date="2026-11-07"), SyncMode.incremental)

    rows = [r.record.data for r in output.records]
    assert sorted(r["date"] for r in rows) == ["2026-11-07", "2026-11-08", "2026-11-09"]
    assert all(r["company_uuid"] == _A and r["group_company_uuid"] == _A for r in rows)
    assert "reviews_total" not in rows[0] and "pending_agent_actions" not in rows[0]


@freeze_time(_NOW)
def test_daily_stats_skip_a_location_whose_hq_holds_the_group_view() -> None:
    with HttpMocker() as http:
        _companies(http, _company(_A, "Alpha"))
        http.get(
            HttpRequest(f"{_BASE}/companies/{_A}/locations/stats", query_params={"from": "2026-11-09", "to": "2026-11-09"}),
            _json({"title": "Conflict", "status": 409, "code": "not_an_hq"}, 409),
        )

        output = _read("review_stats_daily", _config(stats_start_date="2026-11-09"), SyncMode.incremental)

    assert not output.records and not output.errors


@freeze_time(_NOW)
def test_ai_reputation_history_asks_each_assistant_since_the_start() -> None:
    with HttpMocker() as http:
        _companies(http, _company(_A, "Alpha"))
        for engine in ("gemini", "openai", "perplexity", "anthropic"):
            http.get(
                HttpRequest(
                    f"{_BASE}/companies/{_A}/radar/ai-perception", query_params={"engine": engine, "since": "2026-10-01T00:00:00Z"}
                ),
                _json(
                    {
                        "data": {
                            "summary": [],
                            "probes": [],
                            "history": [
                                {
                                    "run_id": f"run-{engine}",
                                    "engine": engine,
                                    "run_at": "2026-11-01T14:00:00Z",
                                    "sentiment": "positive",
                                    "score": 0.8,
                                }
                            ],
                        },
                        "meta": {},
                    }
                ),
            )

        output = _read("ai_reputation_history", _config(start_date="2026-10-01"), SyncMode.incremental)

    assert sorted(r.record.data["engine"] for r in output.records) == ["anthropic", "gemini", "openai", "perplexity"]


def test_every_stream_has_a_schema_with_its_primary_key() -> None:
    import logging

    catalog = YamlDeclarativeSource(path_to_yaml=str(_MANIFEST_PATH)).discover(logging.getLogger("test"), _config())
    assert len(catalog.streams) == 16
    for stream in catalog.streams:
        properties = stream.json_schema["properties"]
        assert stream.source_defined_primary_key, stream.name
        for key in stream.source_defined_primary_key:
            assert key[0] in properties, f"{stream.name}: {key[0]}"
            assert "null" not in properties[key[0]]["type"], f"{stream.name}: {key[0]} is nullable"


def test_error_handler_honours_retry_after_first(manifest: Mapping[str, Any]) -> None:
    for name in ("error_handler", "company_error_handler"):
        strategies = manifest["definitions"][name]["backoff_strategies"]
        assert strategies[0] == {"type": "WaitTimeFromHeader", "header": "Retry-After"}


@freeze_time(_NOW)
def test_a_key_pasted_with_trailing_whitespace_is_trimmed() -> None:
    with HttpMocker() as http:
        request = HttpRequest(f"{_BASE}/companies", query_params={"limit": "100"}, headers={"Authorization": f"Bearer {_KEY}"})
        http.get(request, _json({"data": [_company(_A, "Alpha")], "meta": {"next_cursor": None, "has_more": False}}))

        output = _read("locations", _config(api_key=f" {_KEY} \n"))

    assert [r.record.data["uuid"] for r in output.records] == [_A]
    assert not output.errors


_SCOPE_403 = {
    "title": "Forbidden",
    "status": 403,
    "required_scopes": ["reviews:read"],
    "detail": "This API key or app connection does not have the reviews:read permission this request needs.",
}


def _check(config: dict):
    import logging

    # The platform builds the source with the config (entrypoint), and the streams take the key from it.
    return YamlDeclarativeSource(path_to_yaml=str(_MANIFEST_PATH), config=config).check(logging.getLogger("test"), config)


@freeze_time(_NOW)
def test_check_fails_with_the_scope_text_for_a_key_without_reviews_read() -> None:
    with HttpMocker() as http:
        _companies(http, _company(_A, "Alpha"))
        http.get(HttpRequest(f"{_BASE}/companies/{_A}/stats"), _json(_SCOPE_403, 403))

        status = _check(_config())

    assert status.status.name == "FAILED"
    assert "review_stats" in status.message
    assert "lacks a scope" in status.message and "reviews:read and companies:read" in status.message


@freeze_time(_NOW)
def test_check_succeeds_with_both_scopes() -> None:
    with HttpMocker() as http:
        bearer = {"Authorization": f"Bearer {_KEY}"}
        http.get(
            HttpRequest(f"{_BASE}/companies", query_params={"limit": "100"}, headers=bearer),
            _json({"data": [_company(_A, "Alpha")], "meta": {"next_cursor": None, "has_more": False}}),
        )
        http.get(
            HttpRequest(f"{_BASE}/companies/{_A}/stats", headers=bearer), _json({"data": {"total": 3, "average_rating": 4.67}, "meta": {}})
        )

        status = _check(_config())

    assert status.status.name == "SUCCEEDED", status.message


@freeze_time(_NOW)
@pytest.mark.parametrize(
    "stream,path",
    [
        ("review_stats_daily", "locations/stats"),
        ("review_request_stats_daily", "review-requests/stats"),
    ],
)
def test_daily_stats_stop_after_the_first_scope_error(stream: str, path: str) -> None:
    with HttpMocker() as http:
        _companies(http, _company(_A, "Alpha"), _company(_B, "Beta"))
        http.get(
            HttpRequest(f"{_BASE}/companies/{_A}/{path}", query_params={"from": "2026-11-09", "to": "2026-11-09"}), _json(_SCOPE_403, 403)
        )

        # 90 days of stats: before the probe, a key without the scope sent one failing request per business and day.
        output = _read(stream, _config(stats_start_date="2026-08-11"), SyncMode.incremental)
        calls = [r.url for r in http._mocker.request_history if f"/{path}" in r.url]

    assert len(calls) == 1, calls
    assert not output.records
    assert output.errors
    assert any("lacks a scope" in e.trace.error.message for e in output.errors)


@freeze_time(_NOW)
def test_review_request_stats_daily_one_row_per_day() -> None:
    with HttpMocker() as http:
        _companies(http, _company(_A, "Alpha"))
        for day in ("2026-11-08", "2026-11-09"):
            http.get(
                HttpRequest(f"{_BASE}/companies/{_A}/review-requests/stats", query_params={"from": day, "to": day}),
                _json({"data": {"totals": {"created": 2, "sent": 2, "opened": 1, "reviewed": 0}}, "meta": {}}),
            )

        output = _read("review_request_stats_daily", _config(stats_start_date="2026-11-08"), SyncMode.incremental)

    rows = [r.record.data for r in output.records]
    assert sorted(r["date"] for r in rows) == ["2026-11-08", "2026-11-09"]
    assert all(r["company_uuid"] == _A and r["created"] == 2 for r in rows)
    assert not output.errors
