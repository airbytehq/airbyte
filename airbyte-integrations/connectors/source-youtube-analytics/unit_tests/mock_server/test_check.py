#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Connection check and the `report_types` stream it reads.

Check reads `reportTypes.list`. It must not depend on a report stream. A report stream yields no
slices until YouTube has generated a report file for its job, so a new channel, or a deprecated
report type such as `channel_annotations_a1`, used to fail check with "no stream slices were found".

`HttpMocker` fails on any request that was not registered, so these tests also show that check
does not list or create reporting jobs.
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional

import pytest
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import AirbyteStreamStatus, Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONTENT_OWNER_ID = "content-owner-1"


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda _: None)


def _report_types_request(content_owner_id: Optional[str] = None, page_token: Optional[str] = None) -> HttpRequest:
    builder = YoutubeAnalyticsRequestBuilder("/reportTypes")
    if content_owner_id:
        builder = builder.with_on_behalf_of_content_owner(content_owner_id)
    if page_token:
        builder = builder.with_query_param("pageToken", page_token)
    return builder.build()


def _report_types_page(ids: List[str], next_page_token: Optional[str] = None) -> HttpResponse:
    body: Dict[str, Any] = {"reportTypes": [{"id": report_type_id, "name": f"Report {report_type_id}"} for report_type_id in ids]}
    if next_page_token:
        body["nextPageToken"] = next_page_token
    return HttpResponse(body=json.dumps(body))


def _register_token(http_mocker: HttpMocker) -> None:
    http_mocker.post(
        YoutubeAnalyticsRequestBuilder.token_request(),
        HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})),
    )


@pytest.mark.parametrize("content_owner_id", [None, _CONTENT_OWNER_ID], ids=["channel", "content-owner"])
def test_check_succeeds_for_a_channel_with_no_jobs_or_reports(content_owner_id: Optional[str]) -> None:
    builder = ConfigBuilder()
    if content_owner_id:
        builder = builder.with_content_owner_id(content_owner_id)
    config = builder.build()

    with HttpMocker() as http_mocker:
        _register_token(http_mocker)
        report_types_request = _report_types_request(content_owner_id)
        http_mocker.get(report_types_request, _report_types_page(["channel_basic_a3", "channel_combined_a3"]))

        status = get_source(config).check(logging.getLogger("test"), config)

        http_mocker.assert_number_of_calls(report_types_request, 1)

    assert status.status == Status.SUCCEEDED, status.message


def test_check_fails_with_config_error_message_when_report_types_are_denied() -> None:
    config = ConfigBuilder().build()

    with HttpMocker() as http_mocker:
        _register_token(http_mocker)
        http_mocker.get(
            _report_types_request(),
            HttpResponse(
                body=json.dumps({"error": {"code": 403, "message": "The caller does not have permission", "status": "PERMISSION_DENIED"}}),
                status_code=403,
            ),
        )

        status = get_source(config).check(logging.getLogger("test"), config)

    assert status.status == Status.FAILED
    assert "The YouTube Reporting API denied access: The caller does not have permission." in status.message


def test_report_types_read_follows_next_page_token() -> None:
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream("report_types", SyncMode.full_refresh).build()

    with HttpMocker() as http_mocker:
        _register_token(http_mocker)
        http_mocker.get(_report_types_request(), _report_types_page(["channel_basic_a3"], next_page_token="page-2"))
        http_mocker.get(_report_types_request(page_token="page-2"), _report_types_page(["playlist_basic_a2"]))

        output = read(get_source(config), config, catalog)

    assert output.errors == []
    assert [record.record.data["id"] for record in output.records] == ["channel_basic_a3", "playlist_basic_a2"]
    assert output.get_stream_statuses("report_types")[-1] == AirbyteStreamStatus.COMPLETE
