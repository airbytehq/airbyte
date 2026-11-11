#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
import logging
from unittest import TestCase

from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse


class TestCheck(TestCase):
    def test_check_succeeds_when_retired_annotations_job_has_no_reports(self):
        with HttpMocker() as http_mocker:
            http_mocker.post(
                YoutubeAnalyticsRequestBuilder.token_request(), HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600}))
            )
            http_mocker.get(
                YoutubeAnalyticsRequestBuilder.jobs_endpoint().build(),
                HttpResponse(
                    body=json.dumps(
                        {
                            "jobs": [
                                {"id": "annotations-job", "reportTypeId": "channel_annotations_a1"},
                                {"id": "basic-job", "reportTypeId": "channel_basic_a3"},
                            ]
                        }
                    )
                ),
            )
            http_mocker.get(
                YoutubeAnalyticsRequestBuilder.reports_endpoint("annotations-job")
                .with_created_after("1990-01-01T00:00:00.000000Z")
                .build(),
                HttpResponse(body="{}"),
            )
            http_mocker.get(
                YoutubeAnalyticsRequestBuilder.reports_endpoint("basic-job").with_created_after("1990-01-01T00:00:00.000000Z").build(),
                HttpResponse(
                    body=json.dumps(
                        {
                            "reports": [
                                {
                                    "id": "basic-report",
                                    "jobId": "basic-job",
                                    "startTime": "2026-11-08T00:00:00Z",
                                    "endTime": "2026-11-09T00:00:00Z",
                                    "createTime": "2026-11-09T00:00:00Z",
                                    "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url("basic-report"),
                                }
                            ]
                        }
                    )
                ),
            )
            http_mocker.get(
                YoutubeAnalyticsRequestBuilder.download_endpoint("basic-report").build(),
                HttpResponse(body="date,channel_id,views\n20261108,channel-1,1\n"),
            )

            config = ConfigBuilder().build()
            status = get_source(config=config).check(logging.getLogger("airbyte"), config)

            assert status.status == Status.SUCCEEDED, status
