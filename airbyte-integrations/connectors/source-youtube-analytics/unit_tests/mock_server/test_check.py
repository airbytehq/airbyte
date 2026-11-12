# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging

import requests_mock
from _helpers import get_source

from airbyte_cdk.models import Status


_API = "https://youtubereporting.googleapis.com/v1"


def test_check_succeeds_without_retired_annotations_report(config):
    with requests_mock.Mocker() as mocker:
        mocker.post("https://oauth2.googleapis.com/token", json={"access_token": "token", "expires_in": 3600})
        mocker.get(
            f"{_API}/jobs",
            json={
                "jobs": [
                    {"id": "basic-job", "reportTypeId": "channel_basic_a3"},
                    {"id": "combined-job", "reportTypeId": "channel_combined_a3"},
                ]
            },
        )
        create_annotations = mocker.post(
            f"{_API}/jobs",
            additional_matcher=lambda request: request.json()["reportTypeId"] == "channel_annotations_a1",
            status_code=400,
            json={"error": {"code": 400, "status": "INVALID_ARGUMENT", "message": "Unsupported report type: channel_annotations_a1"}},
        )
        reports = mocker.get(
            f"{_API}/jobs/basic-job/reports",
            json={
                "reports": [
                    {
                        "id": "report-1",
                        "jobId": "basic-job",
                        "startTime": "2026-11-09T00:00:00Z",
                        "endTime": "2026-11-10T00:00:00Z",
                        "createTime": "2026-11-10T01:00:00Z",
                        "downloadUrl": f"{_API}/media/CHANNEL/report-1?alt=media",
                    }
                ]
            },
        )
        mocker.get(f"{_API}/media/CHANNEL/report-1?alt=media", text="date,channel_id,views\n20261109,channel-1,3\n")

        status = get_source(config).check(logging.getLogger("test"), config)

    assert status.status == Status.SUCCEEDED, status.message
    assert reports.called
    assert not create_annotations.called
