# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Behaviour tests for manifest.yaml against mocked Zernio responses.

Response shapes and error bodies are the ones the Zernio API returned to a live
team account. These tests pin paging, partitioning and error handling.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


MANIFEST = yaml.safe_load((Path(__file__).parents[1] / "manifest.yaml").read_text())
API = "https://zernio.com/api/v1"
CONFIG = {"api_key": "zk-test", "start_date": "2025-03-15"}
ACCOUNTS = [
    {"_id": "fb1", "platform": "facebook", "profileId": {"_id": "p1"}},
    {"_id": "ig1", "platform": "instagram", "profileId": {"_id": "p1"}},
    {"_id": "yt1", "platform": "youtube", "profileId": {"_id": "p1"}},
]


def _read(stream, config=CONFIG, expecting_exception=False, mode=SyncMode.full_refresh):
    catalog = CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(stream).with_sync_mode(mode)).build()
    source = ConcurrentDeclarativeSource(source_config=MANIFEST, config=config, catalog=catalog, state=None)
    return read(source, config, catalog, expecting_exception=expecting_exception)


def _records(output):
    return [r.record.data for r in output.records]


def _sent(requests_mock, path):
    return [r for r in requests_mock.request_history if r.url.split("?")[0] == f"{API}{path}"]


def _mock_accounts(requests_mock, accounts=ACCOUNTS):
    requests_mock.get(f"{API}/accounts", json={"accounts": accounts, "pagination": {"limit": 500, "nextCursor": None}})


def test_accounts_cursor_paging_bearer_auth_and_creator_accounts(requests_mock):
    requests_mock.get(
        f"{API}/accounts",
        [
            {
                "json": {
                    "accounts": [ACCOUNTS[0]],
                    "pagination": {"limit": 500, "nextCursor": "c2"},
                }
            },
            {
                "json": {
                    "accounts": [ACCOUNTS[1]],
                    "pagination": {"limit": 500, "nextCursor": None},
                }
            },
        ],
    )
    output = _read("accounts")

    assert [r["_id"] for r in _records(output)] == ["fb1", "ig1"]
    calls = _sent(requests_mock, "/accounts")
    assert calls[0].headers["Authorization"] == "Bearer zk-test"
    assert calls[0].qs["includecreatoraccounts"] == ["true"] and calls[0].qs["includeoverlimit"] == ["true"]
    assert "cursor" not in calls[0].qs and calls[1].qs["cursor"] == ["c2"]


def test_bad_api_key_fails_the_sync_as_config_error(requests_mock):
    requests_mock.get(
        f"{API}/profiles",
        status_code=401,
        json={
            "error": "Invalid, revoked or expired API key.",
            "type": "authentication_error",
            "code": "invalid_credentials",
        },
    )
    output = _read("profiles", expecting_exception=True)

    assert not _records(output)
    assert output.errors and output.errors[-1].trace.error.failure_type.value == "config_error"


def test_team_wide_400_fails_the_sync(requests_mock):
    requests_mock.get(f"{API}/posts", status_code=400, json={"error": "bad", "code": "invalid_field_value"})
    output = _read("posts", expecting_exception=True)
    assert output.errors


def test_external_posts_per_account_and_bad_account_skipped(requests_mock):
    _mock_accounts(requests_mock)

    def posts(request, context):
        if request.qs["accountid"] == ["yt1"]:
            context.status_code = 401
            return {"error": "token expired", "code": "TOKEN_EXPIRED"}
        return {
            "posts": [{"_id": f"x-{request.qs['accountid'][0]}"}],
            "pagination": {"nextCursor": None},
        }

    requests_mock.get(f"{API}/posts", json=posts)
    output = _read("external_posts")

    assert sorted((r["_id"], r["account_id"]) for r in _records(output)) == [
        ("x-fb1", "fb1"),
        ("x-ig1", "ig1"),
    ]
    assert not output.errors
    assert {c.qs["source"][0] for c in _sent(requests_mock, "/posts")} == {"external"}


def test_post_analytics_year_windows_paging_and_account_id(requests_mock):
    _mock_accounts(requests_mock, [ACCOUNTS[0]])

    def analytics(request, context):
        page = request.qs.get("page", ["1"])  # the first page sends no page param
        if page == ["1"] and request.qs["fromdate"] == ["2025-03-15"]:
            return {"posts": [{"_id": f"p{i}"} for i in range(100)]}
        if page == ["2"] and request.qs["fromdate"] == ["2025-03-15"]:
            return {"posts": [{"_id": "p100"}]}
        return {"posts": []}

    requests_mock.get(f"{API}/analytics", json=analytics)
    output = _read("post_analytics")

    assert len(_records(output)) == 101 and {r["account_id"] for r in _records(output)} == {"fb1"}
    windows = sorted({(c.qs["fromdate"][0], c.qs["todate"][0]) for c in _sent(requests_mock, "/analytics")})
    this_year = datetime.now(timezone.utc).year
    assert windows[0] == ("2025-03-15", "2025-12-31")
    assert len(windows) == this_year - 2025 + 1
    assert windows[-1][1] == datetime.now(timezone.utc).strftime("%Y-%m-%d")


def test_follower_stats_flattens_the_per_account_map(requests_mock):
    _mock_accounts(requests_mock, [ACCOUNTS[1]])
    requests_mock.get(
        f"{API}/accounts/follower-stats",
        json={
            "stats": {
                "ig1": [
                    {"date": "2026-11-01", "followers": 5},
                    {"date": "2026-11-02", "followers": 6},
                ]
            }
        },
    )
    output = _read("follower_stats")

    assert {(r["account_id"], r["date"], r["followers"]) for r in _records(output)} == {
        ("ig1", "2026-11-01", 5),
        ("ig1", "2026-11-02", 6),
    }
    assert {c.qs["accountids"][0] for c in _sent(requests_mock, "/accounts/follower-stats")} == {"ig1"}


def test_insights_only_ask_the_matching_platform(requests_mock):
    _mock_accounts(requests_mock)
    requests_mock.get(f"{API}/analytics/facebook/page-insights", json={"accountId": "fb1", "metrics": {"page_follows": {"total": 1}}})
    output = _read("facebook_page_insights")

    assert [r["account_id"] for r in _records(output)] == ["fb1"]
    calls = _sent(requests_mock, "/analytics/facebook/page-insights")
    assert [c.qs["accountid"][0] for c in calls] == ["fb1"]
    assert calls[0].qs["metrictype"] == ["time_series"] and "page_media_view" in calls[0].qs["metrics"][0]


def test_youtube_quota_429_is_skipped_without_retrying(requests_mock):
    _mock_accounts(requests_mock)
    requests_mock.get(
        f"{API}/analytics/youtube/channel-insights",
        status_code=429,
        json={
            "error": "YouTube Analytics daily quota exhausted.",
            "code": "rate_limited",
            "platform": "google",
            "details": {"quotaExhausted": True, "quotaScope": "DEVELOPER"},
        },
    )
    output = _read("youtube_channel_insights")

    assert not _records(output) and not output.errors
    assert len(_sent(requests_mock, "/analytics/youtube/channel-insights")) == 1


def test_demographics_path_per_platform_and_too_few_followers_skipped(requests_mock):
    _mock_accounts(requests_mock, ACCOUNTS[:2])
    requests_mock.get(f"{API}/analytics/facebook/demographics", json={"accountId": "fb1", "demographics": {"country": []}})
    requests_mock.get(
        f"{API}/analytics/instagram/demographics",
        status_code=400,
        json={
            "success": False,
            "error": "Demographic insights require at least 100 followers.",
        },
    )
    output = _read("audience_demographics")

    assert [r["account_id"] for r in _records(output)] == ["fb1"] and not output.errors


def test_comments_only_for_posts_with_comments(requests_mock):
    _mock_accounts(requests_mock, [ACCOUNTS[1]])
    requests_mock.get(
        f"{API}/inbox/comments",
        json={
            "data": [
                {
                    "id": "m1",
                    "accountId": "ig1",
                    "platform": "instagram",
                    "commentCount": 2,
                },
                {
                    "id": "m2",
                    "accountId": "ig1",
                    "platform": "instagram",
                    "commentCount": 0,
                },
            ],
            "pagination": {"hasMore": False},
        },
    )
    requests_mock.get(
        f"{API}/inbox/comments/m1",
        [
            {
                "json": {
                    "comments": [{"id": "c1"}],
                    "pagination": {"hasMore": True, "cursor": "k2"},
                }
            },
            {"json": {"comments": [{"id": "c2"}], "pagination": {"hasMore": False}}},
        ],
    )
    output = _read("comments")

    assert [(r["id"], r["post_id"], r["account_id"]) for r in _records(output)] == [
        ("c1", "m1", "ig1"),
        ("c2", "m1", "ig1"),
    ]
    calls = _sent(requests_mock, "/inbox/comments/m1")
    assert calls[0].qs["accountid"] == ["ig1"] and calls[1].qs["cursor"] == ["k2"]
    assert not _sent(requests_mock, "/inbox/comments/m2")


def test_daily_metrics_both_attributions(requests_mock):
    _mock_accounts(requests_mock, [ACCOUNTS[0]])
    requests_mock.get(
        f"{API}/analytics/daily-metrics",
        json=lambda req, ctx: {"dailyData": [{"date": "2026-11-01", "postCount": 1, "metrics": {"reach": 3}}]},
    )
    output = _read("daily_metrics")

    assert sorted(r["attribution"] for r in _records(output)) == ["publish", "received"]
    assert {c.qs["fromdate"][0] for c in _sent(requests_mock, "/analytics/daily-metrics")} == {"2025-03-15"}


def test_logs_incremental_types_and_skip_paging(requests_mock):
    def logs(request, context):
        if request.qs["type"] == ["publishing"] and "skip" not in request.qs:
            return {"logs": [{"type": "publishing", "created_at": "2026-11-01 10:00:00"}] * 100}
        if request.qs["type"] == ["publishing"]:
            return {"logs": [{"type": "publishing", "created_at": "2026-11-02 10:00:00"}]}
        return {"logs": []}

    requests_mock.get(f"{API}/logs", json=logs)
    output = _read("logs", mode=SyncMode.incremental)

    assert len(_records(output)) == 101
    calls = _sent(requests_mock, "/logs")
    assert {c.qs["type"][0] for c in calls} == {
        "publishing",
        "connections",
        "token_refresh",
        "workflow_event",
        "comment_automation",
    }
    assert all(c.qs["from"][0].endswith("z") for c in calls)
    assert output.state_messages


def test_creator_campaign_children_follow_the_campaigns(requests_mock):
    requests_mock.get(f"{API}/creator-campaigns", json={"campaigns": [{"id": "cc1"}], "total": 1})
    requests_mock.get(f"{API}/creator-campaigns/cc1/submissions", json={"submissions": [{"id": "s1", "viewsLatest": 10}], "total": 1})
    output = _read("creator_campaign_submissions")
    assert [r["id"] for r in _records(output)] == ["s1"]


def test_instagram_daily_totals_reads_single_days_two_to_four_days_ago(requests_mock):
    _mock_accounts(requests_mock)
    requests_mock.get(
        f"{API}/analytics/instagram/account-insights",
        json=lambda req, ctx: {
            "accountId": "ig1",
            "metricType": "total_value",
            "metrics": {"reach": {"total": 4}},
        },
    )
    output = _read("instagram_daily_totals")

    calls = _sent(requests_mock, "/analytics/instagram/account-insights")
    assert {c.qs["accountid"][0] for c in calls} == {"ig1"}
    assert all(c.qs["fromdate"] == c.qs["todate"] and c.qs["metrictype"] == ["total_value"] for c in calls)
    today = datetime.now(timezone.utc).date()
    expected = {(today - timedelta(days=d)).isoformat() for d in (2, 3, 4)}
    assert {r["day"] for r in _records(output)} == expected
    assert {r["account_id"] for r in _records(output)} == {"ig1"}


def test_creator_campaigns_skip_paging(requests_mock):
    requests_mock.get(
        f"{API}/creator-campaigns",
        [
            {
                "json": {
                    "campaigns": [{"id": f"cc{i}"} for i in range(100)],
                    "total": 101,
                }
            },
            {"json": {"campaigns": [{"id": "cc100"}], "total": 101}},
        ],
    )
    output = _read("creator_campaigns")

    assert len(_records(output)) == 101
    calls = _sent(requests_mock, "/creator-campaigns")
    assert calls[0].qs["limit"] == ["100"] and "skip" not in calls[0].qs and calls[1].qs["skip"] == ["100"]
