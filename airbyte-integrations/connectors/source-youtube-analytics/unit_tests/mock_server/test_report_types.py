#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Mock server tests for the connection check and the `report_types` stream it reads.

The check lists report types (`reportTypes.list`) instead of reading a report stream. A report
stream has nothing to read until YouTube has generated a report file for its job, which takes
up to 48 hours after the job is created, so a check against one fails every new setup.
https://developers.google.com/youtube/reporting/v1/reference/rest/v1/reportTypes/list
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
_BASIC = {"id": "channel_basic_a3", "name": "User activity"}
_RETIRED = {"id": "channel_annotations_a1", "name": "Annotations", "deprecateTime": "2025-10-31T07:00:00Z"}
_SYSTEM_MANAGED = {"id": "content_owner_estimated_revenue_a1", "name": "Estimated revenue", "systemManaged": True}


def _given_token(http_mocker: HttpMocker) -> None:
    http_mocker.post(
        YoutubeAnalyticsRequestBuilder.token_request(), HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600}))
    )


def _check(config: Dict[str, Any]):
    return get_source(config=config).check(logging.getLogger("test"), config)


@pytest.mark.parametrize(
    "content_owner_id, report_types_body",
    [
        pytest.param(None, {"reportTypes": [_BASIC]}, id="channel"),
        pytest.param("owner-1", {"reportTypes": [_BASIC]}, id="content-owner"),
        # The API omits `reportTypes` rather than returning an empty list.
        pytest.param(None, {}, id="no-report-types-listed"),
    ],
)
def test_check_succeeds_for_an_account_with_no_reporting_jobs_or_report_files(
    content_owner_id: Optional[str], report_types_body: Dict[str, Any]
) -> None:
    """A new account has no jobs and no report files; the check must pass on valid credentials alone.

    Only the token and `reportTypes` endpoints are mocked, and `HttpMocker` rejects any other
    request, so this also pins that the check neither lists nor creates reporting jobs.
    """
    builder = ConfigBuilder()
    request = YoutubeAnalyticsRequestBuilder.report_types_endpoint()
    if content_owner_id:
        builder = builder.with_content_owner_id(content_owner_id)
        request = request.with_on_behalf_of_content_owner(content_owner_id)

    with HttpMocker() as http_mocker:
        _given_token(http_mocker)
        http_mocker.get(request.build(), HttpResponse(body=json.dumps(report_types_body)))
        status = _check(builder.build())

    assert status.status == Status.SUCCEEDED
    assert status.message is None


@pytest.mark.parametrize(
    "status_code, vendor_message, expected_message",
    [
        pytest.param(
            401,
            "Unauthorized",
            "The authorized Google account does not appear to have an associated YouTube channel.",
            id="401-no-channel",
        ),
        pytest.param(
            403,
            "The caller does not have permission",
            "The YouTube Reporting API denied access: The caller does not have permission.",
            id="403-denied",
        ),
    ],
)
def test_check_fails_with_the_actionable_message_when_the_api_rejects_the_account(
    status_code: int, vendor_message: str, expected_message: str
) -> None:
    with HttpMocker() as http_mocker:
        _given_token(http_mocker)
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.report_types_endpoint().build(),
            HttpResponse(body=json.dumps({"error": {"code": status_code, "message": vendor_message}}), status_code=status_code),
        )
        status = _check(ConfigBuilder().build())

    assert status.status == Status.FAILED
    assert expected_message in status.message


def test_report_types_reads_every_page_and_records_match_the_discovered_schema() -> None:
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream(_STREAM, SyncMode.full_refresh).build()

    with HttpMocker() as http_mocker:
        _given_token(http_mocker)
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.report_types_endpoint().build(),
            HttpResponse(body=json.dumps({"reportTypes": [_BASIC, _RETIRED], "nextPageToken": "page-2"})),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.report_types_endpoint().with_page_token("page-2").build(),
            HttpResponse(body=json.dumps({"reportTypes": [_SYSTEM_MANAGED]})),
        )
        output = read(get_source(config=config), config=config, catalog=catalog)

    assert output.errors == []
    assert [record.record.data for record in output.records] == [_BASIC, _RETIRED, _SYSTEM_MANAGED]

    discovered = {stream.name: stream for stream in get_source(config=config).discover(logging.getLogger("test"), config).streams}[_STREAM]
    assert discovered.source_defined_primary_key == [["id"]]
    assert discovered.supported_sync_modes == [SyncMode.full_refresh]
    properties = discovered.json_schema["properties"]
    json_types = {"string": str, "boolean": bool}
    for record in output.records:
        for field, value in record.record.data.items():
            # Every emitted field is declared, with a value of the declared type.
            declared = properties[field]["type"]
            declared = declared if isinstance(declared, list) else [declared]
            assert any(isinstance(value, json_types[name]) for name in declared if name != "null"), (field, value)
    assert properties["deprecateTime"]["format"] == "date-time"
