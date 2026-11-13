#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
import logging

from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse


def test_check_succeeds_when_retired_annotations_report_has_no_reports() -> None:
    config = ConfigBuilder().build()
    source = get_source(config=config)
    stream = next(stream for stream in source.streams(config) if stream.name == "channel_basic_a3")
    properties = stream.get_json_schema()["properties"]
    dimensions = {"date": "20261110", "channel_id": "channel-1", "video_id": "video-1", "country_code": "US"}
    csv = ",".join(properties) + "\n" + ",".join(dimensions.get(column, "1") for column in properties) + "\n"

    with HttpMocker() as http_mocker:
        http_mocker.post(
            YoutubeAnalyticsRequestBuilder.token_request(),
            HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.jobs_endpoint().build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "jobs": [
                            {"id": "job-annotations", "reportTypeId": "channel_annotations_a1"},
                            {"id": "job-basic", "reportTypeId": "channel_basic_a3"},
                        ]
                    }
                )
            ),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.reports_endpoint("job-annotations").with_created_after("1990-01-01T00:00:00.000000Z").build(),
            HttpResponse(body="{}"),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.reports_endpoint("job-basic").with_created_after("1990-01-01T00:00:00.000000Z").build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "reports": [
                            {
                                "id": "report-basic",
                                "jobId": "job-basic",
                                "startTime": "2026-11-10T07:00:00Z",
                                "endTime": "2026-11-11T07:00:00Z",
                                "createTime": "2026-11-11T12:00:00Z",
                                "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url("report-basic"),
                            }
                        ]
                    }
                )
            ),
        )
        http_mocker.get(YoutubeAnalyticsRequestBuilder.download_endpoint("report-basic").build(), HttpResponse(body=csv))
        result = source.check(logging.getLogger("test"), config)

    assert result.status == Status.SUCCEEDED, result.message
