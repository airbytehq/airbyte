# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for `source-linkly` covering the manifest behaviours that are easy to regress:

- the API key is sent as `Authorization: Bearer <key>`, and a 401 surfaces as a config error
  (from both `check` and `read`) instead of being retried
- a 429 is retried rather than failing the sync
- `workspaces` is the parent of every other stream: each child stream requests once per
  workspace, and the `domains`, `clicks` and `conversions` records carry that `workspace_id`
- `links` pages with `page` / `page_size=1000` and stops on a short page
- `conversions` is scoped through the `workspace_id` query parameter (without it the
  endpoint answers 401), pages with `after` = the last id while `has_more` is true, and
  syncs incrementally on `inserted_at` via `since`, re-reading the hour before the cursor
- `clicks` requests the daily series from `start_date` to today, re-reads two days before
  the saved cursor, and drops buckets without a day
"""

import logging

import pytest
import requests_mock
from _helpers import (
    API_KEY,
    CONFIG,
    CONVERSIONS_URL,
    START_DATE,
    WORKSPACES_URL,
    get_source,
    query_params,
    read_stream,
    records,
    requests_to,
    workspace_url,
)
from freezegun import freeze_time

from airbyte_cdk.models import FailureType, Status, SyncMode
from airbyte_cdk.test.state_builder import StateBuilder


WORKSPACES_PATH = "/api/v1/workspaces"
CONVERSIONS_PATH = "/api/v1/conversions"

UNAUTHORIZED = {"error": "Not authorized", "code": "unauthorized"}


@pytest.fixture
def no_backoff_sleep(monkeypatch):
    """Skip the real backoff waits, so a status that regresses to being retried fails fast instead of stalling."""
    monkeypatch.setattr("time.sleep", lambda _seconds: None)


def _workspace_path(workspace_id: int, endpoint: str) -> str:
    return f"/api/v1/workspace/{workspace_id}/{endpoint}"


def _link(link_id: int, workspace_id: int) -> dict:
    return {
        "id": link_id,
        "workspace_id": workspace_id,
        "url": f"https://example.com/{link_id}",
        "full_url": f"https://demo.linkly.so/{link_id}",
        "clicks_total": 3,
    }


def _links_page(links: list, page_number: int, total_pages: int) -> dict:
    """Linkly's list_links envelope: records under `links` plus page metadata the connector ignores."""
    return {
        "links": links,
        "page_size": 1000,
        "page_number": page_number,
        "total_pages": total_pages,
        "total_entries": 1001,
    }


def test_api_key_is_sent_as_bearer_token():
    with requests_mock.Mocker() as mocker:
        mocker.get(WORKSPACES_URL, json=[{"id": 7, "name": "Marketing"}])
        output = read_stream("workspaces")

    assert records(output) == [{"id": 7, "name": "Marketing"}]

    requests = requests_to(mocker.request_history, WORKSPACES_PATH)
    assert len(requests) == 1
    assert requests[0].headers["Authorization"] == f"Bearer {API_KEY}"


def test_check_reports_a_rejected_api_key_as_failed_without_retrying(no_backoff_sleep):
    with requests_mock.Mocker() as mocker:
        mocker.get(WORKSPACES_URL, status_code=401, json=UNAUTHORIZED)
        status = get_source(CONFIG).check(logging.getLogger("airbyte"), CONFIG)

    assert status.status == Status.FAILED
    assert "Linkly rejected the API key" in status.message
    assert len(requests_to(mocker.request_history, WORKSPACES_PATH)) == 1


def test_read_surfaces_a_rejected_api_key_as_config_error(no_backoff_sleep):
    with requests_mock.Mocker() as mocker:
        mocker.get(WORKSPACES_URL, status_code=401, json=UNAUTHORIZED)
        output = read_stream("workspaces", expecting_exception=True)

    assert records(output) == []
    assert output.errors, "a 401 must emit an error trace"
    assert output.errors[-1].trace.error.failure_type == FailureType.config_error
    assert len(requests_to(mocker.request_history, WORKSPACES_PATH)) == 1


def test_rate_limited_requests_are_retried(no_backoff_sleep):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            WORKSPACES_URL,
            [
                {"status_code": 429, "json": {"error": "Too many requests"}},
                {"status_code": 200, "json": [{"id": 7, "name": "Marketing"}]},
            ],
        )
        output = read_stream("workspaces")

    assert records(output) == [{"id": 7, "name": "Marketing"}]
    assert not output.errors
    assert len(requests_to(mocker.request_history, WORKSPACES_PATH)) == 2


def test_links_paginate_per_workspace_and_stop_on_a_short_page(no_backoff_sleep):
    full_page = [_link(link_id, 7) for link_id in range(1, 1001)]

    with requests_mock.Mocker() as mocker:
        mocker.get(WORKSPACES_URL, json=[{"id": 7}, {"id": 9}])
        mocker.get(
            workspace_url(7, "list_links"),
            [
                {"json": _links_page(full_page, page_number=1, total_pages=2)},
                {"json": _links_page([_link(1001, 7)], page_number=2, total_pages=2)},
                # A stop condition that ignored the short page would request page 3; failing it keeps
                # that regression a fast test failure instead of a silently duplicated sync.
                {"status_code": 400, "json": {}},
            ],
        )
        mocker.get(workspace_url(9, "list_links"), json=_links_page([_link(2001, 9)], page_number=1, total_pages=1))
        output = read_stream("links")

    assert sorted(record["id"] for record in records(output)) == [*range(1, 1002), 2001]

    workspace_7 = [query_params(request) for request in requests_to(mocker.request_history, _workspace_path(7, "list_links"))]
    assert workspace_7 == [{"page": "1", "page_size": "1000"}, {"page": "2", "page_size": "1000"}]

    workspace_9 = [query_params(request) for request in requests_to(mocker.request_history, _workspace_path(9, "list_links"))]
    assert workspace_9 == [{"page": "1", "page_size": "1000"}]


def test_domains_carry_the_workspace_they_were_read_from():
    with requests_mock.Mocker() as mocker:
        mocker.get(WORKSPACES_URL, json=[{"id": 7}, {"id": 9}])
        mocker.get(workspace_url(7, "domains"), json={"domains": [{"id": 1, "name": "go.acme.com", "host": "gigalixir"}]})
        mocker.get(workspace_url(9, "domains"), json={"domains": [{"id": 2, "name": "l.acme.io", "host": "gigalixir"}]})
        output = read_stream("domains")

    by_name = {record["name"]: record for record in records(output)}
    assert by_name["go.acme.com"]["workspace_id"] == 7
    assert by_name["l.acme.io"]["workspace_id"] == 9


def _conversion(conversion_id: str, inserted_at: str) -> dict:
    return {
        "id": conversion_id,
        "link_id": 42,
        "event_type": "sale",
        "event_name": "purchase",
        "occurred_at": "2026-08-30T09:00:00.000000Z",
        "inserted_at": inserted_at,
    }


@freeze_time("2026-09-10T12:00:00Z")
def test_conversions_page_oldest_first_from_start_date_until_has_more_is_false(no_backoff_sleep):
    first_page = [
        _conversion("01K4A0000000000000000000A1", "2026-09-02T10:00:00"),
        _conversion("01K4A0000000000000000000A2", "2026-09-03T10:00:00"),
    ]
    last_page = [_conversion("01K4A0000000000000000000A3", "2026-09-04T10:00:00")]

    with requests_mock.Mocker() as mocker:
        mocker.get(WORKSPACES_URL, json=[{"id": 7}])
        mocker.get(
            CONVERSIONS_URL,
            [
                {"json": {"conversions": first_page, "has_more": True}},
                {"json": {"conversions": last_page, "has_more": False}},
                # A stop condition that ignored has_more would ask again; fail fast if it does.
                {"status_code": 400, "json": {}},
            ],
        )
        output = read_stream("conversions", sync_mode=SyncMode.incremental)

    assert [record["id"] for record in records(output)] == [c["id"] for c in first_page + last_page]
    assert all(record["workspace_id"] == 7 for record in records(output))

    requests = [query_params(request) for request in requests_to(mocker.request_history, CONVERSIONS_PATH)]
    assert requests == [
        {"workspace_id": "7", "since": "2026-09-01T00:00:00", "limit": "1000"},
        {"workspace_id": "7", "since": "2026-09-01T00:00:00", "limit": "1000", "after": "01K4A0000000000000000000A2"},
    ]


@freeze_time("2026-09-10T12:00:00Z")
def test_conversions_incremental_sync_rereads_the_hour_before_the_cursor(no_backoff_sleep):
    state = (
        StateBuilder()
        .with_stream_state(
            "conversions",
            {"states": [{"partition": {"workspace_id": 7, "parent_slice": {}}, "cursor": {"inserted_at": "2026-09-09T10:00:00"}}]},
        )
        .build()
    )

    with requests_mock.Mocker() as mocker:
        mocker.get(WORKSPACES_URL, json=[{"id": 7}])
        mocker.get(
            CONVERSIONS_URL,
            [
                {"json": {"conversions": [_conversion("01K4A0000000000000000000B1", "2026-09-09T11:00:00")], "has_more": False}},
                # Without this, a paginator that ignored has_more would loop on the same page forever.
                {"status_code": 400, "json": {}},
            ],
        )
        output = read_stream("conversions", sync_mode=SyncMode.incremental, state=state)

    assert [record["id"] for record in records(output)] == ["01K4A0000000000000000000B1"]

    requests = requests_to(mocker.request_history, CONVERSIONS_PATH)
    assert len(requests) == 1
    assert query_params(requests[0])["since"] == "2026-09-09T09:00:00", "the lookback must cover late-committed conversions"


@freeze_time("2026-09-10T12:00:00Z")
def test_clicks_first_sync_requests_the_daily_series_from_start_date_to_today():
    traffic = [
        {"t": "2026-09-01", "y": 4},
        {"t": "2026-09-02", "y": 0},
        # Buckets without a day cannot be keyed and must be dropped.
        {"t": None, "y": 5},
    ]

    with requests_mock.Mocker() as mocker:
        mocker.get(WORKSPACES_URL, json=[{"id": 7}])
        mocker.get(workspace_url(7, "clicks"), json={"traffic": traffic})
        output = read_stream("clicks", sync_mode=SyncMode.incremental)

    assert records(output) == [
        {"t": "2026-09-01", "y": 4, "workspace_id": 7},
        {"t": "2026-09-02", "y": 0, "workspace_id": 7},
    ]

    requests = requests_to(mocker.request_history, _workspace_path(7, "clicks"))
    assert len(requests) == 1
    assert query_params(requests[0]) == {"frequency": "day", "start": START_DATE, "end": "2026-09-10"}


@freeze_time("2026-09-10T12:00:00Z")
def test_clicks_incremental_sync_rereads_the_two_days_before_the_cursor():
    state = (
        StateBuilder()
        .with_stream_state(
            "clicks",
            {"states": [{"partition": {"workspace_id": 7, "parent_slice": {}}, "cursor": {"t": "2026-09-08"}}]},
        )
        .build()
    )

    with requests_mock.Mocker() as mocker:
        mocker.get(WORKSPACES_URL, json=[{"id": 7}])
        mocker.get(workspace_url(7, "clicks"), json={"traffic": [{"t": "2026-09-09", "y": 12}, {"t": "2026-09-10", "y": 3}]})
        output = read_stream("clicks", sync_mode=SyncMode.incremental, state=state)

    assert [record["t"] for record in records(output)] == ["2026-09-09", "2026-09-10"]

    requests = requests_to(mocker.request_history, _workspace_path(7, "clicks"))
    assert len(requests) == 1
    assert query_params(requests[0])["start"] == "2026-09-06", "the lookback must re-read today's still-accumulating bucket"
    assert query_params(requests[0])["end"] == "2026-09-10"
