#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
import logging

import pytest
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


def _mock_token(http_mocker: HttpMocker) -> None:
    http_mocker.post(
        YoutubeAnalyticsRequestBuilder.token_request(),
        HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})),
    )


@pytest.mark.parametrize(
    "jobs_body",
    [
        pytest.param({}, id="no-jobs-yet"),
        pytest.param(
            {"jobs": [{"id": "job-1", "reportTypeId": "channel_annotations_a1", "name": "Airbyte reporting job"}]},
            id="job-without-reports",
        ),
    ],
)
def test_check_succeeds_before_youtube_has_generated_any_report(jobs_body) -> None:
    """A freshly authorised channel has no report files yet: YouTube takes up to 48 hours to
    generate the first one after a job is created. The check must still pass once the Reporting
    API accepts the credentials, and must not create a reporting job as a side effect."""
    config = ConfigBuilder().build()

    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        jobs_request = YoutubeAnalyticsRequestBuilder.jobs_endpoint().build()
        http_mocker.get(jobs_request, HttpResponse(body=json.dumps(jobs_body)))
        # No job-creation (POST) or report-listing mock: HttpMocker fails any unmocked request,
        # so the check must pass on the job listing alone.

        status = get_source(config).check(logging.getLogger("test"), config)

        assert status.status == Status.SUCCEEDED, status.message
        http_mocker.assert_number_of_calls(jobs_request, 1)


def test_check_fails_with_the_denied_access_message_on_403() -> None:
    config = ConfigBuilder().build()

    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.jobs_endpoint().build(),
            HttpResponse(
                body=json.dumps({"error": {"code": 403, "message": "The caller does not have permission", "status": "PERMISSION_DENIED"}}),
                status_code=403,
            ),
        )

        status = get_source(config).check(logging.getLogger("test"), config)

    assert status.status == Status.FAILED
    assert "The YouTube Reporting API denied access: The caller does not have permission." in status.message


def test_reporting_jobs_reads_every_page_of_jobs_on_behalf_of_the_content_owner() -> None:
    config = ConfigBuilder().with_content_owner_id("owner-1").build()
    catalog = CatalogBuilder().with_stream("reporting_jobs", SyncMode.full_refresh).build()
    state = StateBuilder().build()

    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.jobs_endpoint().with_on_behalf_of_content_owner("owner-1").build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "jobs": [
                            {
                                "id": "job-1",
                                "reportTypeId": "channel_basic_a3",
                                "name": "Airbyte reporting job",
                                "createTime": "2026-10-01T00:00:00Z",
                            }
                        ],
                        "nextPageToken": "page-2",
                    }
                )
            ),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.jobs_endpoint()
            .with_on_behalf_of_content_owner("owner-1")
            .with_query_param("pageToken", "page-2")
            .build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "jobs": [
                            {
                                "id": "job-2",
                                "reportTypeId": "playlist_basic_a2",
                                "name": "Another tool's job",
                                "createTime": "2026-10-02T00:00:00Z",
                            }
                        ]
                    }
                )
            ),
        )

        output = read(get_source(config=config, state=state), config=config, catalog=catalog, state=state)

    assert output.errors == []
    assert [(r.record.data["id"], r.record.data["reportTypeId"]) for r in output.records] == [
        ("job-1", "channel_basic_a3"),
        ("job-2", "playlist_basic_a2"),
    ]
