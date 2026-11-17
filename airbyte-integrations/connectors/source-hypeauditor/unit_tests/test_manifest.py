# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Behaviour tests for manifest.yaml against mocked HypeAuditor responses.

Response shapes are the ones the HypeAuditor API v2 returns; the paging
quirks of /report/posts were observed against the live API.
"""

from pathlib import Path

import pytest
import yaml

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


MANIFEST = yaml.safe_load((Path(__file__).parents[1] / "manifest.yaml").read_text())
CONFIG = {"auth_id": "123456", "auth_token": "test-token"}
BASE = "https://hypeauditor.com/api"
CM = f"{BASE}/v2/campaign-management/campaigns"


def _read(stream, expecting_exception=False):
    catalog = CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(stream).with_sync_mode(SyncMode.full_refresh)).build()
    source = ConcurrentDeclarativeSource(source_config=MANIFEST, config=CONFIG, catalog=catalog, state=None)
    return read(source, CONFIG, catalog, expecting_exception=expecting_exception)


def _records(output):
    return [r.record.data for r in output.records]


def _campaigns(ids):
    return {"success": True, "data": [{"id": i, "title": f"t-{i}"} for i in ids], "meta": {"total": len(ids)}}


def _offsets(requests_mock, url):
    return [r.qs.get("offset", ["0"])[0] for r in requests_mock.request_history if r.url.split("?")[0] == url]


def test_campaigns_page_by_offset_until_meta_total(requests_mock):
    ids = [f"c{i:03d}" for i in range(150)]
    requests_mock.get(
        CM,
        [
            {"json": {"data": [{"id": i} for i in ids[:100]], "meta": {"total": 150}}},
            {"json": {"data": [{"id": i} for i in ids[100:]], "meta": {"total": 150}}},
        ],
    )
    output = _read("campaigns")

    assert [r["campaign_id"] for r in _records(output)] == ids
    assert _offsets(requests_mock, CM) == ["0", "100"]
    first = requests_mock.request_history[0]
    assert first.headers["X-Auth-Id"] == "123456"
    assert first.headers["X-Auth-Token"] == "test-token"
    assert first.qs["limit"] == ["100"]


def test_short_page_stops_offset_paging(requests_mock):
    requests_mock.get(CM, json=_campaigns(["c1"]))
    url = f"{CM}/c1/posts"
    requests_mock.get(url, json={"data": [{"basic": {"id": f"p{i}"}} for i in range(17)], "meta": {"total": 18}})
    records = _records(_read("campaign_posts"))

    assert len(records) == 17
    assert _offsets(requests_mock, url) == ["0"]


def test_underscore_id_fallback(requests_mock):
    requests_mock.get(CM, json={"data": [{"_id": "abc"}], "meta": {"total": 1}})
    assert _records(_read("campaigns"))[0]["campaign_id"] == "abc"


@pytest.mark.parametrize("status", [401, 403])
def test_auth_failure_fails_the_sync(requests_mock, status):
    requests_mock.get(CM, status_code=status, json={"error": {"code": 4}})
    output = _read("campaigns", expecting_exception=True)

    assert _records(output) == []
    assert output.errors, "sync must fail, not finish green with zero records"
    errors = [e.trace.error for e in output.errors]
    assert all(e.failure_type == FailureType.config_error for e in errors)
    assert any("rejected the credentials" in e.message for e in errors)


def test_campaign_list_404_fails_the_sync(requests_mock):
    requests_mock.get(CM, status_code=404)
    output = _read("campaigns", expecting_exception=True)
    assert output.errors


def test_auth_failure_on_a_substream_fails_the_sync(requests_mock):
    requests_mock.get(CM, json=_campaigns(["c1", "c2"]))
    requests_mock.get(f"{CM}/c1/influencers", json={"data": [{"id": 1}], "meta": {"total": 1}})
    requests_mock.get(f"{CM}/c2/influencers", status_code=401)
    output = _read("campaign_influencers", expecting_exception=True)
    assert output.errors


def test_402_on_one_campaign_is_skipped(requests_mock):
    requests_mock.get(CM, json=_campaigns(["c1", "c2"]))
    requests_mock.get(f"{CM}/c1/report/audience", status_code=402, json={"error": {"code": 27}})
    requests_mock.get(f"{CM}/c2/report/audience", json={"data": {"metrics": {"reach": 10}}})
    output = _read("campaign_report_audience")

    assert not output.errors
    assert _records(output) == [{"campaign_id": "c2", "metrics": {"reach": 10}}]


def test_rate_limit_is_retried(requests_mock):
    requests_mock.get(
        CM,
        [
            {"status_code": 429, "headers": {"Retry-After": "0"}},
            {"json": _campaigns(["c1"])},
        ],
    )
    output = _read("campaigns")
    assert [r["campaign_id"] for r in _records(output)] == ["c1"]


def test_influencers_get_campaign_and_string_influencer_ids(requests_mock):
    requests_mock.get(CM, json=_campaigns(["c1"]))
    requests_mock.get(
        f"{CM}/c1/influencers",
        json={"data": [{"id": 4242, "accounts": [{"accountId": "a"}]}], "meta": {"total": 1}},
    )
    (record,) = _records(_read("campaign_influencers"))
    assert record["campaign_id"] == "c1"
    assert record["influencer_id"] == "4242"


def test_campaign_posts_key_on_basic_id_and_drop_records_without_it(requests_mock):
    requests_mock.get(CM, json=_campaigns(["c1"]))
    requests_mock.get(
        f"{CM}/c1/posts",
        json={"data": [{"_id": "x", "basic": {"id": "p1"}}, {"_id": "y", "basic": {}}], "meta": {"total": 2}},
    )
    records = _records(_read("campaign_posts"))
    assert [(r["campaign_id"], r["post_id"]) for r in records] == [("c1", "p1")]


def test_recent_posts_single_page_and_drop_records_without_id(requests_mock):
    requests_mock.get(CM, json=_campaigns(["c1"]))
    url = f"{CM}/c1/posts/recent"
    requests_mock.get(url, json={"data": [{"id": "r1", "influencer": {"social_type": 2}}, {"text": "no id"}]})
    records = _records(_read("campaign_posts_recent"))

    assert [(r["campaign_id"], r["post_id"]) for r in records] == [("c1", "r1")]
    assert [r.qs for r in requests_mock.request_history if r.url.startswith(url)] == [{"limit": ["30"]}]


def test_recent_posts_500_skips_that_campaign_without_retrying(requests_mock):
    # Large campaigns answer /posts/recent with a deterministic 500 when the
    # response is slow; retrying only delays the same failure.
    requests_mock.get(CM, json=_campaigns(["c1", "c2"]))
    requests_mock.get(f"{CM}/c1/posts/recent", status_code=500, json={"error": "Internal server error"})
    requests_mock.get(f"{CM}/c2/posts/recent", json={"data": [{"id": "r2"}]})
    output = _read("campaign_posts_recent")

    assert not output.errors
    assert [(r["campaign_id"], r["post_id"]) for r in _records(output)] == [("c2", "r2")]
    assert len([r for r in requests_mock.request_history if r.url.startswith(f"{CM}/c1/posts/recent")]) == 1


def test_500_elsewhere_is_still_retried(requests_mock):
    requests_mock.get(CM, json=_campaigns(["c1"]))
    requests_mock.get(
        f"{CM}/c1/influencers",
        [{"status_code": 500}, {"json": {"data": [{"id": 1}], "meta": {"total": 1}}}],
    )
    assert [r["influencer_id"] for r in _records(_read("campaign_influencers"))] == ["1"]


def test_report_posts_pages_by_position_through_short_pages(requests_mock):
    # As observed live: total 90, offset 0 returns 49 rows (one post
    # undeliverable), offset 50 returns the remaining 40, past the end is empty.
    # Advancing by rows returned (offset 49) would re-read a row; stopping on the
    # short page would lose 40.
    requests_mock.get(CM, json=_campaigns(["c1"]))
    url = f"{CM}/c1/report/posts"
    requests_mock.get(
        url,
        [
            {"json": {"data": [{"id": f"p{i}"} for i in range(49)], "meta": {"total": 90}}},
            {"json": {"data": [{"id": f"p{i}"} for i in range(50, 90)], "meta": {"total": 90}}},
            {"json": {"data": [], "meta": {"total": 90}}},
        ],
    )
    records = _records(_read("campaign_report_posts"))

    assert len(records) == 89
    assert len({r["post_id"] for r in records}) == 89
    assert _offsets(requests_mock, url) == ["0", "50", "100"]
    assert {r.qs["limit"][0] for r in requests_mock.request_history if r.url.startswith(url)} == {"50"}


def test_report_posts_empty_first_page_is_one_request(requests_mock):
    requests_mock.get(CM, json=_campaigns(["c1"]))
    url = f"{CM}/c1/report/posts"
    requests_mock.get(url, json={"data": [], "meta": {"total": 0}})

    assert _records(_read("campaign_report_posts")) == []
    assert _offsets(requests_mock, url) == ["0"]


def test_overview_engagement_uses_renamed_endpoint(requests_mock):
    requests_mock.get(CM, json=_campaigns(["c1"]))
    requests_mock.get(
        f"{CM}/c1/report/overview-engagement",
        json={"data": {"engagementHistory": [{"date": "2026-10-01", "value": 1.5, "valueDelta": 0.1}]}},
    )
    (record,) = _records(_read("campaign_report_overview_engagement"))
    assert record == {"campaign_id": "c1", "date": "2026-10-01", "value": 1.5, "valueDelta": 0.1}


def test_creators_cursor_pagination(requests_mock):
    url = f"{BASE}/method/auditor.creators/"
    requests_mock.get(
        url,
        [
            {"json": {"result": {"creators": [{"id": 1}], "next_cursor": "abc"}}},
            {"json": {"result": {"creators": [{"id": 2}], "next_cursor": None}}},
        ],
    )
    records = _records(_read("creators"))

    assert [r["creator_id"] for r in records] == ["1", "2"]
    cursors = [r.qs.get("cursor") for r in requests_mock.request_history]
    assert cursors == [None, ["abc"]]


def test_report_streams_select_their_nested_lists(requests_mock):
    requests_mock.get(CM, json=_campaigns(["c1"]))
    requests_mock.get(
        f"{CM}/c1/report/engagement",
        json={"data": {"engagements": [{"type": "all", "metrics": {"er": {"value": 0.05}}}, {"type": "ig", "metrics": {}}]}},
    )
    requests_mock.get(
        f"{CM}/c1/report/overview-engagement",
        json={"data": {"engagementHistory": [], "paymentHistory": [{"date": "2026-10-01", "value": 250.0, "postCount": 2}]}},
    )
    requests_mock.get(
        f"{CM}/c1/report/influencers",
        json={"data": {"influencers": [{"id": 77, "firstName": "A", "metrics": {"reach": 5}}]}},
    )

    assert [(r["campaign_id"], r["type"]) for r in _records(_read("campaign_report_engagement"))] == [("c1", "all"), ("c1", "ig")]
    assert _records(_read("campaign_report_overview_payments")) == [
        {"campaign_id": "c1", "date": "2026-10-01", "value": 250.0, "postCount": 2}
    ]
    (influencer,) = _records(_read("campaign_report_influencers"))
    assert (influencer["campaign_id"], influencer["influencer_id"]) == ("c1", "77")


def test_overview_report_returns_one_row_per_platform(requests_mock):
    requests_mock.get(CM, json=_campaigns(["c1"]))
    requests_mock.get(
        f"{CM}/c1/report/overview",
        json={"data": [{"type": "all", "metrics": {"reach": {"value": 10}}}, {"type": "tt", "metrics": {"reach": {"value": 4}}}]},
    )
    records = _records(_read("campaign_report_overview"))
    assert [(r["campaign_id"], r["type"]) for r in records] == [("c1", "all"), ("c1", "tt")]


def test_404_on_one_campaign_report_is_skipped(requests_mock):
    requests_mock.get(CM, json=_campaigns(["c1", "c2"]))
    requests_mock.get(f"{CM}/c1/posts", status_code=404)
    requests_mock.get(f"{CM}/c2/posts", json={"data": [{"basic": {"id": "p1"}}], "meta": {"total": 1}})
    output = _read("campaign_posts")

    assert not output.errors
    assert [(r["campaign_id"], r["post_id"]) for r in _records(output)] == [("c2", "p1")]
