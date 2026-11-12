#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Connection check and the `report_types` stream it reads.

`HttpMocker` fails a test on any request that is not registered, so a check that still listed
jobs, created a job, or listed report files would fail here.
"""

import json
import logging
from typing import Any, Dict, Optional

import pytest
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse


_STREAM = "report_types"
_TOKEN_RESPONSE = HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600}))


def _report_type(report_type_id: str, **extra: Any) -> Dict[str, Any]:
    return {"id": report_type_id, "name": f"Report {report_type_id}", **extra}


def _report_types_request(content_owner_id: Optional[str] = None, page_token: Optional[str] = None):
    builder = YoutubeAnalyticsRequestBuilder.report_types_endpoint()
    if content_owner_id:
        builder = builder.with_on_behalf_of_content_owner(content_owner_id)
    if page_token:
        builder = builder.with_page_token(page_token)
    return builder.build()


@pytest.mark.parametrize("content_owner_id", [None, "owner-1"], ids=["channel", "content-owner"])
def test_check_succeeds_for_an_account_with_no_reporting_jobs_or_report_files(content_owner_id: Optional[str]) -> None:
    """A new account has no jobs and no report files; check must pass without listing or creating either."""
    builder = ConfigBuilder()
    if content_owner_id:
        builder = builder.with_content_owner_id(content_owner_id)
    config = builder.build()

    with HttpMocker() as http_mocker:
        http_mocker.post(YoutubeAnalyticsRequestBuilder.token_request(), _TOKEN_RESPONSE)
        http_mocker.get(
            _report_types_request(content_owner_id),
            HttpResponse(body=json.dumps({"reportTypes": [_report_type("channel_basic_a3")]})),
        )

        status = get_source(config).check(logging.getLogger("test"), config)

    assert status.status == Status.SUCCEEDED
    assert status.message is None


def test_check_fails_with_the_no_channel_message_when_the_account_has_no_channel() -> None:
    config = ConfigBuilder().build()

    with HttpMocker() as http_mocker:
        http_mocker.post(YoutubeAnalyticsRequestBuilder.token_request(), _TOKEN_RESPONSE)
        http_mocker.get(
            _report_types_request(),
            HttpResponse(body=json.dumps({"error": {"code": 401, "message": "Unauthorized", "status": "UNAUTHENTICATED"}}), status_code=401),
        )

        status = get_source(config).check(logging.getLogger("test"), config)

    assert status.status == Status.FAILED
    assert "The authorized Google account does not appear to have an associated YouTube channel." in status.message


def test_report_types_read_follows_next_page_token() -> None:
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream(_STREAM, SyncMode.full_refresh).build()
    deprecated = _report_type("channel_basic_a2", deprecateTime="2025-10-31T07:00:00Z", systemManaged=False)

    with HttpMocker() as http_mocker:
        http_mocker.post(YoutubeAnalyticsRequestBuilder.token_request(), _TOKEN_RESPONSE)
        http_mocker.get(
            _report_types_request(),
            HttpResponse(body=json.dumps({"reportTypes": [_report_type("channel_basic_a3")], "nextPageToken": "page-2"})),
        )
        http_mocker.get(
            _report_types_request(page_token="page-2"),
            HttpResponse(body=json.dumps({"reportTypes": [deprecated]})),
        )

        output = read(get_source(config), config, catalog)

    assert output.errors == []
    assert [record.record.data for record in output.records] == [_report_type("channel_basic_a3"), deprecated]
