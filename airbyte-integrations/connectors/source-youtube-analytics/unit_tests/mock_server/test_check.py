# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging

import requests_mock
from _helpers import get_source

from airbyte_cdk.models import Status


def test_check_succeeds_when_only_supported_report_jobs_are_available(config):
    api = "https://youtubereporting.googleapis.com/v1"
    download_url = f"{api}/media/CHANNEL/report-1?alt=media"
    with requests_mock.Mocker() as mocker:
        mocker.post("https://oauth2.googleapis.com/token", json={"access_token": "token", "expires_in": 3600})
        mocker.get(f"{api}/jobs", json={"jobs": [{"id": "job-1", "reportTypeId": "channel_basic_a3"}]})
        # A creation attempt cannot make a retired report appear in subsequent listings.
        mocker.post(f"{api}/jobs", json={})
        mocker.get(
            f"{api}/jobs/job-1/reports",
            json={
                "reports": [
                    {
                        "id": "report-1",
                        "jobId": "job-1",
                        "startTime": "2026-10-01T00:00:00Z",
                        "endTime": "2026-10-02T00:00:00Z",
                        "createTime": "2026-10-03T00:00:00Z",
                        "downloadUrl": download_url,
                    }
                ]
            },
        )
        download = mocker.get(download_url, text="date,channel_id,views\n20261001,channel-1,3\n")

        status = get_source(config).check(logging.getLogger("test"), config)

    assert status.status == Status.SUCCEEDED, status.message
    assert download.called
    assert not any(request.method == "POST" and request.path == "/v1/jobs" for request in mocker.request_history)
