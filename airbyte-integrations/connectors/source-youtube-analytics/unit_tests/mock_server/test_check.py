# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""`check` against a mocked YouTube Reporting API."""

import logging

import requests_mock
from _helpers import get_source

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_API = "https://youtubereporting.googleapis.com/v1"
_TOKEN_URL = "https://oauth2.googleapis.com/token"


def _check(config, mocker: requests_mock.Mocker):
    mocker.post(_TOKEN_URL, json={"access_token": "token", "expires_in": 3600})
    return get_source(config).check(logging.getLogger("test"), config)


def test_check_succeeds_for_a_channel_with_no_report_files_yet(config):
    """A first-time user has no reporting jobs and no report files; the check must still pass and create no job."""
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/jobs", json={})
        mocker.post(f"{_API}/jobs", json={"id": "job-1"})
        mocker.get(requests_mock.ANY, json={})
        report_types = mocker.get(
            f"{_API}/reportTypes",
            json={"reportTypes": [{"id": "channel_basic_a3", "name": "User activity"}]},
        )

        status = _check(config, mocker)
        history = mocker.request_history

    assert status.status == Status.SUCCEEDED, status.message
    assert report_types.call_count == 1
    assert [(r.method, r.path) for r in history if r.hostname == "youtubereporting.googleapis.com"] == [("GET", "/v1/reporttypes")]


def test_check_passes_on_behalf_of_content_owner(config):
    config = {**config, "content_owner_id": "owner-1"}
    with requests_mock.Mocker() as mocker:
        report_types = mocker.get(f"{_API}/reportTypes", json={"reportTypes": [{"id": "channel_basic_a3"}]})

        status = _check(config, mocker)

    assert status.status == Status.SUCCEEDED, status.message
    assert report_types.last_request.qs == {"onbehalfofcontentowner": ["owner-1"]}


def test_check_fails_as_config_error_when_the_account_has_no_channel(config):
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/reportTypes", status_code=401, json={"error": {"code": 401, "message": "Unauthorized"}})

        status = _check(config, mocker)

    assert status.status == Status.FAILED
    assert "YouTube channel" in status.message


def test_report_types_stream_reads_every_page(config):
    pages = {
        None: {"reportTypes": [{"id": "channel_basic_a3", "name": "User activity"}], "nextPageToken": "page-2"},
        "page-2": {"reportTypes": [{"id": "playlist_basic_a2", "name": "Playlist user activity", "systemManaged": False}]},
    }

    def callback(request, context):
        return pages[request.qs.get("pagetoken", [None])[0]]

    with requests_mock.Mocker() as mocker:
        mocker.post(_TOKEN_URL, json={"access_token": "token", "expires_in": 3600})
        report_types = mocker.get(f"{_API}/reportTypes", json=callback)
        catalog = CatalogBuilder().with_stream("report_types", SyncMode.full_refresh).build()

        output = read(get_source(config), config, catalog)
        page_tokens = [request.qs.get("pagetoken", [None])[0] for request in report_types.request_history]

    assert not output.errors
    assert [record.record.data["id"] for record in output.records] == ["channel_basic_a3", "playlist_basic_a2"]
    assert page_tokens == [None, "page-2"]
