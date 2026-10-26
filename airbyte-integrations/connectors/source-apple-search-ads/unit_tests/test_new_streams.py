# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the organization, creatives, negative keyword, product page and search term streams."""

import json
from urllib.parse import parse_qs, urlparse

import pytest
import requests_mock as rm
from _helpers import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover, read


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


def _read(stream_name, sync_mode=SyncMode.full_refresh, config=CONFIG):
    catalog = CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(stream_name).with_sync_mode(sync_mode)).build()
    output = read(get_source(config), config, catalog)
    assert not output.errors, output.errors
    return [r.record.data for r in output.records]


def _api_requests(mocker, method, prefix):
    return [r for r in mocker.request_history if r.method == method and r.url.startswith(API + prefix)]


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
    mocker.get(f"{API}/acls", json={"data": [{"orgId": 1, "orgName": "Org A"}, {"orgId": 2, "orgName": "Org B"}]})
    records = _read("organization")
    assert [r["orgId"] for r in records] == [1, 2]
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

    # Same P1D windows the existing report streams produce for this range; the CDK folds the last day into the final window.
    windows = [("2024-01-01", "2024-01-01"), ("2024-01-02", "2024-01-02"), ("2024-01-03", "2024-01-03"), ("2024-01-04", "2024-01-05")]
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
                    "timeZone": "UTC",
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
