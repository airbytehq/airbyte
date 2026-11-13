#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Mock server tests for the connection check.

YouTube retires report types over time (`channel_annotations_a1` stopped being generated in
2025). A retired report type has no report files, and a job for it can no longer be created,
so a check that depends on one fails for every account. The check must only depend on a
report type YouTube still generates.
https://developers.google.com/youtube/reporting/revision_history
"""

import json
import logging
from typing import Any, Dict, List, Optional

import pytest
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_DEFAULT_START_TIME = "1990-01-01T00:00:00.000000Z"
_RETIRED_REPORT_TYPE = "channel_annotations_a1"
_RETIRED_JOB_ID = "job-retired"
_SUPPORTED_REPORT_TYPE = "channel_basic_a3"
_SUPPORTED_JOB_ID = "job-supported"
_REPORT_ID = "report-1"

_SUPPORTED_JOB = {"id": _SUPPORTED_JOB_ID, "reportTypeId": _SUPPORTED_REPORT_TYPE}
_RETIRED_JOB = {"id": _RETIRED_JOB_ID, "reportTypeId": _RETIRED_REPORT_TYPE}
# A string body rather than a mapping: `HttpRequest` parses every candidate request's body as
# JSON when either side is a mapping, and the form-encoded OAuth refresh request is not JSON.
_CREATE_RETIRED_JOB_REQUEST = HttpRequest(
    url=f"{YoutubeAnalyticsRequestBuilder.BASE_URL}/jobs",
    body=json.dumps({"name": "Airbyte reporting job", "reportTypeId": _RETIRED_REPORT_TYPE}),
)


@pytest.mark.parametrize(
    "jobs, create_retired_job_response",
    [
        pytest.param([_RETIRED_JOB, _SUPPORTED_JOB], None, id="retired-job-exists-but-has-no-report-files"),
        pytest.param(
            [_SUPPORTED_JOB],
            HttpResponse(
                body=json.dumps({"error": {"code": 400, "message": "Request contains an invalid argument.", "status": "INVALID_ARGUMENT"}}),
                status_code=400,
            ),
            id="retired-job-cannot-be-created",
        ),
    ],
)
def test_check_succeeds_for_an_account_whose_retired_report_type_has_no_data(
    jobs: List[Dict[str, Any]], create_retired_job_response: Optional[HttpResponse]
) -> None:
    config = ConfigBuilder().build()
    retired_reports_request = (
        YoutubeAnalyticsRequestBuilder.reports_endpoint(_RETIRED_JOB_ID).with_created_after(_DEFAULT_START_TIME).build()
    )
    supported_reports_request = (
        YoutubeAnalyticsRequestBuilder.reports_endpoint(_SUPPORTED_JOB_ID).with_created_after(_DEFAULT_START_TIME).build()
    )
    download_request = YoutubeAnalyticsRequestBuilder.download_endpoint(_REPORT_ID).build()

    with HttpMocker() as http_mocker:
        http_mocker.post(
            YoutubeAnalyticsRequestBuilder.token_request(),
            HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})),
        )
        http_mocker.get(YoutubeAnalyticsRequestBuilder.jobs_endpoint().build(), HttpResponse(body=json.dumps({"jobs": jobs})))
        if create_retired_job_response:
            http_mocker.post(_CREATE_RETIRED_JOB_REQUEST, create_retired_job_response)
        # YouTube no longer generates files for the retired report type.
        http_mocker.get(retired_reports_request, HttpResponse(body=json.dumps({})))
        http_mocker.get(
            supported_reports_request,
            HttpResponse(
                body=json.dumps(
                    {
                        "reports": [
                            {
                                "id": _REPORT_ID,
                                "jobId": _SUPPORTED_JOB_ID,
                                "startTime": "2026-10-18T07:00:00Z",
                                "endTime": "2026-10-19T07:00:00Z",
                                "createTime": "2026-10-20T00:00:00Z",
                                "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url(_REPORT_ID),
                            }
                        ]
                    }
                )
            ),
        )
        http_mocker.get(download_request, HttpResponse(body="date,channel_id,video_id,views\n20261018,channel-1,video-1,3\n"))

        status = get_source(config).check(logging.getLogger("test"), config)

        assert status.status == Status.SUCCEEDED, status.message
        # The check reads the supported report and never touches the retired one.
        http_mocker.assert_number_of_calls(supported_reports_request, 1)
        http_mocker.assert_number_of_calls(download_request, 1)
        http_mocker.assert_number_of_calls(retired_reports_request, 0)
        if create_retired_job_response:
            http_mocker.assert_number_of_calls(_CREATE_RETIRED_JOB_REQUEST, 0)
