#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""The connection check and the `report_types` stream it reads.

`HttpMocker` fails any request that has no mock, so a check that still reached `/jobs` or a
report listing (as it did while it read a report stream) fails these tests.
"""

import json
import logging
from typing import Optional

import pytest
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import AirbyteStreamStatus, Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse


_STREAM = "report_types"
_CONTENT_OWNER_ID = "content-owner-1"


def _mock_token(http_mocker: HttpMocker) -> None:
    http_mocker.post(
        YoutubeAnalyticsRequestBuilder.token_request(),
        HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})),
    )


def _report_types_request(content_owner_id: Optional[str] = None, page_token: Optional[str] = None):
    builder = YoutubeAnalyticsRequestBuilder.report_types_endpoint()
    if content_owner_id:
        builder = builder.with_on_behalf_of_content_owner(content_owner_id)
    if page_token:
        builder = builder.with_query_param("pageToken", page_token)
    return builder.build()


def _config(content_owner_id: Optional[str]):
    builder = ConfigBuilder()
    if content_owner_id:
        builder = builder.with_content_owner_id(content_owner_id)
    return builder.build()


@pytest.mark.parametrize("content_owner_id", [None, _CONTENT_OWNER_ID], ids=["channel", "content-owner"])
def test_check_succeeds_for_an_account_with_no_reporting_jobs_or_report_files(content_owner_id: Optional[str]) -> None:
    """A new account has no jobs and no report files; the check must pass and must not create a job."""
    config = _config(content_owner_id)
    request = _report_types_request(content_owner_id)

    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        http_mocker.get(
            request,
            HttpResponse(body=json.dumps({"reportTypes": [{"id": "channel_basic_a3", "name": "User activity"}]})),
        )
        status = get_source(config).check(logging.getLogger("test"), config)
        http_mocker.assert_number_of_calls(request, 1)

    assert status.status == Status.SUCCEEDED
    assert status.message is None


@pytest.mark.parametrize(
    "status_code, body, expected_message",
    [
        pytest.param(
            401,
            {"error": {"code": 401, "message": "Unauthorized", "status": "UNAUTHENTICATED"}},
            "The authorized Google account does not appear to have an associated YouTube channel.",
            id="401-no-channel",
        ),
        pytest.param(
            403,
            {"error": {"code": 403, "message": "The caller does not have permission", "status": "PERMISSION_DENIED"}},
            "The YouTube Reporting API denied access: The caller does not have permission.",
            id="403-denied",
        ),
    ],
)
def test_check_fails_with_the_connector_message_when_youtube_rejects_the_account(status_code, body, expected_message) -> None:
    config = _config(None)
    request = _report_types_request()

    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        http_mocker.get(request, HttpResponse(body=json.dumps(body), status_code=status_code))
        status = get_source(config).check(logging.getLogger("test"), config)
        # Both filters are `action: FAIL`, so the request is not retried.
        http_mocker.assert_number_of_calls(request, 1)

    assert status.status == Status.FAILED
    # The CDK passes the reason through `repr`, hence the leading quote.
    assert status.message.startswith(f"'Stream {_STREAM} is not available: {expected_message}")


@pytest.mark.parametrize("content_owner_id", [None, _CONTENT_OWNER_ID], ids=["channel", "content-owner"])
def test_read_follows_next_page_token_and_emits_every_report_type(content_owner_id: Optional[str]) -> None:
    config = _config(content_owner_id)
    catalog = CatalogBuilder().with_stream(_STREAM, SyncMode.full_refresh).build()
    first_page = _report_types_request(content_owner_id)
    second_page = _report_types_request(content_owner_id, page_token="page-2")

    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        http_mocker.get(
            first_page,
            HttpResponse(
                body=json.dumps(
                    {
                        "reportTypes": [
                            {"id": "channel_basic_a3", "name": "User activity"},
                            {"id": "channel_basic_a2", "name": "User activity", "deprecateTime": "2025-10-31T07:00:00Z"},
                        ],
                        "nextPageToken": "page-2",
                    }
                )
            ),
        )
        http_mocker.get(
            second_page,
            HttpResponse(body=json.dumps({"reportTypes": [{"id": "playlist_basic_a2", "name": "Playlist user activity"}]})),
        )
        output = read(get_source(config), config=config, catalog=catalog)
        http_mocker.assert_number_of_calls(first_page, 1)
        http_mocker.assert_number_of_calls(second_page, 1)

    assert output.errors == []
    assert [record.record.data for record in output.records] == [
        {"id": "channel_basic_a3", "name": "User activity"},
        {"id": "channel_basic_a2", "name": "User activity", "deprecateTime": "2025-10-31T07:00:00Z"},
        {"id": "playlist_basic_a2", "name": "Playlist user activity"},
    ]
    assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE
