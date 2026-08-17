# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for `source-ashby` pagination request bodies.

Ashby's `.list` endpoints document the page size as `limit` and the page token as `cursor`
(https://developers.ashbyhq.com/docs/pagination-and-incremental-sync). These tests assert the
exact request bodies the connector sends so the configured page size actually reaches the API.
"""

import json

import pytest
import requests_mock
from _helpers import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_CONFIG = {"api_key": "test-api-key", "start_date": "2017-01-25T00:00:00Z"}

_PAGE_SIZE = 100


def _read(stream_name: str):
    source = get_source(config=_CONFIG)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(source=source, config=_CONFIG, catalog=catalog)


def _request_bodies(mocker: requests_mock.Mocker, path: str) -> list[dict]:
    return [json.loads(request.text or "{}") for request in mocker.request_history if request.path == path]


@pytest.mark.parametrize(
    "stream_name, path",
    [
        ("users", "/user.list"),
        ("candidates", "/candidate.list"),
        ("applications", "/application.list"),
    ],
)
def test_page_size_is_sent_as_limit(stream_name: str, path: str) -> None:
    """Every paginated request carries the page size as `limit`, and never as the unsupported `per_page`."""
    page_1 = {
        "success": True,
        "results": [{"id": "record-1"}],
        "moreDataAvailable": True,
        "nextCursor": "page-2-token",
    }
    page_2 = {"success": True, "results": [{"id": "record-2"}], "moreDataAvailable": False}

    with requests_mock.Mocker() as mocker:
        mocker.post(
            f"https://api.ashbyhq.com{path}",
            [
                {"json": page_1, "status_code": 200},
                {"json": page_2, "status_code": 200},
            ],
        )
        output = _read(stream_name)

    emitted_ids = [record.record.data["id"] for record in output.records]
    assert emitted_ids == ["record-1", "record-2"], f"expected both pages to be emitted, got {emitted_ids}"

    bodies = _request_bodies(mocker, path)
    assert len(bodies) == 2, f"expected 2 paginated requests against {path}, got {len(bodies)}"
    for body in bodies:
        assert body.get("limit") == _PAGE_SIZE, f"page size must be sent as `limit`; got {body}"
        assert "per_page" not in body, f"`per_page` is not a documented Ashby request field; got {body}"

    assert "cursor" not in bodies[0], f"first request must not carry a cursor; got {bodies[0]}"
    assert bodies[1].get("cursor") == "page-2-token", f"second request must forward `nextCursor`; got {bodies[1]}"
