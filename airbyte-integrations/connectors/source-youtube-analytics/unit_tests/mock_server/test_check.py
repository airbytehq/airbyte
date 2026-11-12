#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Optional

import pytest
import requests_mock
from _helpers import get_source
from mock_server.config import ConfigBuilder

from airbyte_cdk.models import Status


_API = "https://youtubereporting.googleapis.com/v1"
_TOKEN_URL = "https://oauth2.googleapis.com/token"


@pytest.mark.parametrize("job_exists", [True, False], ids=["existing-job", "new-job"])
@pytest.mark.parametrize("content_owner_id", [None, "owner-1"], ids=["channel", "content-owner"])
def test_check_uses_basic_report_when_annotations_have_no_reports(job_exists: bool, content_owner_id: Optional[str]) -> None:
    config_builder = ConfigBuilder()
    if content_owner_id:
        config_builder.with_content_owner_id(content_owner_id)
    config = config_builder.build()
    basic_job = {"id": "basic-job", "reportTypeId": "channel_basic_a3"}
    jobs = [{"id": "annotations-job", "reportTypeId": "channel_annotations_a1"}]
    if job_exists:
        jobs.append(basic_job)

    def create_job(request, context):
        jobs.append(basic_job)
        return basic_job

    with requests_mock.Mocker(case_sensitive=True) as mocker:
        mocker.post(_TOKEN_URL, json={"access_token": "token", "expires_in": 3600})
        mocker.get(f"{_API}/jobs", json=lambda request, context: {"jobs": jobs})
        mocker.post(f"{_API}/jobs", json=create_job)
        mocker.get(f"{_API}/jobs/annotations-job/reports", json={})
        mocker.get(
            f"{_API}/jobs/basic-job/reports",
            json={
                "reports": [
                    {
                        "id": "basic-report",
                        "jobId": "basic-job",
                        "startTime": "2026-10-18T07:00:00Z",
                        "endTime": "2026-10-19T07:00:00Z",
                        "createTime": "2026-10-20T00:00:00Z",
                        "downloadUrl": f"{_API}/media/CHANNEL/basic-report?alt=media",
                    }
                ]
            },
        )
        mocker.get(
            f"{_API}/media/CHANNEL/basic-report",
            text="date,channel_id,video_id,views\n20261018,channel-1,video-1,42\n",
        )

        status = get_source(config).check(logging.getLogger("test"), config)

    assert status.status == Status.SUCCEEDED, status.message
    owner_params = {"onBehalfOfContentOwner": [content_owner_id]} if content_owner_id else {}
    jobs_request = ("GET", "/v1/jobs", owner_params)
    expected_requests = [jobs_request]
    if not job_exists:
        expected_requests += [("POST", "/v1/jobs", {}), jobs_request]
    expected_requests += [
        ("GET", "/v1/jobs/basic-job/reports", {**owner_params, "createdAfter": ["1990-01-01T00:00:00.000000Z"]}),
        ("GET", "/v1/media/CHANNEL/basic-report", {**owner_params, "alt": ["media"]}),
    ]
    assert [
        (request.method, request.path, request.qs) for request in mocker.request_history if request.path.startswith("/v1/")
    ] == expected_requests
    job_creations = [request.json() for request in mocker.request_history if request.method == "POST" and request.path == "/v1/jobs"]
    assert job_creations == ([] if job_exists else [{"name": "Airbyte reporting job", "reportTypeId": "channel_basic_a3"}])
