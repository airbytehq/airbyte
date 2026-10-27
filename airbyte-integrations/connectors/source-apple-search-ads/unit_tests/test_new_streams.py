# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the organization, creatives, negative keyword, product page and search term streams."""

import json
from urllib.parse import parse_qs, urlparse

import pytest
import requests_mock as rm
from _helpers import get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover, read
from airbyte_cdk.test.state_builder import StateBuilder


API = "https://api.searchads.apple.com/api/v5"
TOKEN_URL = "https://appleid.apple.com/auth/oauth2/token"

CONFIG = {
    "org_id": 12345,
    "client_id": "client-id",
    "client_secret": "client-secret",
    "start_date": "2024-01-01",
    "end_date": "2024-01-02",
    "timezone": "UTC",
    "lookback_window": 1,
    "backoff_factor": 1,
    "num_workers": 1,
    "token_refresh_endpoint": "https://appleid.apple.com/auth/oauth2/token?grant_type=client_credentials&scope=searchadsorg",
}

CAMPAIGNS = [
    {"id": 1, "adamId": 100, "supplySources": ["APPSTORE_SEARCH_RESULTS"]},
    {"id": 2, "adamId": 100, "supplySources": ["APPSTORE_TODAY_TAB"]},
    {"id": 3, "adamId": 200},
]

FULL_PAGE = [{"id": i} for i in range(1000)]
EMPTY_REPORT = {"data": {"reportingDataResponse": {"row": []}}}

NEW_STREAMS = {
    "organization": (["orgId"], False),
    "creatives": (["id"], False),
    "campaign_negative_keywords": (["id"], False),
    "adgroup_negative_keywords": (["id"], False),
    "product_pages": (["id"], False),
    "search_terms_report_daily": (None, True),
}


@pytest.fixture
def mocker():
    with rm.Mocker() as m:
        m.post(TOKEN_URL, json={"access_token": "token", "expires_in": 3600, "token_type": "Bearer"})
        m.get(f"{API}/campaigns", json={"data": CAMPAIGNS})
        yield m


@pytest.fixture(autouse=True)
def frozen_clock():
    # The fixtures use January 2024 dates, and search term windows start at most 89 days back.
    with freeze_time("2024-01-06T12:00:00Z"):
        yield


def _read(stream_name, sync_mode=SyncMode.full_refresh, config=CONFIG):
    catalog = CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(stream_name).with_sync_mode(sync_mode)).build()
    output = read(get_source(config), config, catalog)
    assert not output.errors, output.errors
    return [r.record.data for r in output.records]


def _api_requests(mocker, method, prefix):
    return [r for r in mocker.request_history if r.method == method and r.url.startswith(API + prefix)]


def _requested_days(mocker):
    requests = _api_requests(mocker, "POST", "/reports/campaigns/")
    assert all(r.json()["startTime"] == r.json()["endTime"] for r in requests)
    return sorted((int(urlparse(r.url).path.split("/")[-2]), r.json()["startTime"]) for r in requests)


def test_discover_exposes_new_streams():
    output = discover(get_source(CONFIG), CONFIG)
    streams = {s.name: s for s in output.catalog.catalog.streams}
    for name, (primary_key, incremental) in NEW_STREAMS.items():
        assert name in streams
        stream = streams[name]
        if primary_key:
            assert stream.source_defined_primary_key == [[k] for k in primary_key]
        else:
            assert not stream.source_defined_primary_key
        assert (SyncMode.incremental in stream.supported_sync_modes) is incremental
        if incremental:
            assert stream.default_cursor_field == ["date"]


def test_organization_reads_user_acls(mocker):
    # Get User ACL lists every organization the API user can access; only the configured one is synced.
    mocker.get(f"{API}/acls", json={"data": [{"orgId": 12345, "orgName": "Org A"}, {"orgId": 2, "orgName": "Another client"}]})
    records = _read("organization")
    assert [r["orgId"] for r in records] == [12345]
    assert len(_api_requests(mocker, "GET", "/acls")) == 1


def test_creatives_paginates_with_offset_and_org_context(mocker):
    first_page = [{"id": i} for i in range(1000)]
    mocker.get(
        f"{API}/creatives",
        [{"json": {"data": first_page}}, {"json": {"data": [{"id": 1000}]}}],
    )
    records = _read("creatives")
    assert len(records) == 1001
    requests = _api_requests(mocker, "GET", "/creatives")
    assert [parse_qs(urlparse(r.url).query) for r in requests] == [
        {"limit": ["1000"]},
        {"limit": ["1000"], "offset": ["1000"]},
    ]
    assert all(r.headers["X-AP-Context"] == "orgId=12345" for r in requests)


def test_campaign_negative_keywords_requests_every_campaign(mocker):
    for campaign in CAMPAIGNS:
        mocker.get(
            f"{API}/campaigns/{campaign['id']}/negativekeywords",
            json={"data": [{"id": campaign["id"] * 10, "campaignId": campaign["id"], "text": "free"}]},
        )
    records = _read("campaign_negative_keywords")
    assert sorted(r["id"] for r in records) == [10, 20, 30]
    paths = sorted(urlparse(r.url).path for r in _api_requests(mocker, "GET", "/campaigns/"))
    assert paths == [f"/api/v5/campaigns/{i}/negativekeywords" for i in (1, 2, 3)]


def test_adgroup_negative_keywords_uses_parent_campaign_and_adgroup_ids(mocker):
    mocker.get(f"{API}/campaigns/1/adgroups", json={"data": [{"id": 11, "campaignId": 1}, {"id": 12, "campaignId": 1}]})
    mocker.get(f"{API}/campaigns/2/adgroups", json={"data": [{"id": 21, "campaignId": 2}]})
    mocker.get(f"{API}/campaigns/3/adgroups", json={"data": []})
    for campaign_id, adgroup_id in ((1, 11), (1, 12), (2, 21)):
        mocker.get(
            f"{API}/campaigns/{campaign_id}/adgroups/{adgroup_id}/negativekeywords",
            json={"data": [{"id": adgroup_id * 10, "campaignId": campaign_id, "adGroupId": adgroup_id}]},
        )
    records = _read("adgroup_negative_keywords")
    assert sorted(r["id"] for r in records) == [110, 120, 210]
    paths = sorted(
        urlparse(r.url).path for r in mocker.request_history if r.url.endswith("negativekeywords") or "negativekeywords?" in r.url
    )
    assert paths == [
        "/api/v5/campaigns/1/adgroups/11/negativekeywords",
        "/api/v5/campaigns/1/adgroups/12/negativekeywords",
        "/api/v5/campaigns/2/adgroups/21/negativekeywords",
    ]


def test_product_pages_deduplicates_apps_across_campaigns(mocker):
    mocker.get(f"{API}/apps/100/product-pages", json={"data": [{"id": "pp-1", "adamId": 100}]})
    mocker.get(f"{API}/apps/200/product-pages", json={"data": [{"id": "pp-2", "adamId": 200}]})
    records = _read("product_pages")
    assert sorted(r["id"] for r in records) == ["pp-1", "pp-2"]
    paths = sorted(urlparse(r.url).path for r in _api_requests(mocker, "GET", "/apps/"))
    assert paths == ["/api/v5/apps/100/product-pages", "/api/v5/apps/200/product-pages"]


def test_search_terms_report_daily_requests_each_search_campaign_and_day(mocker):
    def report(request, context):
        body = request.json()
        return {
            "data": {
                "reportingDataResponse": {
                    "row": [
                        {
                            "metadata": {
                                "adGroupId": 7,
                                "keywordId": 8,
                                "searchTermText": f"term {body['startTime']}",
                                "countryOrRegion": "US",
                            },
                            "granularity": [{"date": body["startTime"], "impressions": 5}],
                        }
                    ]
                }
            }
        }

    mocker.post(f"{API}/reports/campaigns/1/searchterms", json=report)
    mocker.post(f"{API}/reports/campaigns/3/searchterms", json=report)

    # One day per request, and the configured End Date is the last day requested.
    windows = [(f"2024-01-0{day}", f"2024-01-0{day}") for day in range(1, 6)]
    records = _read("search_terms_report_daily", SyncMode.incremental, dict(CONFIG, end_date="2024-01-05"))

    requests = _api_requests(mocker, "POST", "/reports/campaigns/")
    observed = sorted((urlparse(r.url).path, json.dumps(r.json(), sort_keys=True)) for r in requests)
    expected = sorted(
        (
            f"/api/v5/reports/campaigns/{campaign_id}/searchterms",
            json.dumps(
                {
                    "startTime": start,
                    "endTime": end,
                    # Apple: "Search term-level reports only support a timeZone value of ORTZ."
                    "timeZone": "ORTZ",
                    "granularity": "DAILY",
                    "groupBy": ["countryOrRegion"],
                    "returnRowTotals": False,
                    "returnGrandTotals": False,
                    "selector": {
                        "orderBy": [{"field": "impressions", "sortOrder": "DESCENDING"}],
                        "pagination": {"limit": 1000},
                    },
                },
                sort_keys=True,
            ),
        )
        for campaign_id in (1, 3)
        for start, end in windows
    )
    assert observed == expected
    assert all(r.headers["X-AP-Context"] == "orgId=12345" for r in requests)

    assert sorted((r["campaignId"], r["date"]) for r in records) == [(c, start) for c in (1, 3) for start, _ in windows]
    for record in records:
        assert record["adGroupId"] == 7
        assert record["keywordId"] == 8
        assert record["searchTermText"] == f"term {record['date']}"
        assert record["countryorregion"] == "US"


@pytest.mark.parametrize(
    "stream_name, path, pages, expected_queries",
    [
        pytest.param(
            "campaign_negative_keywords",
            "/campaigns/1/negativekeywords",
            [FULL_PAGE, [{"id": 1000}]],
            [{"limit": ["1000"]}, {"limit": ["1000"], "offset": ["1000"]}],
            id="campaign_negative_keywords",
        ),
        pytest.param(
            "adgroup_negative_keywords",
            "/campaigns/1/adgroups/11/negativekeywords",
            [FULL_PAGE, [{"id": 1000}]],
            [{"limit": ["1000"]}, {"limit": ["1000"], "offset": ["1000"]}],
            id="adgroup_negative_keywords",
        ),
        # Apple documents no limit or offset for Get Product Pages.
        pytest.param("product_pages", "/apps/100/product-pages", [[{"id": "pp-1"}]], [{}], id="product_pages"),
    ],
)
def test_child_streams_send_org_context_and_paginate(mocker, stream_name, path, pages, expected_queries):
    mocker.get(f"{API}/campaigns", json={"data": [CAMPAIGNS[0]]})
    mocker.get(f"{API}/campaigns/1/adgroups", json={"data": [{"id": 11, "campaignId": 1}]})
    mocker.get(f"{API}{path}", [{"json": {"data": page}} for page in pages])

    records = _read(stream_name)

    requests = [r for r in mocker.request_history if urlparse(r.url).path == f"/api/v5{path}"]
    assert len(records) == sum(len(page) for page in pages)
    assert [parse_qs(urlparse(r.url).query) for r in requests] == expected_queries
    assert all(r.headers["X-AP-Context"] == "orgId=12345" for r in requests)


def _search_term_rows(count):
    return [
        {"metadata": {"adGroupId": 7, "keywordId": 8, "searchTermText": f"term {i}", "countryOrRegion": "US"}, "granularity": []}
        for i in range(count)
    ]


def test_search_terms_report_daily_paginates_in_selector(mocker):
    mocker.post(
        f"{API}/reports/campaigns/1/searchterms",
        [{"json": {"data": {"reportingDataResponse": {"row": rows}}}} for rows in (_search_term_rows(1000), _search_term_rows(1))],
    )
    mocker.post(f"{API}/reports/campaigns/3/searchterms", json=EMPTY_REPORT)

    records = _read("search_terms_report_daily", SyncMode.incremental, dict(CONFIG, end_date="2024-01-01"))

    assert len(records) == 1001
    pages = [r.json()["selector"]["pagination"] for r in _api_requests(mocker, "POST", "/reports/campaigns/1/")]
    assert pages == [{"limit": 1000}, {"limit": 1000, "offset": 1000}]


def test_search_terms_report_daily_keeps_low_volume_rollup_row(mocker):
    # Apple: `other` rows hold search terms under 10 impressions, with the dimensions set to null.
    rollup = {
        "other": True,
        "metadata": {"adGroupId": 7, "keywordId": 8, "searchTermText": None, "countryOrRegion": "US", "searchTermSource": "TARGETED"},
        "granularity": [{"date": "2024-01-01", "impressions": 3}],
    }
    mocker.post(f"{API}/reports/campaigns/1/searchterms", json={"data": {"reportingDataResponse": {"row": [rollup]}}})
    mocker.post(f"{API}/reports/campaigns/3/searchterms", json=EMPTY_REPORT)

    records = _read("search_terms_report_daily", SyncMode.incremental, dict(CONFIG, end_date="2024-01-01"))

    # The AddFields condition skips null terms, so the top-level key is absent and the destination sees null.
    assert [(r["campaignId"], r.get("searchTermText"), r["other"]) for r in records] == [(1, None, True)]


def _read_with_state(stream_state, config):
    catalog = (
        CatalogBuilder()
        .with_stream(ConfiguredAirbyteStreamBuilder().with_name("search_terms_report_daily").with_sync_mode(SyncMode.incremental))
        .build()
    )
    state = StateBuilder().with_stream_state("search_terms_report_daily", stream_state).build()
    output = read(get_source(config, catalog=catalog, state=state), config, catalog, state)
    assert not output.errors, output.errors
    return output


@pytest.mark.parametrize(
    "stream_state",
    [
        pytest.param({"date": "2024-01-04"}, id="legacy_flat_state"),
        pytest.param({"state": {"date": "2024-01-04"}, "use_global_cursor": True}, id="global_state"),
    ],
)
def test_search_terms_report_daily_resumes_from_state_minus_lookback(mocker, stream_state):
    for campaign_id in (1, 3):
        mocker.post(f"{API}/reports/campaigns/{campaign_id}/searchterms", json=EMPTY_REPORT)

    output = _read_with_state(stream_state, dict(CONFIG, end_date="2024-01-05"))

    assert _requested_days(mocker) == [(campaign_id, day) for campaign_id in (1, 3) for day in ("2024-01-03", "2024-01-04", "2024-01-05")]
    # global_substream_cursor keeps one cursor for all campaigns instead of per-partition states.
    assert "states" not in output.most_recent_state.stream_state.__dict__


def test_search_terms_report_daily_without_end_date_requests_today_and_keeps_record_date_state(mocker):
    def report(request, context):
        row = {"metadata": {"adGroupId": 7, "keywordId": 8, "searchTermText": "term", "countryOrRegion": "US"}}
        return {
            "data": {"reportingDataResponse": {"row": [dict(row, granularity=[{"date": request.json()["startTime"], "impressions": 5}])]}}
        }

    for campaign_id in (1, 3):
        mocker.post(f"{API}/reports/campaigns/{campaign_id}/searchterms", json=report)
    config = {key: value for key, value in CONFIG.items() if key != "end_date"}

    output = _read_with_state({}, dict(config, start_date="2024-01-05"))

    # Today (2024-01-06 on the frozen clock) is requested once per campaign, and tomorrow never.
    assert _requested_days(mocker) == [(campaign_id, day) for campaign_id in (1, 3) for day in ("2024-01-05", "2024-01-06")]
    # The cursor ends one day after today, but the state keeps the newest record date.
    assert output.most_recent_state.stream_state.state == {"date": "2024-01-06"}


@pytest.mark.parametrize(
    "dates",
    [
        pytest.param({"start_date": "2024-01-04", "end_date": "2024-01-03"}, id="start_after_end_date"),
        pytest.param({"start_date": "2024-01-07", "end_date": None}, id="start_tomorrow_without_end_date"),
    ],
)
def test_search_terms_report_daily_sends_nothing_past_the_last_day(mocker, dates):
    for campaign_id in (1, 3):
        mocker.post(f"{API}/reports/campaigns/{campaign_id}/searchterms", json=EMPTY_REPORT)
    config = {key: value for key, value in dict(CONFIG, **dates).items() if value is not None}

    _read_with_state({}, config)

    assert _api_requests(mocker, "POST", "/reports/campaigns/") == []


def test_search_terms_report_daily_future_state_sends_no_report_requests(mocker):
    # Same shape as integration_tests/abnormal_state.json.
    _read_with_state({"date": "2999-11-06"}, dict(CONFIG, end_date="2024-01-05"))

    assert _api_requests(mocker, "POST", "/reports/campaigns/") == []


def test_search_terms_report_daily_starts_within_apples_daily_window(mocker):
    mocker.post(f"{API}/reports/campaigns/1/searchterms", json={"data": {"reportingDataResponse": {"row": []}}})
    mocker.post(f"{API}/reports/campaigns/3/searchterms", json={"data": {"reportingDataResponse": {"row": []}}})

    with freeze_time("2026-10-26T10:00:00Z"):
        _read("search_terms_report_daily", SyncMode.incremental, dict(CONFIG, start_date="2020-01-01", end_date="2026-07-30"))

    starts = sorted({r.json()["startTime"] for r in _api_requests(mocker, "POST", "/reports/campaigns/")})
    # Apple serves DAILY reports only when startTime is at most 90 days in the past.
    assert starts[0] == "2026-07-29"


def test_search_terms_report_daily_keeps_numeric_search_terms_as_text(mocker):
    terms = ["2048", '"vpn"', "'a' 'b'", "True"]
    rows = [
        {"metadata": {"adGroupId": 7, "keywordId": 8, "searchTermText": term, "countryOrRegion": "US"}, "granularity": []} for term in terms
    ]
    mocker.post(f"{API}/reports/campaigns/1/searchterms", json={"data": {"reportingDataResponse": {"row": rows}}})
    mocker.post(f"{API}/reports/campaigns/3/searchterms", json={"data": {"reportingDataResponse": {"row": []}}})

    records = _read("search_terms_report_daily", SyncMode.incremental, dict(CONFIG, end_date="2024-01-01"))

    assert [record["searchTermText"] for record in records] == terms


def test_search_terms_report_daily_400_is_a_system_error(mocker):
    mocker.post(
        f"{API}/reports/campaigns/1/searchterms",
        status_code=400,
        json={"data": None, "error": {"errors": [{"messageCode": "INVALID_INPUT", "message": "some other problem", "field": ""}]}},
    )
    mocker.post(f"{API}/reports/campaigns/3/searchterms", json={"data": {"reportingDataResponse": {"row": []}}})
    catalog = (
        CatalogBuilder()
        .with_stream(ConfiguredAirbyteStreamBuilder().with_name("search_terms_report_daily").with_sync_mode(SyncMode.incremental))
        .build()
    )
    config = dict(CONFIG, end_date="2024-01-01")

    output = read(get_source(config), config, catalog, expecting_exception=True)

    error = output.errors[0].trace.error
    assert error.failure_type.value == "system_error"
    assert "Start Date" not in error.message
    assert "some other problem" in error.message


@pytest.mark.parametrize(
    "stream_name, field_path, expected",
    [
        ("creatives", ("creationTime",), {"format": "date-time", "airbyte_type": "timestamp_without_timezone"}),
        ("creatives", ("modificationTime",), {"format": "date-time", "airbyte_type": "timestamp_without_timezone"}),
        ("campaign_negative_keywords", ("modificationTime",), {"format": "date-time", "airbyte_type": "timestamp_without_timezone"}),
        ("adgroup_negative_keywords", ("creationTime",), {"format": "date-time", "airbyte_type": "timestamp_without_timezone"}),
        ("product_pages", ("modificationTime",), {"format": "date-time", "airbyte_type": "timestamp_without_timezone"}),
        ("search_terms_report_daily", ("date",), {"format": "date"}),
        ("search_terms_report_daily", ("granularity", "items", "date"), {"format": "date"}),
        (
            "search_terms_report_daily",
            ("metadata", "modificationTime"),
            {"format": "date-time", "airbyte_type": "timestamp_without_timezone"},
        ),
    ],
)
def test_new_streams_type_their_dates(stream_name, field_path, expected):
    # Typed from the start: retyping a released stream later would be a breaking change.
    streams = {stream.name: stream for stream in discover(get_source(CONFIG), CONFIG).catalog.catalog.streams}
    node = streams[stream_name].json_schema
    for key in field_path:
        node = node["items"] if key == "items" else node["properties"][key]
    assert {key: node.get(key) for key in expected} == expected
