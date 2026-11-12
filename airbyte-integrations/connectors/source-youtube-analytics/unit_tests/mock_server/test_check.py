#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Connection check against a mocked YouTube Reporting API.

Setting up a source must not depend on YouTube having generated a report file for any one report
type: a new account has no reporting jobs, a new job has no files for up to 48 hours, and a job
for a report type YouTube has retired never gets one.
"""

import logging
from typing import Any, Dict

import pytest
import requests_mock
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_API = YoutubeAnalyticsRequestBuilder.BASE_URL
_JOBS = [
    {"id": "job-1", "reportTypeId": "channel_annotations_a1", "name": "Airbyte reporting job", "createTime": "2026-10-01T00:00:00Z"},
    {"id": "job-2", "reportTypeId": "channel_basic_a3", "name": "Airbyte reporting job", "createTime": "2026-10-02T00:00:00Z"},
]


def _register_api(mocker: requests_mock.Mocker, jobs_body: Dict[str, Any]) -> None:
    mocker.post(YoutubeAnalyticsRequestBuilder.TOKEN_URL, json={"access_token": "token", "expires_in": 3600})
    mocker.get(f"{_API}/jobs", json=jobs_body)
    # A job was created (or would be), but YouTube has no report file for it.
    mocker.post(f"{_API}/jobs", json={"id": "job-new"})
    mocker.get(requests_mock.ANY, json={})


def _api_calls(mocker: requests_mock.Mocker) -> list:
    return [(request.method, request.path) for request in mocker.request_history if request.hostname == "youtubereporting.googleapis.com"]


@pytest.mark.parametrize(
    "jobs_body",
    [
        pytest.param({}, id="new-account-without-reporting-jobs"),
        pytest.param({"jobs": _JOBS}, id="jobs-exist-but-no-report-files-yet"),
    ],
)
def test_check_succeeds_without_any_report_file_and_creates_no_job(jobs_body: Dict[str, Any]) -> None:
    config = ConfigBuilder().build()

    with requests_mock.Mocker() as mocker:
        _register_api(mocker, jobs_body)
        status = get_source(config).check(logging.getLogger("test"), config)
        api_calls = _api_calls(mocker)

    assert status.status == Status.SUCCEEDED, status.message
    # One listing call: the check neither creates a reporting job nor looks for report files.
    assert api_calls == [("GET", "/v1/jobs")]


def test_reporting_jobs_stream_follows_pagination_and_sends_content_owner() -> None:
    config = ConfigBuilder().with_content_owner_id("owner-1").build()
    catalog = CatalogBuilder().with_stream("reporting_jobs", SyncMode.full_refresh).build()

    def jobs_page(request, context):
        token = request.qs.get("pagetoken", [None])[0]
        if token is None:
            return {"jobs": _JOBS[:1], "nextPageToken": "page-2"}
        assert token == "page-2"
        return {"jobs": _JOBS[1:]}

    with requests_mock.Mocker() as mocker:
        mocker.post(YoutubeAnalyticsRequestBuilder.TOKEN_URL, json={"access_token": "token", "expires_in": 3600})
        mocker.get(f"{_API}/jobs", json=jobs_page)
        output = read(get_source(config), config, catalog)
        requests = [request for request in mocker.request_history if request.path == "/v1/jobs"]

    assert output.errors == []
    assert [record.record.data for record in output.records] == _JOBS
    # `requests_mock` lower-cases query strings.
    assert [(request.method, request.qs) for request in requests] == [
        ("GET", {"onbehalfofcontentowner": ["owner-1"]}),
        ("GET", {"onbehalfofcontentowner": ["owner-1"], "pagetoken": ["page-2"]}),
    ]
