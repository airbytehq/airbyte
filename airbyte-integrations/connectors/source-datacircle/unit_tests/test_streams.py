# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
from jsonschema import Draft7Validator
from requests_mock import ANY, Mocker

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
_URL = "https://api.datacircle.dev/v1"
_UNEXPECTED_REQUEST = {"status_code": 418, "json": {"error": "The test did not expect this request."}}
_APIS = [
    {
        "api": "Employee profile",
        "slug": "linkedin-profile",
        "plans": 2,
        "providers": 2,
        "sheetPage": "https://datacircle.dev/linkedin-profile-api-pricing",
        "bestPage": "https://datacircle.dev/best-linkedin-profile-api",
        "best": {"provider": "Bridgly", "plan": "Scale", "score": 78.3, "perThousand": 1},
    },
    {
        "api": "Employee email",
        "slug": "email-finder",
        "plans": 1,
        "providers": 1,
        "sheetPage": "https://datacircle.dev/email-finder-api-pricing",
        "bestPage": None,
        "best": None,
    },
]


def _plan(provider: str, rank: int | None = None, api: str = "Employee profile") -> dict:
    return {
        "provider": provider,
        "api": api,
        "website": "https://example.com",
        "plan": "Scale",
        "billing": "monthly",
        "pay": 49,
        "currency": "USD",
        "score": 78.3,
        "perThousand": 1.25,
        "strengths": ["under $2 per 1,000"],
        "aggregators": [],
        "fields": ["full_name", "headline"],
        "perWindow": None,
        "batch": "no batch",
        "page": "https://datacircle.dev/linkedin-profile-api-pricing/bridgly-scale",
        "rank": rank,
    }


@pytest.fixture(autouse=True)
def isolated_http(requests_mock: Mocker, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # The CDK caches parent-stream responses in a SQLite file. Keep that file out of `unit_tests/` and out of other tests.
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
    # Registered first, so the mocks of each test take precedence: a request no mock matches fails the read.
    requests_mock.register_uri(ANY, ANY, **_UNEXPECTED_REQUEST)


def _source(config: dict) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH), catalog=CatalogBuilder().build(), config=config, state=StateBuilder().build()
    )


def _read(stream: str, config: dict, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build()
    return read(_source(config), config, catalog, expecting_exception=expecting_exception)


def _records(output: EntrypointOutput) -> list:
    return [message.record.data for message in output.records]


def _query(requests_mock: Mocker, path: str) -> list[dict]:
    return [parse_qs(urlsplit(r.url).query) for r in requests_mock.request_history if r.path == f"/v1{path}"]


def _assert_match_schema(stream: str, records: list) -> None:
    [catalog_stream] = [s for s in _source({}).discover(logging.getLogger("airbyte"), {}).streams if s.name == stream]
    validator = Draft7Validator(catalog_stream.json_schema)
    for record in records:
        assert not list(validator.iter_errors(record)), record


def test_discover_publishes_four_streams_with_their_keys() -> None:
    streams = {s.name: s for s in _source({}).discover(logging.getLogger("airbyte"), {}).streams}

    assert {name: s.source_defined_primary_key for name, s in streams.items()} == {
        "apis": [["slug"]],
        "best_plans": [["api_slug"], ["rank"]],
        "plans": None,
        "providers": [["slug"]],
    }
    assert {"provider", "plan", "perThousand", "score", "fields", "rank"} <= set(streams["plans"].json_schema["properties"])


def test_check_reads_apis_and_plans(requests_mock: Mocker) -> None:
    requests_mock.get(f"{_URL}/apis", json=_APIS)
    requests_mock.get(f"{_URL}/plans", json={"total": 1, "offset": 0, "plans": [_plan("Bridgly")]})

    status = _source({}).check(logging.getLogger("airbyte"), {})

    assert status.status == Status.SUCCEEDED


def test_check_fails_with_the_api_message_on_an_unknown_api(requests_mock: Mocker) -> None:
    requests_mock.get(f"{_URL}/apis", json=_APIS)
    requests_mock.get(f"{_URL}/plans", status_code=400, json={"error": "api must be one of: Employee profile, Employee email"})

    status = _source({"api": "nope"}).check(logging.getLogger("airbyte"), {"api": "nope"})

    assert status.status == Status.FAILED
    assert "api must be one of" in status.message


def test_apis_reads_the_list(requests_mock: Mocker) -> None:
    requests_mock.get(f"{_URL}/apis", json=_APIS)

    records = _records(_read("apis", {}))

    assert [r["slug"] for r in records] == ["linkedin-profile", "email-finder"]
    _assert_match_schema("apis", records)


def test_plans_pages_by_offset_until_a_short_page(requests_mock: Mocker) -> None:
    full = [_plan(f"Provider {i}") for i in range(50)]
    requests_mock.get(
        f"{_URL}/plans",
        [
            {"json": {"total": 52, "offset": 0, "plans": full}},
            {"json": {"total": 52, "offset": 50, "plans": [_plan("Last 1"), _plan("Last 2")]}},
            _UNEXPECTED_REQUEST,
        ],
    )

    records = _records(_read("plans", {"api": " linkedin-profile ", "query": "scale"}))

    assert len(records) == 52
    first, second = _query(requests_mock, "/plans")
    assert first == {"api": ["linkedin-profile"], "query": ["scale"], "sort": ["score"], "limit": ["50"]}
    assert second == {**first, "offset": ["50"]}
    _assert_match_schema("plans", records)


def test_plans_leaves_out_the_filters_left_empty(requests_mock: Mocker) -> None:
    requests_mock.get(f"{_URL}/plans", json={"total": 1, "offset": 0, "plans": [_plan("Bridgly")]})

    _read("plans", {})

    assert _query(requests_mock, "/plans") == [{"sort": ["score"], "limit": ["50"]}]


def test_plans_fails_with_the_api_message_on_a_bad_filter(requests_mock: Mocker) -> None:
    requests_mock.get(f"{_URL}/plans", status_code=400, json={"error": "api must be one of: Employee profile"})

    output = _read("plans", {"api": "nope"}, expecting_exception=True)

    assert any("api must be one of" in str(error.trace.error.message) for error in output.errors)


@pytest.mark.parametrize("api", [None, "email-finder", "employee EMAIL"])
def test_best_plans_reads_each_api_or_the_one_set(requests_mock: Mocker, api: str | None) -> None:
    requests_mock.get(f"{_URL}/apis", json=_APIS)
    requests_mock.get(f"{_URL}/apis/linkedin-profile/best", json={"slug": "linkedin-profile", "plans": [_plan("Bridgly", 1), _plan("Other", 2)]})
    requests_mock.get(f"{_URL}/apis/email-finder/best", json={"slug": "email-finder", "plans": [_plan("Finder", 1, "Employee email")]})

    records = _records(_read("best_plans", {"api": api, "best_plans_limit": 3} if api else {}))

    expected = [("email-finder", 1)] if api else [("linkedin-profile", 1), ("linkedin-profile", 2), ("email-finder", 1)]
    assert sorted((r["api_slug"], r["rank"]) for r in records) == sorted(expected)
    assert {q["limit"][0] for q in _query(requests_mock, "/apis/email-finder/best")} == {"3" if api else "10"}
    _assert_match_schema("best_plans", records)


def test_best_plans_skips_an_api_gone_since_the_list(requests_mock: Mocker) -> None:
    requests_mock.get(f"{_URL}/apis", json=_APIS)
    requests_mock.get(f"{_URL}/apis/linkedin-profile/best", status_code=404, json={"error": "no API has the slug linkedin-profile"})
    requests_mock.get(f"{_URL}/apis/email-finder/best", json={"slug": "email-finder", "plans": [_plan("Finder", 1)]})

    output = _read("best_plans", {})

    assert [r["api_slug"] for r in _records(output)] == ["email-finder"]
    assert output.errors == []


def test_providers_reads_each_configured_slug(requests_mock: Mocker) -> None:
    for slug, name in (("bridgly", "Bridgly"), ("bright-data", "Bright Data")):
        requests_mock.get(
            f"{_URL}/providers/{slug}",
            json={"provider": name, "slug": slug, "website": "https://example.com", "apis": [{"api": "Employee profile", "slug": "linkedin-profile", "rank": 1, "sheetPage": None, "bestPage": None, "plans": [_plan(name, 1)]}]},
        )

    records = _records(_read("providers", {"providers": ["bridgly", "bright-data"]}))

    assert sorted(r["slug"] for r in records) == ["bridgly", "bright-data"]
    _assert_match_schema("providers", records)


def test_providers_reads_none_when_none_is_set() -> None:
    output = _read("providers", {})

    assert _records(output) == []
    assert output.errors == []


def test_providers_fails_with_the_api_message_on_an_unknown_slug(requests_mock: Mocker) -> None:
    requests_mock.get(f"{_URL}/providers/nope", status_code=404, json={"error": "no provider has the slug nope"})

    output = _read("providers", {"providers": ["nope"]}, expecting_exception=True)

    assert any("no provider has the slug nope" in str(error.trace.error.message) for error in output.errors)


def test_a_429_waits_for_retry_after_then_reads(requests_mock: Mocker) -> None:
    requests_mock.get(
        f"{_URL}/apis",
        [{"status_code": 429, "headers": {"Retry-After": "1"}, "json": {"error": "more than 60 calls in a minute"}}, {"json": _APIS}],
    )

    records = _records(_read("apis", {}))

    assert len(records) == 2
    assert len(_query(requests_mock, "/apis")) == 2
