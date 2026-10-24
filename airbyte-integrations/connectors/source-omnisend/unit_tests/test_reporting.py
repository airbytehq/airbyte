# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Offline behavior tests against the connector's pinned declarative CDK.

Run with airbyte-cdk==6.48.10, pytest and requests-mock. All records and keys are
synthetic; no live Omnisend request or account is required.
"""

import logging
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path

import pytest
import requests
import yaml
from jsonschema import Draft7Validator, FormatChecker, ValidationError

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource
from airbyte_cdk.sources.streams.call_rate import CallRateLimitHit


MANIFEST_PATH = Path(__file__).parents[1] / "manifest.yaml"
LEGACY = ["contacts", "campaigns", "carts", "orders", "products"]
NEW = [
    "brand",
    "campaigns_v2026",
    "automations",
    "forms",
    "segments",
    "analytics_reports",
    "analytics_statistics",
    "form_reports",
    "analytics_reports_daily",
    "analytics_statistics_daily",
]
BASE_URL = "https://api.omnisend.com"
LOGGER = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def isolated_request_cache(tmp_path, monkeypatch):
    # CDK parent streams cache native HTTP responses; never share them across cases.
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))


@pytest.fixture
def manifest():
    return yaml.safe_load(MANIFEST_PATH.read_text())


@pytest.fixture
def config():
    return {"api_key": "synthetic-legacy-key", "enable_reporting": True}


def source(manifest, config):
    return ConcurrentDeclarativeSource(source_config=deepcopy(manifest), config=config, catalog=None, state=None)


def streams(manifest, config):
    return {stream.name: stream for stream in source(manifest, config).streams(config)}


def read(stream):
    return [
        dict(record)
        for partition in stream.stream_slices(sync_mode=SyncMode.full_refresh)
        for record in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=partition)
    ]


def test_spec_and_discovery_remain_compatible_with_api_key_only(manifest):
    config = {"api_key": "synthetic-legacy-key"}
    connector = source(manifest, config)
    spec = connector.spec(LOGGER).connectionSpecification
    Draft7Validator(spec).validate(config)
    assert spec["required"] == ["api_key"]
    catalog = connector.discover(LOGGER, config)
    assert [stream.name for stream in catalog.streams] == LEGACY + NEW
    assert all(stream.supported_sync_modes == [SyncMode.full_refresh] for stream in catalog.streams)


@pytest.mark.parametrize("name", NEW)
def test_new_streams_are_disabled_without_opt_in(manifest, name, requests_mock):
    config = {"api_key": "synthetic-legacy-key"}
    assert read(streams(manifest, config)[name]) == []
    assert requests_mock.call_count == 0


@pytest.mark.parametrize(
    "name,selector,id_field",
    [
        ("contacts", "contacts", "contactID"),
        ("campaigns", "campaign", "campaignID"),
        ("carts", "carts", "cartID"),
        ("orders", "orders", "orderID"),
        ("products", "products", "productID"),
    ],
)
def test_legacy_requests_and_schema_unchanged(manifest, config, requests_mock, name, selector, id_field):
    url = f"{BASE_URL}/v3/{name}"
    requests_mock.get(url, json={selector: [{id_field: "synthetic-entity"}], "paging": {"next": None}})
    stream = streams(manifest, config)[name]
    assert read(stream) == [{id_field: "synthetic-entity"}]
    request = requests_mock.last_request
    assert request.headers["X-API-KEY"] == config["api_key"]
    assert "Authorization" not in request.headers
    assert "Omnisend-Version" not in request.headers
    assert request.qs["limit"] == ["100"]
    assert stream.primary_key == [id_field]


def test_check_still_uses_legacy_contacts(manifest, requests_mock):
    config = {"api_key": "synthetic-legacy-key"}
    requests_mock.get(f"{BASE_URL}/v3/contacts", json={"contacts": [], "paging": {"next": None}})
    assert source(manifest, config).check_connection(LOGGER, config)[0]
    assert all(request.path == "/v3/contacts" for request in requests_mock.request_history)


@pytest.mark.parametrize("separate_key", [False, True])
def test_new_auth_and_version_are_separate_from_legacy(manifest, config, requests_mock, separate_key):
    if separate_key:
        config["reporting_api_key"] = "synthetic-reporting-key"
    requests_mock.get(f"{BASE_URL}/api/brands/current", json={"brandID": "synthetic-brand", "currency": "EUR"})
    assert read(streams(manifest, config)["brand"])[0]["brandID"] == "synthetic-brand"
    assert requests_mock.last_request.headers["Authorization"] == f"Omnisend-API-Key {config.get('reporting_api_key', config['api_key'])}"
    assert requests_mock.last_request.headers["Omnisend-Version"] == "2026-03-15"
    assert "X-API-KEY" not in requests_mock.last_request.headers


@pytest.mark.parametrize(
    "name,path,limit",
    [
        ("campaigns_v2026", "campaigns", "250"),
        ("automations", "automations", "250"),
        ("forms", "forms", "250"),
        ("segments", "segments", "50"),
    ],
)
def test_opaque_pagination_reaches_empty_terminal_page(manifest, config, requests_mock, name, path, limit):
    id_field = "segmentID" if name == "segments" else "id"
    requests_mock.get(
        f"{BASE_URL}/api/{path}",
        [
            {
                "json": {
                    path: [{id_field: "synthetic-first", "name": None}],
                    "paging": {"hasMore": True, "cursors": {"after": "opaque/+=="}},
                }
            },
            {"json": {path: [], "paging": {"hasMore": False}}},
        ],
    )
    assert read(streams(manifest, config)[name]) == [{id_field: "synthetic-first", "name": None}]
    assert requests_mock.call_count == 2
    assert requests_mock.request_history[0].qs["limit"] == [limit]
    assert requests_mock.last_request.qs["after"] == ["opaque/+=="]


def report_response(request, context):
    root = "reports" if request.path.endswith("reports") else "statistics"
    return {
        root: [
            {
                "alias": query["alias"],
                "metrics": query["metrics"],
                "dimensions": query["dimensions"],
                "rows": [{"sent": 0, "clickedUnique": None}],
            }
            for query in request.json()["queries"]
        ]
    }


def test_monthly_reports_keep_interval_uniques_and_native_nulls(manifest, config, requests_mock):
    requests_mock.post(f"{BASE_URL}/api/analytics/reports", json=report_response)
    records = read(streams(manifest, config)["analytics_reports"])
    assert len(records) == 4
    assert {row["query_period"] for row in records} == {"lastMonth"}
    assert {row["date_basis"] for row in records} == {"send"}
    queries = requests_mock.last_request.json()["queries"]
    assert all(query["dateRange"] == {"interval": "lastMonth"} for query in queries)
    assert all("timestamp" not in [dimension["name"] for dimension in query["dimensions"]] for query in queries)
    assert all(row["rows"] == [{"sent": 0, "clickedUnique": None}] for row in records)
    assert queries[2]["filters"] == [{"name": "marketingActivityType", "operator": "in", "values": ["Automation"]}]


def test_daily_reports_use_daily_send_cohorts(manifest, config, requests_mock):
    requests_mock.post(f"{BASE_URL}/api/analytics/reports", json=report_response)
    records = read(streams(manifest, config)["analytics_reports_daily"])
    query = requests_mock.last_request.json()["queries"][0]
    assert query["dimensions"] == [{"name": "timestamp", "granularity": "day"}, {"name": "marketingActivityType"}]
    assert query["dateRange"] == {"interval": "lastMonth"}
    assert records[0]["date_basis"] == "send"
    assert records[0]["rows"][0]["sent"] == 0
    assert records[0]["rows"][0]["clickedUnique"] is None


@pytest.mark.parametrize(
    "name,window_key,granularity",
    [
        ("analytics_statistics", "statistics_windows", "month"),
        ("analytics_statistics_daily", "daily_statistics_windows", "hour"),
    ],
)
def test_statistics_keep_explicit_exclusive_windows_and_empty_envelopes(manifest, config, requests_mock, name, window_key, granularity):
    config[window_key] = [{"from": "2026-10-24T21:00:00Z", "to": "2026-10-25T22:00:00Z"}]

    def empty_response(request, context):
        response = report_response(request, context)
        for report in response["statistics"]:
            report["rows"] = []
        return response

    requests_mock.post(f"{BASE_URL}/api/analytics/statistics", json=empty_response)
    records = read(streams(manifest, config)[name])
    assert len(records) == (4 if granularity == "month" else 1)
    assert all(row["rows"] == [] and row["date_basis"] == "event" for row in records)
    assert all(row["query_window_start"] == config[window_key][0]["from"] for row in records)
    assert all(row["query_window_end"] == config[window_key][0]["to"] for row in records)
    for query in requests_mock.last_request.json()["queries"]:
        assert query["dateRange"] == config[window_key][0]
        assert query["dimensions"][0] == {"name": "timestamp", "granularity": granularity}


def test_form_reports_use_parent_id_and_separate_inclusive_end(manifest, config, requests_mock):
    config["form_report_windows"] = [{"from": "2026-09-01T00:00:00Z", "to": "2026-09-30T23:59:59.999999Z"}]
    requests_mock.get(f"{BASE_URL}/api/forms", json={"forms": [{"id": "synthetic-form"}], "paging": {"hasMore": False}})
    requests_mock.get(
        f"{BASE_URL}/api/forms/synthetic-form/report/periodic", json={"formID": "synthetic-form", "granularity": "day", "rows": []}
    )
    records = read(streams(manifest, config)["form_reports"])
    assert records == [
        {
            "formID": "synthetic-form",
            "granularity": "day",
            "rows": [],
            "form_id": "synthetic-form",
            "date_basis": "form_activity",
            "query_window_start": config["form_report_windows"][0]["from"],
            "query_window_end": config["form_report_windows"][0]["to"],
        }
    ]
    assert requests_mock.last_request.qs["createdatfrom"] == [config["form_report_windows"][0]["from"].lower()]
    assert requests_mock.last_request.qs["createdatto"] == [config["form_report_windows"][0]["to"].lower()]


def test_explicit_utc_chunks_preserve_a_25_hour_local_day(manifest, config, requests_mock):
    # Real Europe/Athens October boundaries converted to UTC; slicing is caller-controlled.
    bounds = [
        "2026-09-30T21:00:00Z",
        "2026-10-07T21:00:00Z",
        "2026-10-14T21:00:00Z",
        "2026-10-21T21:00:00Z",
        "2026-10-28T21:00:00Z",
        "2026-10-31T22:00:00Z",
    ]
    config["daily_statistics_windows"] = [{"from": start, "to": end} for start, end in zip(bounds, bounds[1:])]
    requests_mock.post(f"{BASE_URL}/api/analytics/statistics", json=report_response)
    records = read(streams(manifest, config)["analytics_statistics_daily"])
    sent = [request.json()["queries"][0]["dateRange"] for request in requests_mock.request_history]
    assert sent == config["daily_statistics_windows"]
    assert len(records) == 5
    parse = lambda text: datetime.fromisoformat(text.replace("Z", "+00:00"))
    assert all(parse(window["to"]) - parse(window["from"]) <= timedelta(days=7) for window in sent)
    assert parse(sent[-1]["to"]) - parse(sent[0]["from"]) == timedelta(days=31, hours=1)


@pytest.mark.parametrize("key", ["statistics_windows", "form_report_windows", "daily_statistics_windows"])
def test_omitted_windows_make_no_report_requests(manifest, config, requests_mock, key):
    name = {
        "statistics_windows": "analytics_statistics",
        "form_report_windows": "form_reports",
        "daily_statistics_windows": "analytics_statistics_daily",
    }[key]
    # Form parent discovery may read form metadata, but must not request reports.
    requests_mock.get(f"{BASE_URL}/api/forms", json={"forms": [], "paging": {"hasMore": False}})
    assert read(streams(manifest, config)[name]) == []
    assert not any("report" in request.path or request.method == "POST" for request in requests_mock.request_history)


@pytest.mark.parametrize(
    "bad_window",
    [
        {"from": "2026-10-01", "to": "2026-10-02T00:00:00Z"},
        {"from": "2026-10-01T00:00:00+03:00", "to": "2026-10-02T00:00:00+03:00"},
        {"from": "2026-10-01T00:00:00Z"},
    ],
)
def test_daily_window_spec_rejects_non_utc_or_missing_bound(manifest, config, bad_window):
    config["daily_statistics_windows"] = [bad_window]
    spec = source(manifest, config).spec(LOGGER).connectionSpecification
    with pytest.raises(ValidationError):
        Draft7Validator(spec, format_checker=FormatChecker()).validate(config)


@pytest.mark.parametrize(
    "body,headers,expected",
    [
        ({"retryAfter": 86400}, {}, "86400"),
        ({}, {"Retry-After": "120"}, "120"),
        ({}, {}, "not supplied"),
    ],
)
def test_429_fails_without_retry_and_reports_wait_hint(manifest, config, requests_mock, body, headers, expected):
    requests_mock.post(f"{BASE_URL}/api/analytics/reports", status_code=429, json=body, headers=headers)
    with pytest.raises(Exception, match=f"retryAfter seconds: {expected}"):
        read(streams(manifest, config)["analytics_reports"])
    assert requests_mock.call_count == 1


@pytest.mark.parametrize("code", [400, 401, 403, 410, 415, 422])
def test_invalid_or_unpermitted_reporting_is_not_silently_ignored(manifest, config, requests_mock, code):
    requests_mock.post(f"{BASE_URL}/api/analytics/reports", status_code=code, json={"error": "synthetic request rejected"})
    with pytest.raises(Exception):
        read(streams(manifest, config)["analytics_reports"])
    assert requests_mock.call_count == 1


def test_transient_failure_retries_then_preserves_success(manifest, config, requests_mock, monkeypatch):
    monkeypatch.setattr("time.sleep", lambda seconds: None)
    requests_mock.post(
        f"{BASE_URL}/api/analytics/reports",
        [
            {"status_code": 503, "json": {"error": "synthetic transient error"}},
            {"json": {"reports": [{"alias": "overview", "rows": [], "metrics": [], "dimensions": []}]}},
        ],
    )
    assert read(streams(manifest, config)["analytics_reports"])[0]["rows"] == []
    assert requests_mock.call_count == 2


def test_analytics_sliding_budget_is_shared_and_does_not_throttle_legacy(manifest, config):
    connector = source(manifest, config)
    connector.streams(config)
    budget = connector._constructor._api_budget
    reports = requests.Request("POST", f"{BASE_URL}/api/analytics/reports").prepare()
    statistics = requests.Request("POST", f"{BASE_URL}/api/analytics/statistics").prepare()
    legacy = requests.Request("GET", f"{BASE_URL}/v3/contacts").prepare()
    policy = budget.get_matching_policy(reports)
    assert policy is budget.get_matching_policy(statistics)
    assert budget.get_matching_policy(legacy) is None
    for index in range(10):
        budget.acquire_call(reports if index % 2 else statistics, block=False)
    with pytest.raises(CallRateLimitHit):
        budget.acquire_call(reports, block=False)


def test_daily_quota_is_a_rolling_window_not_a_midnight_reset(manifest, config, monkeypatch):
    from pyrate_limiter.clocks import TimeClock

    clock = [0]
    monkeypatch.setattr(TimeClock, "now", lambda self: clock[0])
    connector = source(manifest, config)
    connector.streams(config)
    budget = connector._constructor._api_budget
    request = requests.Request("POST", f"{BASE_URL}/api/analytics/reports").prepare()
    # Spread calls across minutes so only the daily limit becomes binding.
    for index in range(55):
        clock[0] = (index // 10) * 61_000
        budget.acquire_call(request, block=False)
    clock[0] = 23 * 60 * 60 * 1000
    with pytest.raises(CallRateLimitHit):
        budget.acquire_call(request, block=False)
    clock[0] = 24 * 60 * 60 * 1000 + 1
    budget.acquire_call(request, block=False)


def test_server_failure_stops_after_three_retries(manifest, config, requests_mock, monkeypatch):
    monkeypatch.setattr("time.sleep", lambda seconds: None)
    requests_mock.post(f"{BASE_URL}/api/analytics/reports", status_code=503, json={"error": "synthetic unavailable"})
    with pytest.raises(Exception):
        read(streams(manifest, config)["analytics_reports"])
    assert requests_mock.call_count == 4


def test_rejected_oversize_hourly_window_fails_without_retry(manifest, config, requests_mock):
    # Cross-field span validation belongs to the API; never silently truncate it.
    config["daily_statistics_windows"] = [{"from": "2026-09-01T00:00:00Z", "to": "2026-09-09T00:00:00Z"}]
    requests_mock.post(f"{BASE_URL}/api/analytics/statistics", status_code=400, json={"error": "hourly range exceeds seven days"})
    with pytest.raises(Exception):
        read(streams(manifest, config)["analytics_statistics_daily"])
    assert requests_mock.call_count == 1
    assert requests_mock.last_request.json()["queries"][0]["dateRange"] == config["daily_statistics_windows"][0]


@pytest.mark.parametrize("name,root", [("analytics_reports", "reports"), ("analytics_statistics", "statistics")])
def test_report_envelopes_preserve_nested_native_rows_and_aliases(manifest, config, requests_mock, name, root):
    config["statistics_windows"] = [{"from": "2026-09-01T00:00:00Z", "to": "2026-10-01T00:00:00Z"}]
    payloads = []

    def response(request, context):
        records = [
            {
                "alias": query["alias"],
                "dimensions": query["dimensions"],
                "metrics": query["metrics"],
                "rows": [{"dimensions": {"marketingActivityType": "Campaign"}, "metrics": {"sent": 0, "clickedUnique": None}}],
            }
            for query in request.json()["queries"]
        ]
        payloads.extend(deepcopy(records))
        return {root: records}

    requests_mock.post(f"{BASE_URL}/api/analytics/{root}", json=response)
    records = read(streams(manifest, config)[name])
    assert [record["alias"] for record in records] == [query["alias"] for query in requests_mock.last_request.json()["queries"]]
    for actual, original in zip(records, payloads):
        assert {key: actual[key] for key in original} == original
        assert actual["rows"][0]["metrics"]["sent"] == 0
        assert actual["rows"][0]["metrics"]["clickedUnique"] is None


def test_discovery_advertises_native_metadata_fields(manifest, config):
    catalog = {stream.name: stream.json_schema for stream in source(manifest, config).discover(LOGGER, config).streams}
    assert catalog["segments"]["properties"]["segmentID"]["type"] == "string"
    assert catalog["automations"]["properties"]["isEnabled"]["type"] == ["null", "boolean"]
    assert catalog["automations"]["properties"]["blocks"]["type"] == ["null", "array"]
    assert catalog["campaigns_v2026"]["properties"]["channel"]["type"] == ["null", "string"]
    assert catalog["forms"]["properties"]["displayType"]["type"] == ["null", "string"]
