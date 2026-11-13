# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging

import pytest
import requests_mock
from _helpers import get_source

from airbyte_cdk.models import Status


@pytest.mark.parametrize("csv", ["date,channel_id,views\n20261101,channel-1,1\n", "date,channel_id,views\n"])
def test_check_succeeds_without_retired_annotations_job(config, csv):
    api = "https://youtubereporting.googleapis.com/v1"
    with requests_mock.Mocker() as mocker:
        mocker.post("https://oauth2.googleapis.com/token", json={"access_token": "token", "expires_in": 3600})
        mocker.get(f"{api}/jobs", json={"jobs": [{"id": "basic-job", "reportTypeId": "channel_basic_a3"}]})
        # A retired report never appears in jobs.list, even after the requester tries to create it.
        mocker.post(f"{api}/jobs", json={})
        mocker.get(
            f"{api}/jobs/basic-job/reports?createdAfter=1990-01-01T00%3A00%3A00.000000Z",
            complete_qs=True,
            json={"reports": [{"id": "report-1", "createTime": "2026-11-02T00:00:00Z", "downloadUrl": f"{api}/media/report-1"}]},
        )
        mocker.get(f"{api}/media/report-1", text=csv)

        result = get_source(config).check(logging.getLogger("test"), config)

        assert result.status == Status.SUCCEEDED, result.message
        assert [(request.method, request.path) for request in mocker.request_history] == [
            ("POST", "/token"),
            ("GET", "/v1/jobs"),
            ("POST", "/token"),
            ("GET", "/v1/jobs/basic-job/reports"),
            ("POST", "/token"),
            ("GET", "/v1/media/report-1"),
        ]
