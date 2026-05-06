# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for cursor-based pagination on the Confluence v2 streams.

The Confluence Cloud REST API v2 (`/wiki/api/v2/...`) only supports cursor-based
pagination — it ignores the `start` parameter that Confluence v1 uses. Each
paginated response carries the cursor for the next page in `_links.next`, e.g.
`/wiki/api/v2/pages?limit=25&cursor=<token>`. When `_links.next` is absent there
are no more pages.

These tests register a mock that varies its response based on the `cursor` query
parameter and assert that the connector:

1. Issues the first request without a `cursor` parameter (only `limit`).
2. Extracts the cursor token from `_links.next` on the first response.
3. Issues the second request with that token in the `cursor` query parameter.
4. Stops paginating once `_links.next` is absent.
5. Emits records from every page in order.
"""

from urllib.parse import parse_qs, urlsplit

import requests_mock
from _helpers import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


def _parsed_qs(url: str) -> dict:
    """Parse the case-preserving query string off `url`.

    `requests_mock.Request.qs` lowercases both keys and values, which strips the
    original casing from the opaque cursor token. Parsing the raw URL with
    `urllib.parse` preserves the value casing the connector actually sent.
    """
    return parse_qs(urlsplit(url).query, keep_blank_values=True)


_CONFIG = {
    "email": "test@example.com",
    "api_token": "test-api-token",
    "domain_name": "example.atlassian.net",
}

_NEXT_CURSOR_TOKEN = "eyJpZCI6IjEyMyIsImxpbWl0IjoyNX0"  # opaque, base64-ish

# Stream-name → (URL path on the Atlassian host, primary-key field)
_V2_STREAMS = {
    "blog_posts": "/wiki/api/v2/blogposts",
    "pages": "/wiki/api/v2/pages",
    "space": "/wiki/api/v2/spaces",
}


def _record(record_id: str) -> dict:
    """Minimal record payload — Confluence v2 records have many fields, but the
    pagination logic only depends on `_links.next`, so we keep records small."""
    return {"id": record_id, "title": f"item-{record_id}", "status": "current"}


def _make_paginated_callback(path: str):
    """Build a `requests_mock` callback that returns two pages keyed off the
    `cursor` query parameter on `path`.

    Page 1 (no `cursor` in request): returns records 1, 2 plus a `_links.next`
    pointing at `cursor=<token>`. Page 2 (`cursor=<token>` in request): returns
    records 3, 4 with no `_links.next`, signalling end of pagination.
    """

    def _callback(request, context):
        qs = _parsed_qs(request.url)
        cursor = qs.get("cursor", [None])[0]
        if cursor is None:
            return {
                "results": [_record("1"), _record("2")],
                "_links": {
                    "next": f"{path}?limit=25&cursor={_NEXT_CURSOR_TOKEN}",
                    "base": "https://example.atlassian.net/wiki",
                },
            }
        assert cursor == _NEXT_CURSOR_TOKEN, f"expected cursor={_NEXT_CURSOR_TOKEN!r} on page 2 request, got {cursor!r}"
        return {
            "results": [_record("3"), _record("4")],
            "_links": {
                "base": "https://example.atlassian.net/wiki",
            },
        }

    return _callback


def _sync(stream_name: str, mocker: requests_mock.Mocker):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    source = get_source(config=_CONFIG)
    return read(source, _CONFIG, catalog)


def _assert_v2_cursor_pagination(stream_name: str, path: str) -> None:
    url = f"https://example.atlassian.net{path}"
    with requests_mock.Mocker() as mocker:
        mocker.get(url, json=_make_paginated_callback(path))
        output = _sync(stream_name, mocker)

        requests_made = [r for r in mocker.request_history if r.path == path]

    assert len(requests_made) == 2, (
        f"expected exactly two paginated requests for {stream_name}, got {len(requests_made)}: {[r.url for r in requests_made]}"
    )

    first_qs = _parsed_qs(requests_made[0].url)
    assert "cursor" not in first_qs, f"first request to {stream_name} must not include a cursor parameter, got qs={first_qs}"
    assert first_qs.get("limit") == ["25"], f"first request to {stream_name} must include limit=25, got qs={first_qs}"
    assert "start" not in first_qs, f"v2 stream {stream_name} must not send the v1 offset `start` parameter, got qs={first_qs}"

    second_qs = _parsed_qs(requests_made[1].url)
    assert second_qs.get("cursor") == [_NEXT_CURSOR_TOKEN], (
        f"second request to {stream_name} must inject the cursor token from _links.next, got qs={second_qs}"
    )
    assert second_qs.get("limit") == ["25"], f"second request to {stream_name} must include limit=25, got qs={second_qs}"

    emitted_ids = [record.record.data["id"] for record in output.records]
    assert emitted_ids == ["1", "2", "3", "4"], f"expected records from both pages of {stream_name}, got {emitted_ids}"


def test_blog_posts_uses_v2_cursor_pagination():
    """`blog_posts` reads `_links.next` for the next-page cursor."""
    _assert_v2_cursor_pagination("blog_posts", "/wiki/api/v2/blogposts")


def test_pages_uses_v2_cursor_pagination():
    """`pages` reads `_links.next` for the next-page cursor."""
    _assert_v2_cursor_pagination("pages", "/wiki/api/v2/pages")


def test_space_uses_v2_cursor_pagination():
    """`space` reads `_links.next` for the next-page cursor."""
    _assert_v2_cursor_pagination("space", "/wiki/api/v2/spaces")
