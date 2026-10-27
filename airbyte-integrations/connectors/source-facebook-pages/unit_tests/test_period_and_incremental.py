#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import logging
from urllib.parse import parse_qs, urlparse

import pytest
import requests_mock as rm
from source_facebook_pages.source import SourceFacebookPages

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


CONFIG = {"page_id": "1", "access_token": "token"}
ACCESS_TOKEN_URL = "https://graph.facebook.com/1?fields=access_token&access_token=token"
INSIGHTS_URL = "https://graph.facebook.com/v24.0/1/insights"
FEED_URL = "https://graph.facebook.com/v24.0/1/feed"
POST = {"id": "1_1", "created_time": "2024-06-01T00:00:00+0000"}


def _read(stream, sync_mode, config, url, body, state=None):
    catalog = CatalogBuilder().with_stream(stream, sync_mode).build()
    with rm.Mocker() as m:
        m.get(ACCESS_TOKEN_URL, json={"access_token": "access"})
        m.get(url, json=body)
        output = read(SourceFacebookPages(catalog=catalog, config=config, state=state), config, catalog, state=state)
        queries = [parse_qs(urlparse(r.url).query) for r in m.request_history if urlparse(r.url).path == urlparse(url).path]
    assert len(queries) == 1
    return output, queries[0]


def test_page_insights_omits_period_by_default():
    _, query = _read("page_insights", SyncMode.full_refresh, CONFIG, INSIGHTS_URL, {"data": []})
    assert "period" not in query


def test_page_insights_sends_configured_period():
    _, query = _read("page_insights", SyncMode.full_refresh, {**CONFIG, "page_insights_period": "day"}, INSIGHTS_URL, {"data": []})
    assert query["period"] == ["day"]


@pytest.mark.parametrize("sync_mode", [SyncMode.full_refresh, SyncMode.incremental])
def test_post_reads_whole_feed_without_start_date_or_state(sync_mode):
    output, query = _read("post", sync_mode, CONFIG, FEED_URL, {"data": [POST], "paging": {}})
    assert "since" not in query
    assert len(output.records) == 1


def test_post_incremental_uses_start_date():
    config = {**CONFIG, "start_date": "2024-01-01T00:00:00Z"}
    _, query = _read("post", SyncMode.incremental, config, FEED_URL, {"data": [POST], "paging": {}})
    assert query["since"] == ["2024-01-01T00:00:00+0000"]


def test_post_incremental_resumes_from_state_and_advances_cursor():
    state = StateBuilder().with_stream_state("post", {"created_time": "2024-03-01T00:00:00+0000"}).build()
    output, query = _read("post", SyncMode.incremental, CONFIG, FEED_URL, {"data": [POST], "paging": {}}, state=state)
    assert query["since"] == ["2024-03-01T00:00:00+0000"]
    assert output.state_messages[-1].state.stream.stream_state.__dict__ == {"created_time": "2024-06-01T00:00:00+0000"}


def test_check_passes_when_page_has_no_insights_yet():
    # Meta returns an empty data array for Pages under 100 likes; setup must still succeed for them.
    with rm.Mocker() as m:
        m.get(ACCESS_TOKEN_URL, json={"access_token": "access"})
        m.get(INSIGHTS_URL, json={"data": []})
        result = SourceFacebookPages(config=CONFIG).check(logging.getLogger("test"), CONFIG)
    assert result.status.value == "SUCCEEDED", result.message


def test_invalid_metric_is_reported_as_config_error():
    # Meta rejects the whole request when any metric is invalid; the user can always fix the list.
    config = {**CONFIG, "page_insights_metrics": ["page_views_totl"]}
    catalog = CatalogBuilder().with_stream("page_insights", SyncMode.full_refresh).build()
    error = {"error": {"message": "(#100) The value must be a valid insights metric", "type": "OAuthException", "code": 100}}
    with rm.Mocker() as m:
        m.get(ACCESS_TOKEN_URL, json={"access_token": "access"})
        m.get(INSIGHTS_URL, status_code=400, json=error)
        output = read(SourceFacebookPages(catalog=catalog, config=config), config, catalog, expecting_exception=True)
    assert output.errors[0].trace.error.failure_type.value == "config_error"
    assert "Insights Metrics settings" in output.errors[0].trace.error.message


def test_backoff_waits_for_meta_estimated_time_to_regain_access():
    import requests
    from source_facebook_pages.components import MetaUsageBackoffStrategy

    strategy = MetaUsageBackoffStrategy(config=CONFIG, parameters={})
    throttled = requests.Response()
    throttled.headers["X-Business-Use-Case-Usage"] = '{"123": [{"type": "pages", "call_count": 100, "estimated_time_to_regain_access": 2}]}'
    assert strategy.backoff_time(throttled, 1) == 120

    plain = requests.Response()
    assert strategy.backoff_time(plain, 1) is None
    assert strategy.backoff_time(requests.ConnectionError(), 1) is None


def test_comment_stream_reads_post_ids_then_comments_per_post():
    catalog = CatalogBuilder().with_stream("comment", SyncMode.full_refresh).build()
    with rm.Mocker() as m:
        m.get(ACCESS_TOKEN_URL, json={"access_token": "access"})
        m.get(FEED_URL, json={"data": [{"id": "1_10"}, {"id": "1_11"}], "paging": {}})
        m.get("https://graph.facebook.com/v24.0/1_10/comments", json={"data": [{"id": "c1", "message": "hi"}], "paging": {}})
        m.get("https://graph.facebook.com/v24.0/1_11/comments", json={"data": [], "paging": {}})
        output = read(SourceFacebookPages(catalog=catalog, config=CONFIG), CONFIG, catalog)
        feed = [parse_qs(urlparse(r.url).query) for r in m.request_history if urlparse(r.url).path == "/v24.0/1/feed"]
        comments = [parse_qs(urlparse(r.url).query) for r in m.request_history if urlparse(r.url).path.endswith("/comments")]
    assert feed[0]["fields"] == ["id"], "parent read must only ask for post ids"
    assert len(comments) == 2 and comments[0]["filter"] == ["stream"] and "message" in comments[0]["fields"][0]
    assert [r.record.data for r in output.records] == [{"id": "c1", "message": "hi", "post_id": "1_10"}]


def test_rating_stream_requests_recommendation_fields():
    catalog = CatalogBuilder().with_stream("rating", SyncMode.full_refresh).build()
    with rm.Mocker() as m:
        m.get(ACCESS_TOKEN_URL, json={"access_token": "access"})
        m.get("https://graph.facebook.com/v24.0/1/ratings", json={"data": [{"rating": 5, "recommendation_type": "positive"}], "paging": {}})
        output = read(SourceFacebookPages(catalog=catalog, config=CONFIG), CONFIG, catalog)
        query = parse_qs(urlparse(m.request_history[-1].url).query)
    assert "review_text" in query["fields"][0] and "reviewer" in query["fields"][0]
    assert len(output.records) == 1
