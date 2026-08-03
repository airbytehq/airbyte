#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Unit tests for the `report_types` connection-check stream.

The connection `check` used to target a report stream (e.g. `channel_basic_a3`), whose partitions
come from already-generated report files. On a fresh setup the YouTube Reporting API has not
produced any report yet, so the stream yields no slices and `CheckStream` fails with
`no stream slices were found` (airbytehq/oncall#13144). The `report_types` stream instead hits
`GET /v1/reportTypes`, which returns data with only valid OAuth credentials -- no reporting job or
generated report required. These tests assert that behavior against a mocked API.
"""

import logging

import requests_mock
from _helpers import get_source

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_REPORTING_API = "https://youtubereporting.googleapis.com/v1"


def _report_types(*ids: str, next_page_token: str | None = None) -> dict:
    body: dict = {"reportTypes": [{"id": report_id, "name": report_id} for report_id in ids]}
    if next_page_token:
        body["nextPageToken"] = next_page_token
    return body


def test_check_succeeds_via_report_types_without_reporting_job(config):
    """`check` passes using only `GET /reportTypes` and never touches the reporting `jobs` API."""
    source = get_source(config=config)

    with requests_mock.Mocker() as mocker:
        mocker.post("https://oauth2.googleapis.com/token", json={"access_token": "test_access_token", "expires_in": 3600})
        report_types_mock = mocker.get(f"{_REPORTING_API}/reportTypes", json=_report_types("channel_basic_a3", "channel_cards_a1"))

        status = source.check(logging.getLogger("test"), config)

    assert status.status == Status.SUCCEEDED
    assert report_types_mock.called
    # The fix's whole point: the check must not depend on reporting jobs / generated report data.
    assert not any("/jobs" in request.path for request in mocker.request_history)


def test_check_fails_when_report_types_is_unauthorized(config):
    """`check` reports FAILED when `GET /reportTypes` rejects the credentials."""
    source = get_source(config=config)

    with requests_mock.Mocker() as mocker:
        mocker.post("https://oauth2.googleapis.com/token", json={"access_token": "test_access_token", "expires_in": 3600})
        report_types_mock = mocker.get(
            f"{_REPORTING_API}/reportTypes",
            status_code=401,
            json={"error": {"code": 401, "message": "Invalid Credentials"}},
        )

        status = source.check(logging.getLogger("test"), config)

    assert status.status == Status.FAILED
    assert report_types_mock.called
    assert "report_types" in status.message


def test_report_types_stream_extracts_records_and_paginates(config):
    """The stream extracts records from `reportTypes` and follows `nextPageToken` via `pageToken`."""
    source = get_source(config=config)
    catalog = CatalogBuilder().with_stream("report_types", SyncMode.full_refresh).build()

    with requests_mock.Mocker() as mocker:
        mocker.post("https://oauth2.googleapis.com/token", json={"access_token": "test_access_token", "expires_in": 3600})

        # Bounded response list: a broken paginator fails an assertion instead of looping forever.
        mocker.get(
            f"{_REPORTING_API}/reportTypes",
            [
                {"json": _report_types("channel_basic_a3", "channel_cards_a1", next_page_token="page-2")},
                {"json": _report_types("channel_demographics_a1")},
            ],
        )

        output = read(source, config, catalog)

    record_ids = [record.record.data["id"] for record in output.records]
    assert record_ids == ["channel_basic_a3", "channel_cards_a1", "channel_demographics_a1"]

    report_types_requests = [r for r in mocker.request_history if r.path == "/v1/reporttypes"]
    assert len(report_types_requests) == 2, f"expected pagination to make 2 requests, got {len(report_types_requests)}"
    assert report_types_requests[1].qs.get("pagetoken") == ["page-2"]
