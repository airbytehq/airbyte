# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Offline tests for manifest.yaml against a mocked Sprout Social API.

Each test reads through the airbyte-cdk declarative runtime and asserts on the
HTTP requests the connector makes and the records it emits. Response shapes
follow what the Sprout Social API v1 returns.
"""

import copy
import logging
import time
from datetime import date
from pathlib import Path

import pytest
import requests_mock
import yaml

from airbyte_cdk.models import (
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
)
from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource
from airbyte_cdk.test.entrypoint_wrapper import read


MANIFEST = yaml.safe_load((Path(__file__).parent.parent / "manifest.yaml").read_text())
METRICS = MANIFEST["definitions"]["metric_lists"]
BASE = "https://api.sproutsocial.com/v1/"
CID = "1234567"
CONFIG = {"api_token": "test-token", "customer_ids": [CID], "start_date": "2024-06-01"}
PROFILES = [
    {"customer_profile_id": 1000001, "network_type": "facebook", "name": "FB", "groups": [501]},
    {"customer_profile_id": 1000002, "network_type": "fb_instagram_account", "name": "IG", "groups": [502]},
    {"customer_profile_id": 1000003, "network_type": "linkedin_company", "name": "LI", "groups": [501]},
    {"customer_profile_id": 9999999, "network_type": "bluesky", "name": "no metrics", "groups": [501]},
]
CID2 = "2222222"  # a second customer on the same token
PROFILES2 = [{"customer_profile_id": 7000001, "network_type": "twitter", "name": "X", "groups": [42]}]
ALL_STREAMS = [
    "clients",
    "customer_profiles",
    "tags",
    "groups",
    "users",
    "topics",
    "teams",
    "queues",
    "profile_analytics",
    "post_analytics",
]


def catalog(*names):
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name=n, json_schema={}, supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental]),
                sync_mode=SyncMode.incremental if n.endswith("_analytics") else SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
            )
            for n in names
        ]
    )


def run(config, names, manifest=MANIFEST, **kw):
    cat = catalog(*names)
    source = ConcurrentDeclarativeSource(catalog=cat, config=config, state=None, source_config=manifest)
    return read(source, config, cat, **kw)


def fast_backoff(manifest):
    m = copy.deepcopy(manifest)
    m["definitions"]["requester"]["error_handler"]["backoff_strategies"] = [
        {"type": "ConstantBackoffStrategy", "backoff_time_in_seconds": 0.01}
    ]
    return m


def profile_id(body):
    return int(body["filters"][0].split("(")[1].rstrip(")"))


class FakeSprout:
    """Mocks the endpoints and records request bodies. Facebook has 3 pages of posts."""

    def __init__(self, m, posts_status=None, customers=None):
        self.posts, self.profiles = [], []
        self.posts_status = posts_status
        customers = customers or {CID: PROFILES}
        m.get(BASE + "metadata/client", json={"data": [{"customer_id": int(c), "name": f"Customer {c}"} for c in customers]})
        for cid, profiles in customers.items():
            m.get(BASE + f"{cid}/metadata/customer", json={"data": profiles})
            m.get(
                BASE + f"{cid}/metadata/customer/tags", json={"data": [{"tag_id": 111, "text": "CAMP_X", "active": True, "groups": [501]}]}
            )
            for name in ("groups", "users", "topics", "teams", "queues"):
                m.get(BASE + f"{cid}/metadata/customer/{name}", json={"data": []})
            m.post(BASE + f"{cid}/analytics/posts", json=self._posts)
            m.post(BASE + f"{cid}/analytics/profiles", json=self._profiles)

    def _posts(self, request, context):
        body = request.json()
        self.posts.append({**body, "_customer": request.path.split("/")[2]})
        if self.posts_status and self.posts_status(len(self.posts)) != 200:
            context.status_code = self.posts_status(len(self.posts))
            return {"error": "gateway timeout"}
        pid, page = profile_id(body), body.get("page", 1)
        return {
            "data": [
                {
                    "guid": f"p:{pid}_{page}{i}",
                    "customer_profile_id": str(pid),  # Sprout returns it as a string on posts
                    "created_time": f"2026-0{page}-1{i}T12:00:00Z",
                    "from": {"name": "Example Brand", "screen_name": "examplebrand"},
                    "internal": {"tags": [{"id": 111}]},
                    "pinterest.board_name": "Board",
                    "metrics": {"lifetime.impressions": 100 * page + i, "lifetime.reactions": i},
                }
                for i in range(2)
            ],
            "paging": {"current_page": page, "total_pages": 3 if pid == 1000001 else 1},
        }

    def _profiles(self, request, context):
        body = request.json()
        self.profiles.append({**body, "_customer": request.path.split("/")[2]})
        return {
            "data": [
                {
                    "dimensions": {"customer_profile_id": profile_id(body), "reporting_period.by(day)": "2026-10-01"},
                    "metrics": {"lifetime_snapshot.followers_count": 1234, "impressions": 55, "posts_sent_by_post_type": {"photo": 2}},
                }
            ],
            "paging": {"current_page": 1, "total_pages": 1},
        }


@pytest.fixture(scope="module")
def full_read():
    with requests_mock.Mocker() as m:
        api = FakeSprout(m)
        out = run(CONFIG, ALL_STREAMS)
    records = {}
    for msg in out.records:
        records.setdefault(msg.record.stream, []).append(msg.record.data)
    return api, out, records


def test_discover_streams_keys_and_cursors():
    config = dict(CONFIG)
    source = ConcurrentDeclarativeSource(catalog=None, config=config, state=None, source_config=MANIFEST)
    streams = {s.name: s for s in source.discover(logging.getLogger(), config).streams}
    assert sorted(streams) == sorted(ALL_STREAMS)
    assert streams["post_analytics"].source_defined_primary_key == [["guid"]]
    assert streams["post_analytics"].default_cursor_field == ["created_time"]
    assert streams["profile_analytics"].source_defined_primary_key == [["customer_profile_id"], ["reporting_period_by_day"]]
    assert streams["profile_analytics"].default_cursor_field == ["reporting_period_by_day"]
    assert streams["tags"].source_defined_primary_key == [["customer_id"], ["tag_id"]]
    assert streams["clients"].source_defined_primary_key == [["customer_id"]]


def test_full_read_has_no_errors(full_read):
    _, out, records = full_read
    assert not out.errors
    assert len(records["customer_profiles"]) == 4
    assert len(records["tags"]) == 1


def test_per_network_metrics_in_body(full_read):
    api, _, _ = full_read
    by_pid = {}
    for b in api.posts:
        by_pid.setdefault(profile_id(b), b)
    assert by_pid[1000001]["metrics"] == METRICS["post_metrics"]["facebook"]
    assert by_pid[1000002]["metrics"] == METRICS["post_metrics"]["fb_instagram_account"]
    assert by_pid[1000003]["metrics"] == METRICS["post_metrics"]["linkedin_company"]
    prof = {profile_id(b): b for b in api.profiles}
    assert prof[1000001]["metrics"] == METRICS["profile_metrics"]["facebook"]
    assert isinstance(by_pid[1000001]["fields"], list) and "internal" in by_pid[1000001]["fields"]


def test_network_without_metrics_is_not_requested(full_read):
    api, _, records = full_read
    assert 9999999 not in {profile_id(b) for b in api.posts + api.profiles}
    # ...but the profile itself still lands in customer_profiles
    assert 9999999 in {r["customer_profile_id"] for r in records["customer_profiles"]}


def test_page_in_body_stops_at_total_pages(full_read):
    api, _, _ = full_read
    fb = [b for b in api.posts if profile_id(b) == 1000001]
    slices = {b["filters"][1] for b in fb}
    pages = sorted(b.get("page", 1) for b in fb)
    assert pages == sorted([1, 2, 3] * len(slices))  # never page 4 (Sprout returns 400 past the end)
    assert all(b["limit"] == 50 and isinstance(b["limit"], int) for b in fb)


def _range(filter_):
    lo, hi = filter_.split("(", 1)[1].rstrip(")").split("..")
    return date.fromisoformat(lo[:10]), date.fromisoformat(hi[:10])


def test_profile_slices_are_at_most_one_year(full_read):
    # Sprout rejects reporting_period ranges over one year (400). Inclusive range => <= 365 days.
    api, _, _ = full_read
    for b in api.profiles:
        assert ".." in b["filters"][1] and "..." not in b["filters"][1]
        lo, hi = _range(b["filters"][1])
        assert (hi - lo).days + 1 <= 365, b["filters"][1]


def test_profile_slice_ending_today_is_at_most_one_year():
    # Regression: with step P365D a slice ending exactly on today was 366 days.
    start = date.today().replace(year=date.today().year - 1).isoformat()
    with requests_mock.Mocker() as m:
        api = FakeSprout(m)
        out = run({**CONFIG, "start_date": start, "profile_ids": ["1000001"]}, ["profile_analytics"])
    assert not out.errors
    for b in api.profiles:
        lo, hi = _range(b["filters"][1])
        assert (hi - lo).days + 1 <= 365, b["filters"][1]


def test_metric_keys_are_flattened_and_cleaned(full_read):
    _, _, records = full_read
    post = records["post_analytics"][0]
    assert {"lifetime_impressions", "lifetime_reactions", "pinterest_board_name"} <= set(post)
    assert "metrics" not in post
    assert isinstance(post["internal"], dict) and isinstance(post["from"], dict)
    assert post["customer_profile_id"] == int(post["customer_profile_id"]) and isinstance(post["customer_profile_id"], int)
    prof = records["profile_analytics"][0]
    assert {"reporting_period_by_day", "lifetime_snapshot_followers_count", "impressions", "customer_profile_id"} <= set(prof)
    assert "dimensions" not in prof and "metrics" not in prof
    assert isinstance(prof["posts_sent_by_post_type"], dict)


def test_record_keys_are_declared_in_schema(full_read):
    _, _, records = full_read
    for stream in ("post_analytics", "profile_analytics", "customer_profiles", "tags"):
        declared = set(MANIFEST["definitions"]["streams"][stream]["schema_loader"]["schema"]["properties"])
        undeclared = set().union(*map(set, records[stream])) - declared
        assert not undeclared, (stream, undeclared)


def test_every_declared_property_has_a_type():
    # Some destinations drop a column declared as `{}` instead of typing it,
    # which loses nested fields such as `from`, `internal` and `visual_media`.
    for name, stream in MANIFEST["definitions"]["streams"].items():
        props = stream["schema_loader"]["schema"]["properties"]
        untyped = sorted(k for k, v in props.items() if "type" not in v)
        assert not untyped, (name, untyped)


def test_state_is_per_profile_on_renamed_cursors(full_read):
    _, out, _ = full_read
    blobs = {s.state.stream.stream_descriptor.name: s.state.stream.stream_state.__dict__ for s in out.state_messages}
    for stream, cursor in (("profile_analytics", "reporting_period_by_day"), ("post_analytics", "created_time")):
        states = blobs[stream]["states"]
        assert {s["partition"]["customer_profile_id"] for s in states} == {1000001, 1000002, 1000003}
        assert {s["partition"]["parent_slice"]["customer_id"] for s in states} == {CID}
        assert all(cursor in s["cursor"] for s in states)


def test_multiple_customers():
    customers = {CID: PROFILES, CID2: PROFILES2}
    with requests_mock.Mocker() as m:
        api = FakeSprout(m, customers=customers)
        out = run({**CONFIG, "customer_ids": [CID, CID2]}, ALL_STREAMS)
        paths = {r.path for r in m.request_history}
    assert not out.errors
    records = {}
    for msg in out.records:
        records.setdefault(msg.record.stream, []).append(msg.record.data)
    # Every customer-scoped endpoint is read once per customer, under its own ID.
    for cid in customers:
        assert f"/v1/{cid}/metadata/customer/tags" in paths
    assert {(r["customer_id"], r["customer_profile_id"]) for r in records["customer_profiles"]} == {
        (int(c), p["customer_profile_id"]) for c, ps in customers.items() for p in ps
    }
    assert sorted(r["customer_id"] for r in records["tags"]) == [int(CID), int(CID2)]
    # Analytics requests go to the profile's own customer, and records carry it.
    assert {(b["_customer"], profile_id(b)) for b in api.posts} == {(CID, 1000001), (CID, 1000002), (CID, 1000003), (CID2, 7000001)}
    assert {(r["customer_id"], r["customer_profile_id"]) for r in records["post_analytics"]} >= {(int(CID2), 7000001)}
    assert {r["customer_id"] for r in records["profile_analytics"]} == {int(CID), int(CID2)}
    assert METRICS["post_metrics"]["twitter"] == next(b for b in api.posts if b["_customer"] == CID2)["metrics"]


def test_only_configured_customers_are_read():
    with requests_mock.Mocker() as m:
        FakeSprout(m, customers={CID: PROFILES, CID2: PROFILES2})
        out = run(CONFIG, ["customer_profiles", "tags"])
        paths = {r.path for r in m.request_history}
    assert not out.errors
    assert not any(p.startswith(f"/v1/{CID2}/") for p in paths)


def test_transient_504_is_retried():
    with requests_mock.Mocker() as m:
        api = FakeSprout(m, posts_status=lambda n: 504 if n <= 2 else 200)
        out = run({**CONFIG, "profile_ids": ["1000003"]}, ["post_analytics"], manifest=fast_backoff(MANIFEST))
    assert not out.errors
    assert len(out.records) > 0 and len(api.posts) >= 3


def test_persistent_504_fails_the_sync():
    with requests_mock.Mocker() as m:
        FakeSprout(m, posts_status=lambda n: 504)
        out = run({**CONFIG, "profile_ids": ["1000003"]}, ["post_analytics"], manifest=fast_backoff(MANIFEST), expecting_exception=True)
    assert out.errors
    assert any("post_analytics" in str(e.trace.error.message) for e in out.errors)


def test_api_budget_throttles():
    m2 = copy.deepcopy(MANIFEST)
    m2["api_budget"]["policies"][0]["rates"] = [{"limit": 4, "interval": "PT2S"}]
    with requests_mock.Mocker() as m:
        FakeSprout(m)
        t0 = time.time()
        out = run({**CONFIG, "profile_ids": ["1000001"]}, ["customer_profiles", "post_analytics"], manifest=m2)
        took = time.time() - t0
        calls = len(m.request_history)
    assert not out.errors
    assert calls > 8 and took >= 2 * ((calls - 1) // 4) * 0.8
