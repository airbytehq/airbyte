# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Tests for the `report_types` stream and the `check` that reads it.

`check` must work for an account whose reporting jobs have not produced report files yet:
YouTube generates the first report file for a new reporting job up to 48 hours after the job is
created, so a check that reads a report stream finds no report to read on a new setup.
"""

import logging
import time

import pytest
import requests_mock
from _helpers import get_source

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_API = "https://youtubereporting.googleapis.com/v1"
_TOKEN_URL = "https://oauth2.googleapis.com/token"
_CONTENT_OWNER_ID = "content-owner-1"


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda _: None)


def _register_new_account(mocker: requests_mock.Mocker) -> None:
    """An account with no Airbyte reporting jobs: any job created now has no report files yet."""
    mocker.post(_TOKEN_URL, json={"access_token": "token", "expires_in": 3600})
    mocker.get(
        f"{_API}/reportTypes",
        json={"reportTypes": [{"id": "channel_basic_a3", "name": "User activity"}]},
    )
    listings = iter([{}, {"jobs": [{"id": "new-job", "reportTypeId": "channel_annotations_a1"}]}])
    mocker.get(f"{_API}/jobs", json=lambda request, context: next(listings, {}))
    mocker.post(f"{_API}/jobs", json={"id": "new-job"})
    mocker.get(f"{_API}/jobs/new-job/reports", json={})


@pytest.mark.parametrize(
    "content_owner_id, expected_query",
    [(None, {}), (_CONTENT_OWNER_ID, {"onbehalfofcontentowner": [_CONTENT_OWNER_ID]})],
    ids=["channel", "content-owner"],
)
def test_check_succeeds_for_a_new_account_without_creating_a_reporting_job(config, content_owner_id, expected_query):
    if content_owner_id:
        config = {**config, "content_owner_id": content_owner_id}
    with requests_mock.Mocker() as mocker:
        _register_new_account(mocker)

        status = get_source(config).check(logging.getLogger("test"), config)
        api_requests = [(r.method, r.path, r.qs) for r in mocker.request_history if r.hostname == "youtubereporting.googleapis.com"]

    assert status.status == Status.SUCCEEDED, status.message
    assert api_requests == [("GET", "/v1/reporttypes", expected_query)]


@pytest.mark.parametrize(
    "status_code, body, expected_message",
    [
        (401, {"error": {"code": 401, "message": "Unauthorized"}}, "does not appear to have an associated YouTube channel"),
        (
            403,
            {"error": {"code": 403, "message": "The caller does not have permission"}},
            "The YouTube Reporting API denied access: The caller does not have permission.",
        ),
    ],
    ids=["no-channel", "forbidden"],
)
def test_check_reports_why_the_account_cannot_use_the_reporting_api(config, status_code, body, expected_message):
    with requests_mock.Mocker() as mocker:
        mocker.post(_TOKEN_URL, json={"access_token": "token", "expires_in": 3600})
        mocker.get(f"{_API}/reportTypes", status_code=status_code, json=body)
        mocker.get(f"{_API}/jobs", status_code=status_code, json=body)

        status = get_source(config).check(logging.getLogger("test"), config)

    assert status.status == Status.FAILED
    assert expected_message in status.message


def test_report_types_read_follows_next_page_token(config):
    pages = {
        None: {"reportTypes": [{"id": "channel_basic_a3", "name": "User activity"}], "nextPageToken": "page-2"},
        "page-2": {"reportTypes": [{"id": "playlist_basic_a2", "name": "Playlist user activity", "deprecateTime": "2027-01-01T00:00:00Z"}]},
    }
    with requests_mock.Mocker() as mocker:
        mocker.post(_TOKEN_URL, json={"access_token": "token", "expires_in": 3600})
        mocker.get(f"{_API}/reportTypes", json=lambda request, context: pages[request.qs.get("pagetoken", [None])[0]])

        catalog = CatalogBuilder().with_stream("report_types", SyncMode.full_refresh).build()
        output = read(get_source(config), config, catalog)
        tokens = [r.qs.get("pagetoken", [None])[0] for r in mocker.request_history if r.path == "/v1/reporttypes"]

    assert output.errors == []
    assert [record.record.data for record in output.records] == pages[None]["reportTypes"] + pages["page-2"]["reportTypes"]
    assert tokens == [None, "page-2"]
