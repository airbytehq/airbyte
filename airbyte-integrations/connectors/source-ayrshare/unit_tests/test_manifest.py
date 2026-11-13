"""Behaviour tests for manifest.yaml against mocked Ayrshare responses.

Response shapes and error codes are the ones the Ayrshare API returned to a
Business-plan account. The profile streams need real Profile Keys to read
live, so these tests are what pins their behaviour.
"""
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

import yaml
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import read

MANIFEST = yaml.safe_load((Path(__file__).parents[1] / "manifest.yaml").read_text())
API = "https://api.ayrshare.com/api"
KEYED = {"api_key": "primary-key", "profile_keys": "pk-a, pk-b", "platforms": ["facebook", "instagram"]}


def _read(stream, config, expecting_exception=False):
    catalog = (
        CatalogBuilder()
        .with_stream(ConfiguredAirbyteStreamBuilder().with_name(stream).with_sync_mode(SyncMode.full_refresh))
        .build()
    )
    source = ConcurrentDeclarativeSource(source_config=MANIFEST, config=config, catalog=catalog, state=None)
    return read(source, config, catalog, expecting_exception=expecting_exception)


def _records(output):
    return [r.record.data for r in output.records]


def _mock_users(requests_mock):
    """GET /user answers per Profile-Key: pk-a -> ref-a, pk-b -> ref-b."""

    def user(request, context):
        key = request.headers.get("Profile-Key")
        return {"refId": {"pk-a": "ref-a", "pk-b": "ref-b"}[key], "activeSocialAccounts": ["facebook"]}

    requests_mock.get(f"{API}/user", json=user)


def _sent(requests_mock, path):
    return [r for r in requests_mock.request_history if r.url.split("?")[0] == f"{API}{path}"]


def test_profiles_cursor_paging_and_bearer_auth(requests_mock):
    requests_mock.get(
        f"{API}/profiles",
        [
            {"json": {"profiles": [{"refId": "r1"}], "hasMore": True, "nextCursor": "c2"}},
            {"json": {"profiles": [{"refId": "r2"}], "hasMore": False}},
        ],
    )
    output = _read("profiles", {"api_key": "primary-key"})

    assert [r["refId"] for r in _records(output)] == ["r1", "r2"]
    calls = _sent(requests_mock, "/profiles")
    assert calls[0].headers["Authorization"] == "Bearer primary-key"
    assert "Profile-Key" not in calls[0].headers
    assert calls[0].qs.get("cursor") is None and calls[1].qs["cursor"] == ["c2"]


def test_bad_api_key_fails_the_sync(requests_mock):
    requests_mock.get(f"{API}/profiles", status_code=401, json={"code": 102, "status": "error"})
    output = _read("profiles", {"api_key": "wrong"}, expecting_exception=True)

    assert not _records(output)
    assert output.errors and output.errors[-1].trace.error.failure_type.value == "config_error"


def test_profile_streams_emit_nothing_without_profile_keys(requests_mock):
    for stream in ["post_history", "platform_posts", "social_analytics", "post_analytics", "comments", "platform_comments"]:
        output = _read(stream, {"api_key": "primary-key"})
        assert not _records(output) and not output.errors, stream
    assert not requests_mock.request_history


def test_post_history_per_profile_key_and_no_history_skipped(requests_mock):
    _mock_users(requests_mock)

    def history(request, context):
        if request.headers["Profile-Key"] == "pk-b":
            context.status_code = 400
            return {"history": {"code": 221, "status": "error"}, "code": 221}
        return {"history": [{"id": "post1", "status": "success", "postIds": [{"id": "fb1", "platform": "facebook"}]}]}

    requests_mock.get(f"{API}/history", json=history)
    output = _read("post_history", KEYED)

    assert _records(output) == [
        {"id": "post1", "status": "success", "postIds": [{"id": "fb1", "platform": "facebook"}], "ref_id": "ref-a"}
    ]
    assert not output.errors
    calls = _sent(requests_mock, "/history")
    assert sorted(c.headers["Profile-Key"] for c in calls) == ["pk-a", "pk-b"]
    assert calls[0].qs["lastdays"] == ["0"] and calls[0].qs["limit"] == ["1000"]


def test_no_history_code_221_is_the_real_body_shape(requests_mock):
    """no posts -> HTTP 400, code nested under `history`."""
    _mock_users(requests_mock)
    requests_mock.get(
        f"{API}/history",
        status_code=400,
        json={"history": {"code": 221, "action": "get", "status": "error"}, "refId": "x", "count": 0},
    )
    output = _read("post_history", KEYED)
    assert not _records(output) and not output.errors


def test_platform_posts_fan_out_paging_and_unlinked_skip(requests_mock):
    _mock_users(requests_mock)

    def facebook(request, context):
        # Profiles are read concurrently, so answer by key and cursor, not call order.
        if request.headers["Profile-Key"] == "pk-b":
            return {"posts": [], "meta": {"pagination": {"hasMore": False}}}
        if request.qs.get("next") == ["n2"]:
            return {"posts": [{"id": "f2"}], "meta": {"pagination": {"hasMore": False}}}
        return {"posts": [{"id": "f1", "post": "hi", "pageId": "p"}], "meta": {"pagination": {"hasMore": True, "next": "n2"}}}

    requests_mock.get(f"{API}/history/facebook", json=facebook)
    requests_mock.get(f"{API}/history/instagram", status_code=400, json={"code": 156, "status": "error"})
    output = _read("platform_posts", KEYED)

    recs = sorted(_records(output), key=lambda r: r["id"])
    assert [(r["ref_id"], r["platform"], r["id"]) for r in recs] == [("ref-a", "facebook", "f1"), ("ref-a", "facebook", "f2")]
    assert recs[0]["raw"] == {"id": "f1", "post": "hi", "pageId": "p"}
    assert not output.errors
    fb_a = [c for c in _sent(requests_mock, "/history/facebook") if c.headers["Profile-Key"] == "pk-a"]
    assert [c.qs.get("next") for c in fb_a] == [None, ["n2"]]
    assert len(_sent(requests_mock, "/history/instagram")) == 2


def test_platform_posts_missing_social_account_103_skipped(requests_mock):
    """/history/{platform} on an unlinked network -> 400 code 103, not 156."""
    _mock_users(requests_mock)
    requests_mock.get(f"{API}/history/facebook", json={"posts": [{"id": "f1"}], "meta": {"pagination": {"hasMore": False}}})
    requests_mock.get(
        f"{API}/history/instagram",
        status_code=400,
        json={"code": 103, "action": "get", "status": "error", "message": "Missing social account."},
    )
    output = _read("platform_posts", KEYED)
    assert len(_records(output)) == 2 and not output.errors


def test_platform_posts_broken_cursor_ends_that_partition_only(requests_mock):
    """a `next` cursor answered 404 code 1. Keep page 1, skip the rest, don't fail."""
    _mock_users(requests_mock)
    broken = {"code": 1, "action": "request", "status": "error", "message": "This endpoint does not exist."}

    def facebook(request, context):
        if "next" in request.qs:
            context.status_code = 404
            return broken
        ref = {"pk-a": "a", "pk-b": "b"}[request.headers["Profile-Key"]]
        return {"posts": [{"id": f"fb-{ref}"}], "meta": {"pagination": {"hasMore": True, "next": "c2"}}}

    requests_mock.get(f"{API}/history/facebook", json=facebook)
    requests_mock.get(f"{API}/history/instagram", json={"posts": [{"id": "ig1"}], "meta": {"pagination": {"hasMore": False}}})
    output = _read("platform_posts", KEYED)

    assert sorted(r["id"] for r in _records(output)) == ["fb-a", "fb-b", "ig1", "ig1"]
    assert not output.errors


def test_other_404_on_platform_posts_still_fails(requests_mock):
    _mock_users(requests_mock)
    requests_mock.get(f"{API}/history/facebook", status_code=404, json={"code": 999, "status": "error"})
    requests_mock.get(f"{API}/history/instagram", json={"posts": []})
    output = _read("platform_posts", KEYED, expecting_exception=True)
    assert output.errors


def test_other_400_on_platform_posts_fails(requests_mock):
    _mock_users(requests_mock)
    requests_mock.get(f"{API}/history/facebook", status_code=400, json={"code": 101, "status": "error"})
    requests_mock.get(f"{API}/history/instagram", json={"posts": []})
    output = _read("platform_posts", KEYED, expecting_exception=True)
    assert output.errors


def test_social_analytics_body_and_platform_object(requests_mock):
    _mock_users(requests_mock)

    def analytics(request, context):
        p = request.json()["platforms"][0]
        return {p: {"analytics": {"followersCount": 10}}, "status": "success"}

    requests_mock.post(f"{API}/analytics/social", json=analytics)
    output = _read("social_analytics", KEYED)

    recs = _records(output)
    assert len(recs) == 4  # 2 profiles x 2 platforms
    fb_a = next(r for r in recs if r["ref_id"] == "ref-a" and r["platform"] == "facebook")
    assert fb_a["facebook"] == {"analytics": {"followersCount": 10}}
    assert {r.json()["platforms"][0] for r in requests_mock.request_history if r.method == "POST"} == {"facebook", "instagram"}


def test_social_analytics_daily_only_daily_capable_networks(requests_mock):
    _mock_users(requests_mock)
    requests_mock.post(f"{API}/analytics/social", json={"status": "success"})
    config = dict(KEYED, platforms=["facebook", "linkedin"])
    _read("social_analytics_daily", config)

    bodies = [r.json() for r in requests_mock.request_history if r.method == "POST"]
    assert {b["platforms"][0] for b in bodies} == {"facebook"}
    assert all(b["daily"] is True and b["quarters"] == 1 for b in bodies)


def test_post_analytics_and_comments_use_grandparent_profile_key(requests_mock):
    _mock_users(requests_mock)

    def history(request, context):
        ref = {"pk-a": "a", "pk-b": "b"}[request.headers["Profile-Key"]]
        return {"history": [{"id": f"post-{ref}"}]}

    requests_mock.get(f"{API}/history", json=history)
    requests_mock.post(f"{API}/analytics/post", json=lambda req, ctx: {"id": req.json()["id"], "facebook": {"analytics": {"likeCount": 1}}})
    requests_mock.get(f"{API}/comments/post-a", json={"id": "post-a", "facebook": [{"commentId": "c1"}]})
    requests_mock.get(f"{API}/comments/post-b", status_code=404, json={"code": 186, "status": "error"})

    analytics = _records(_read("post_analytics", KEYED))
    assert sorted((r["post_id"], r["ref_id"]) for r in analytics) == [("post-a", "ref-a"), ("post-b", "ref-b")]
    posts = [r for r in requests_mock.request_history if r.method == "POST"]
    assert sorted((r.json()["id"], r.headers["Profile-Key"]) for r in posts) == [("post-a", "pk-a"), ("post-b", "pk-b")]

    output = _read("comments", KEYED)
    assert _records(output) == [{"id": "post-a", "facebook": [{"commentId": "c1"}], "post_id": "post-a", "ref_id": "ref-a"}]
    assert not output.errors
    assert _sent(requests_mock, "/comments/post-a")[-1].headers["Profile-Key"] == "pk-a"


def _iso(days_ago):
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")


def test_platform_comments_recent_commented_posts_only(requests_mock):
    """Only posts from the last 90 days with comments (any recent YouTube video) get a comments call."""
    _mock_users(requests_mock)
    config = dict(KEYED, profile_keys="pk-a", platforms=["facebook", "youtube"])
    requests_mock.get(
        f"{API}/history/facebook",
        [
            {"json": {"posts": [
                {"id": "fb-new", "created": _iso(1), "commentsCount": 2},
                {"id": "fb-none", "created": _iso(2), "commentsCount": 0},
                {"id": "fb-old", "created": _iso(200), "commentsCount": 9},
            ], "meta": {"pagination": {"hasMore": True, "next": "p2"}}}},
            {"json": {"posts": [{"id": "fb-older", "created": _iso(300), "commentsCount": 5}],
                      "meta": {"pagination": {"hasMore": False}}}},
        ],
    )
    requests_mock.get(
        f"{API}/history/youtube",
        [
            # Not sorted: an old video first, a recent one on the next page.
            {"json": {"posts": [{"id": "yt-old", "created": _iso(400), "position": 0}],
                      "meta": {"pagination": {"hasMore": True, "next": "y2"}}}},
            {"json": {"posts": [{"id": "yt-off", "created": _iso(3), "position": 1},
                                {"id": "yt-new", "created": _iso(4), "position": 2}],
                      "meta": {"pagination": {"hasMore": False}}}},
        ],
    )
    requests_mock.get(f"{API}/comments/fb-new", json={
        "facebook": [{"commentId": "c1", "comment": "Nice", "created": _iso(1), "from": {"name": "Ann", "id": "1"},
                      "platform": "facebook", "replies": [{"commentId": "c1r", "comment": "Thanks", "from": {"name": "GP"}}]}],
        "status": "success", "commentsCount": 1, "lastUpdated": _iso(0)})
    requests_mock.get(f"{API}/comments/yt-off", status_code=403,
                      json={"code": 306, "action": "analytics", "status": "error", "message": "Comments are disabled"})
    requests_mock.get(f"{API}/comments/yt-new", json={
        "youtube": [{"commentId": "y1", "comment": "Great", "userName": "@viewer", "platform": "youtube"}],
        "status": "success"})

    output = _read("platform_comments", config)

    assert not output.errors
    recs = sorted(_records(output), key=lambda r: r["commentId"])
    assert [(r["commentId"], r["platform"], r["post_id"], r["ref_id"]) for r in recs] == [
        ("c1", "facebook", "fb-new", "ref-a"), ("y1", "youtube", "yt-new", "ref-a")]
    assert recs[0]["from"] == {"name": "Ann", "id": "1"} and recs[0]["replies"][0]["comment"] == "Thanks"
    assert recs[0]["raw"]["comment"] == "Nice" and "post_id" not in recs[0]["raw"]
    assert recs[1]["commenter_name"] == "@viewer" and "userName" in recs[1]["raw"]
    # Facebook stopped after page 1 (its last post is older than 90 days); YouTube paged in full.
    assert len(_sent(requests_mock, "/history/facebook")) == 1
    assert len(_sent(requests_mock, "/history/youtube")) == 2
    calls = [r for r in requests_mock.request_history if "/comments/" in r.url]
    assert sorted(r.url.split("?")[0].rsplit("/", 1)[1] for r in calls) == ["fb-new", "yt-new", "yt-off"]
    assert all(r.headers["Profile-Key"] == "pk-a" and r.qs["searchplatformid"] == ["true"] for r in calls)
    assert {r.qs["platform"][0] for r in calls} == {"facebook", "youtube"}


@pytest.mark.parametrize("platform, comment, name, cid", [
    ("facebook", {"from": {"name": "Ann", "id": "1"}}, "Ann", "1"),
    ("instagram", {"from": {"username": "ann.ig", "id": "2"}}, "ann.ig", "2"),
    ("tiktok", {"username": "ann_tt", "displayName": "Ann T", "userId": "3"}, "ann_tt", "3"),
    ("youtube", {"userName": "@ann", "channelUrl": "http://www.youtube.com/channel/UC4"}, "@ann",
     "http://www.youtube.com/channel/UC4"),
    ("tiktok", {}, None, None),
])
def test_platform_comments_commenter_per_network(requests_mock, platform, comment, name, cid):
    """Each network names the commenter differently; commenter_name/_id normalise it."""
    _mock_users(requests_mock)
    config = dict(KEYED, profile_keys="pk-a", platforms=[platform])
    requests_mock.get(f"{API}/history/{platform}", json={
        "posts": [{"id": "p1", "created": _iso(1), "commentsCount": 1}], "meta": {"pagination": {"hasMore": False}}})
    requests_mock.get(f"{API}/comments/p1", json={
        platform: [dict(comment, commentId="c1", comment="hi", platform=platform)], "status": "success"})

    recs = _records(_read("platform_comments", config))

    assert [(r.get("commenter_name"), r.get("commenter_id")) for r in recs] == [(name, cid)]


def test_batch_file_waits_until_written(requests_mock, monkeypatch):
    monkeypatch.setattr("time.sleep", lambda s: None)
    signed = "https://storage.googleapis.com/batch.ayrshare.com/users/x/users-batch.json?Signature=abc"
    requests_mock.get(f"{API}/user/batch", json={"success": True, "url": signed})
    requests_mock.get(signed, [{"json": {}}, {"json": {}}, {"json": {"users": [{"refId": "r1"}, {"refId": "r2"}]}}])
    output = _read("profile_users", {"api_key": "primary-key"})

    assert [r["refId"] for r in _records(output)] == ["r1", "r2"]
    downloads = [r for r in requests_mock.request_history if r.url.startswith("https://storage.googleapis.com")]
    assert len(downloads) == 3
    assert "Authorization" not in downloads[0].headers  # never send the API key to the signed URL


def test_action_log_and_daily_counts_share_one_response(requests_mock):
    requests_mock.get(
        f"{API}/profiles",
        json={"profiles": {"actionLog": [{"action": "create", "refId": "r1", "created": "2026-11-04T22:28:31.710Z"}],
                           "userProfileReport": [{"reported": "2026-11-05T09:17:20.035Z", "userProfilesCount": 9}]}},
    )
    assert _records(_read("profile_action_log", {"api_key": "k"}))[0]["refId"] == "r1"
    assert _records(_read("profile_counts_daily", {"api_key": "k"}))[0]["userProfilesCount"] == 9
    assert _sent(requests_mock, "/profiles")[0].qs["actionlog"] == ["365"]
