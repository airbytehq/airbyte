#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""`check` must not depend on any report file existing.

YouTube retired `channel_annotations_a1` on 2025-10-31, so its job produces no new report files,
and a job created for any report type has no files for up to two days. A check that reads a
report stream therefore fails with "no stream slices were found" both for accounts whose only
job is a retired report type and for brand-new accounts. The check reads the `report_types`
listing instead: it needs valid credentials and API access, and creates nothing in YouTube.
"""

import json
import logging

import pytest
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_REPORT_TYPES = {
    "reportTypes": [
        {"id": "channel_basic_a3", "name": "User activity"},
        {"id": "channel_annotations_a1", "name": "Annotations", "deprecateTime": "2025-10-31T00:00:00Z"},
    ]
}


def _token(http_mocker: HttpMocker) -> None:
    http_mocker.post(
        YoutubeAnalyticsRequestBuilder.token_request(),
        HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})),
    )


_NEW_JOB = {
    "jobs": [
        {"id": "job-basic", "reportTypeId": "channel_basic_a3"},
        {"id": "job-annotations", "reportTypeId": "channel_annotations_a1"},
    ]
}
_RETIRED_JOB = {"jobs": [{"id": "job-annotations", "reportTypeId": "channel_annotations_a1"}]}


@pytest.mark.parametrize(
    "jobs_pages",
    [
        # No job yet: listing is empty, the job is created, and its report list stays empty
        # until YouTube generates the first file.
        pytest.param([{}, _NEW_JOB], id="new-account-without-report-files"),
        # The only job is for a report type YouTube retired, so it lists no report files.
        pytest.param([_RETIRED_JOB], id="only-a-retired-report-job"),
    ],
)
def test_check_succeeds_before_any_report_file_exists(jobs_pages) -> None:
    config = ConfigBuilder().build()

    with HttpMocker() as http_mocker:
        _token(http_mocker)
        report_types = YoutubeAnalyticsRequestBuilder.report_types_endpoint().build()
        http_mocker.get(report_types, HttpResponse(body=json.dumps(_REPORT_TYPES)))
        # Served so that a check that reads a report stream runs to its real "no stream
        # slices" failure instead of an unmocked-request error.
        jobs = YoutubeAnalyticsRequestBuilder.jobs_endpoint().build()
        http_mocker.get(jobs, [HttpResponse(body=json.dumps(page)) for page in jobs_pages] * 3)
        for report_type in ("channel_annotations_a1", "channel_basic_a3"):
            http_mocker.post(
                HttpRequest(url=f"{YoutubeAnalyticsRequestBuilder.BASE_URL}/jobs", body=json.dumps({"name": "Airbyte reporting job", "reportTypeId": report_type})),
                HttpResponse(body=json.dumps({"id": "job-new"})),
            )
        for job_id in ("job-basic", "job-annotations"):
            http_mocker.get(
                YoutubeAnalyticsRequestBuilder.reports_endpoint(job_id).with_created_after("1990-01-01T00:00:00.000000Z").build(),
                HttpResponse(body=json.dumps({})),
            )

        status = get_source(config).check(logging.getLogger("test"), config)

        assert status.message is None
        assert status.status == Status.SUCCEEDED
        http_mocker.assert_number_of_calls(report_types, 1)


def test_check_passes_content_owner_to_report_types() -> None:
    config = ConfigBuilder().with_content_owner_id("owner-1").build()

    with HttpMocker() as http_mocker:
        _token(http_mocker)
        report_types = YoutubeAnalyticsRequestBuilder.report_types_endpoint().with_on_behalf_of_content_owner("owner-1").build()
        http_mocker.get(report_types, HttpResponse(body=json.dumps(_REPORT_TYPES)))

        status = get_source(config).check(logging.getLogger("test"), config)

        assert status.status == Status.SUCCEEDED
        http_mocker.assert_number_of_calls(report_types, 1)


def test_check_reports_no_channel_access_as_failure() -> None:
    config = ConfigBuilder().build()

    with HttpMocker() as http_mocker:
        _token(http_mocker)
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.report_types_endpoint().build(),
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
        _token(http_mocker)
        first = YoutubeAnalyticsRequestBuilder.report_types_endpoint().build()
        second = YoutubeAnalyticsRequestBuilder.report_types_endpoint().with_query_param("pageToken", "page-2").build()
        http_mocker.get(first, HttpResponse(body=json.dumps({**_REPORT_TYPES, "nextPageToken": "page-2"})))
        http_mocker.get(second, HttpResponse(body=json.dumps({"reportTypes": [{"id": "playlist_basic_a2", "name": "Playlist user activity"}]})))

        output = read(get_source(config), config, catalog)

        assert output.errors == []
        assert [record.record.data["id"] for record in output.records] == [
            "channel_basic_a3",
            "channel_annotations_a1",
            "playlist_basic_a2",
        ]
        assert output.records[1].record.data["deprecateTime"] == "2025-10-31T00:00:00Z"
        http_mocker.assert_number_of_calls(first, 1)
        http_mocker.assert_number_of_calls(second, 1)
