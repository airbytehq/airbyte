# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging

import requests_mock
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.models import Status, Type


def test_check_succeeds_when_only_supported_basic_report_job_exists():
    config = ConfigBuilder().build()
    source = get_source(config)
    api = YoutubeAnalyticsRequestBuilder.BASE_URL
    job_id = "job-channel-basic-a3"
    download_url = YoutubeAnalyticsRequestBuilder.download_url("report-basic")

    with requests_mock.Mocker() as mocker:
        mocker.post(YoutubeAnalyticsRequestBuilder.TOKEN_URL, json={"access_token": "token", "expires_in": 3600})
        mocker.get(f"{api}/jobs", json={"jobs": [{"id": job_id, "reportTypeId": "channel_basic_a3"}]})
        mocker.post(f"{api}/jobs", json={})
        reports = mocker.get(
            f"{api}/jobs/{job_id}/reports",
            json={
                "reports": [
                    {
                        "id": "report-basic",
                        "jobId": job_id,
                        "startTime": "2026-11-01T07:00:00Z",
                        "endTime": "2026-11-02T08:00:00Z",
                        "createTime": "2026-11-03T00:00:00Z",
                        "downloadUrl": download_url,
                    }
                ]
            },
        )
        mocker.get(download_url, text="date,channel_id,views\n20261101,channel-1,1\n")

        messages = list(AirbyteEntrypoint(source).check(source.spec(logging.getLogger("test")), config))

    status = next(message.connectionStatus for message in messages if message.type == Type.CONNECTION_STATUS)
    assert status.status == Status.SUCCEEDED, status.message
    assert reports.called
