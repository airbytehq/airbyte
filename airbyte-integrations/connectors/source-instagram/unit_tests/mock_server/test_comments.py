# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from urllib.parse import parse_qs, urlparse

import jsonschema
import pytest
import requests_cache

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.call_rate import HttpAPIBudget
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover, read

from ..conftest import find_stream, get_source


BASE = "https://graph.facebook.com/v23.0"
FIELDS = "id,text,timestamp,username,from,hidden,like_count"


@pytest.fixture(autouse=True)
def clear_cache(monkeypatch):
    monkeypatch.delenv("REQUEST_CACHE_PATH", raising=False)
    requests_cache.SQLiteCache("file::memory:?cache=shared").clear()


@pytest.fixture
def comments_config():
    return {"access_token": "test-token", "start_date": "2026-11-01T00:00:00Z", "enable_comments": True}


def accounts(requests_mock, count=1):
    return requests_mock.get(
        f"{BASE}/me/accounts",
        json={"data": [{"id": f"page-{i}", "instagram_business_account": {"id": f"account-{i}"}} for i in range(count)]},
    )


def comment(comment_id="c1"):
    return {
        "id": comment_id,
        "text": "Example comment",
        "timestamp": "2026-01-01T01:02:03+0000",
        "username": None,
        "from": None,
        "hidden": False,
        "like_count": 0,
    }


def read_comments(config, expecting_exception=False, media=False):
    catalog = CatalogBuilder().with_stream("comments", SyncMode.full_refresh)
    if media:
        catalog.with_stream("media", SyncMode.full_refresh)
    return read(get_source(config), config, catalog.build(), expecting_exception=expecting_exception)


def test_catalog_and_old_config(comments_config):
    default = {**comments_config, "enable_comments": False}
    old = discover(get_source(default), default).catalog.catalog.streams
    new = discover(get_source(comments_config), comments_config).catalog.catalog.streams
    assert len(old) == 8
    assert {s.name for s in new} == {s.name for s in old} | {"comments"}
    old_streams = {s.name: s for s in old}
    assert all(s == old_streams[s.name] for s in new if s.name != "comments")
    stream = next(s for s in new if s.name == "comments")
    assert stream.supported_sync_modes == [SyncMode.full_refresh]
    assert stream.source_defined_primary_key == [["id"]]


def test_two_accounts_media_and_comment_pages(comments_config, requests_mock):
    accounts(requests_mock, 2)
    for i in range(2):
        requests_mock.get(
            f"{BASE}/account-{i}/media",
            [
                {
                    "json": {
                        "data": [{"id": f"m{i}a"}],
                        "paging": {"cursors": {"after": f"media-{i}"}, "next": "https://graph.facebook.com/next"},
                    }
                },
                {"json": {"data": [{"id": f"m{i}b"}], "paging": {"cursors": {"after": "terminal"}}}},
            ],
        )
        for suffix in "ab":
            requests_mock.get(
                f"{BASE}/m{i}{suffix}/comments",
                [
                    {
                        "json": {
                            "data": [comment(f"c{i}{suffix}1")],
                            "paging": {"cursors": {"after": "AbC+/="}, "next": "https://graph.facebook.com/next"},
                        }
                    },
                    {"json": {"data": [comment(f"c{i}{suffix}2")], "paging": {"cursors": {"after": "terminal"}}}},
                ],
            )
    output = read_comments(comments_config)
    assert not output.errors
    assert len(output.records) == 8
    schema = find_stream("comments", comments_config).get_json_schema()
    for message in output.records:
        data = message.record.data
        account_index, suffix = data["id"][1:3]
        assert data["media_id"] == f"m{account_index}{suffix}"
        assert data["business_account_id"] == f"account-{account_index}"
        assert data["page_id"] == f"page-{account_index}"
        assert set(data) <= set(schema["properties"])
        jsonschema.validate(data, schema, format_checker=jsonschema.FormatChecker())
    comments_requests = [r for r in requests_mock.request_history if r.path.endswith("/comments")]
    assert len(comments_requests) == 8
    for request in comments_requests:
        params = parse_qs(urlparse(request.url).query)
        assert params["fields"] == [FIELDS]
        assert params["limit"] == ["50"]
        assert params.get("after", ["AbC+/="]) == ["AbC+/="]
        assert request.headers["Authorization"] == "Bearer test-token"
    media_requests = [r for r in requests_mock.request_history if r.path.endswith("/media")]
    assert len(media_requests) == 4
    assert all(r.qs["fields"] == ["id"] for r in media_requests)
    assert all("since" not in r.qs for r in media_requests)


@pytest.mark.parametrize("data", [[], [comment()]])
@pytest.mark.parametrize("paging", [None, {}, {"cursors": None}, {"cursors": {"before": "before", "after": "last"}}])
def test_final_cursors_do_not_loop(comments_config, requests_mock, data, paging):
    accounts(requests_mock)
    requests_mock.get(f"{BASE}/account-0/media", json={"data": [{"id": "old-media"}]})
    endpoint = requests_mock.get(f"{BASE}/old-media/comments", json={"data": data, "paging": paging})
    output = read_comments(comments_config)
    assert len(output.records) == len(data)
    assert endpoint.call_count == 1


def test_nullable_redacted_authors_and_optional_fields(comments_config, requests_mock):
    accounts(requests_mock)
    requests_mock.get(f"{BASE}/account-0/media", json={"data": [{"id": "media"}]})
    requests_mock.get(
        f"{BASE}/media/comments", json={"data": [{"id": "c1"}, {**comment("c2"), "from": {"id": "author", "username": "example"}}]}
    )
    output = read_comments(comments_config)
    assert len(output.records) == 2
    schema = find_stream("comments", comments_config).get_json_schema()
    for record in output.records:
        jsonschema.validate(record.record.data, schema)
    assert "text" not in output.records[0].record.data


@pytest.mark.parametrize("stage", ["accounts", "media", "comments"])
@pytest.mark.parametrize("status,code", [(400, 10), (403, 200), (400, 190), (400, 100), (404, 100)])
def test_denied_parent_or_edge_fails(comments_config, requests_mock, stage, status, code):
    accounts(requests_mock)
    requests_mock.get(f"{BASE}/account-0/media", json={"data": [{"id": "media"}]})
    requests_mock.get(f"{BASE}/media/comments", json={"data": []})
    url = {"accounts": "me/accounts", "media": "account-0/media", "comments": "media/comments"}[stage]
    endpoint = requests_mock.get(
        f"{BASE}/{url}", status_code=status, json={"error": {"code": code, "message": "Access denied", "error_subcode": 33}}
    )
    output = read_comments(comments_config, expecting_exception=True)
    assert output.errors
    assert endpoint.call_count == 1
    messages = str([error.trace.error.message for error in output.errors])
    assert "comments" in messages or "permission" in messages.lower()


@pytest.mark.parametrize(
    "status,body",
    [
        (429, {"error": {"code": 4}}),
        (400, {"error": {"code": 613}}),
        (400, {"error": {"code": 2, "is_transient": True}}),
        (500, {"error": {"code": 2}}),
    ],
)
def test_transient_graph_errors_retry(comments_config, requests_mock, mocker, status, body):
    # As in test_streams.test_common_error_retry, isolate retry handling from the
    # budget's real-time bucket reset because the suite mocks time.sleep.
    update_budget = mocker.patch.object(HttpAPIBudget, "update_from_response")
    accounts(requests_mock)
    requests_mock.get(f"{BASE}/account-0/media", json={"data": [{"id": "media"}]})
    endpoint = requests_mock.get(
        f"{BASE}/media/comments",
        [
            {"status_code": status, "json": body, "headers": {"Retry-After": "0"}},
            {"json": {"data": [comment()]}},
        ],
    )
    assert len(read_comments(comments_config).records) == 1
    assert endpoint.call_count == 2
    assert update_budget.call_count >= 4  # Parents and edge still use the shared budget.


def test_retries_are_bounded(comments_config, requests_mock):
    accounts(requests_mock)
    requests_mock.get(f"{BASE}/account-0/media", json={"data": [{"id": "media"}]})
    endpoint = requests_mock.get(f"{BASE}/media/comments", status_code=400, json={"error": {"code": 4}})
    assert read_comments(comments_config, expecting_exception=True).errors
    assert endpoint.call_count == 6


def test_account_pages_skip_pages_without_a_professional_account(comments_config, requests_mock):
    account_request = requests_mock.get(
        f"{BASE}/me/accounts",
        [
            {
                "json": {
                    "data": [
                        {"id": "unlinked"},
                        {"id": "null", "instagram_business_account": None},
                        {"id": "empty", "instagram_business_account": {}},
                    ],
                    "paging": {"cursors": {"after": "account-next"}, "next": "https://graph.facebook.com/next"},
                }
            },
            {
                "json": {
                    "data": [{"id": "page", "instagram_business_account": {"id": "account"}}],
                    "paging": {"cursors": {"after": "terminal"}},
                }
            },
        ],
    )
    requests_mock.get(f"{BASE}/account/media", json={"data": [{"id": "media"}]})
    requests_mock.get(f"{BASE}/media/comments", json={"data": [comment()]})
    output = read_comments(comments_config)
    assert len(output.records) == 1
    assert output.records[0].record.data["page_id"] == "page"
    assert account_request.call_count == 2
    assert account_request.last_request.qs["after"] == ["account-next"]


def test_no_professional_accounts_is_successfully_empty(comments_config, requests_mock):
    accounts(requests_mock, 0)
    output = read_comments(comments_config)
    assert not output.records
    assert not output.errors
    assert requests_mock.call_count == 1


def test_empty_nonterminal_pages_continue(comments_config, requests_mock):
    accounts(requests_mock)
    media = requests_mock.get(
        f"{BASE}/account-0/media",
        [
            {"json": {"data": [], "paging": {"cursors": {"after": "more-media"}, "next": "https://graph.facebook.com/next"}}},
            {"json": {"data": [{"id": "media"}]}},
        ],
    )
    comments = requests_mock.get(
        f"{BASE}/media/comments",
        [
            {"json": {"data": [], "paging": {"cursors": {"after": "more-comments"}, "next": "https://graph.facebook.com/next"}}},
            {"json": {"data": [comment()]}},
        ],
    )
    assert len(read_comments(comments_config).records) == 1
    assert media.call_count == 2
    assert comments.call_count == 2


def test_media_and_comments_do_not_repeat_carousel_enrichment(comments_config, requests_mock):
    account_request = accounts(requests_mock)
    media_request = requests_mock.get(
        f"{BASE}/account-0/media",
        json={
            "data": [
                {
                    "id": "carousel",
                    "media_type": "CAROUSEL_ALBUM",
                    "media_product_type": "FEED",
                    "timestamp": "2020-01-01T00:00:00+0000",
                    "children": {"data": [{"id": "child"}]},
                }
            ]
        },
    )
    child_request = requests_mock.get(f"{BASE}/child", json={"id": "child", "media_type": "IMAGE", "timestamp": "2020-01-01T00:00:00+0000"})
    comment_request = requests_mock.get(f"{BASE}/carousel/comments", json={"data": [comment()]})
    output = read_comments(comments_config, media=True)
    assert {r.record.stream for r in output.records} == {"media", "comments"}
    assert child_request.call_count == 1
    assert comment_request.call_count == 1
    # Concurrent parent reads can race before their shared HTTP cache is populated.
    assert 1 <= account_request.call_count <= 2
    assert media_request.call_count == 2  # One detailed listing and one ID-only listing.
