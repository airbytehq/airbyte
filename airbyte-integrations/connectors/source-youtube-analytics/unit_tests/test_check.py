# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for the connection `check` of `source-youtube-analytics`.

The connector's `check` block uses `CheckStream`, which verifies availability by generating
the first partition of the configured stream. Availability for a report stream requires the
YouTube Reporting API to have (or be able to create) a reporting job for that stream's
`reportTypeId`.

The report type `channel_annotations_a1` was retired by the YouTube Reporting API, so a job
can no longer be found or created for it. When `check` targeted `channel_annotations_a1`, no
partitions could be generated and setup failed with "no stream slices were found" (oncall
#13144). These tests assert that `check` targets a currently-supported report type and
succeeds, and that it does not depend on the deprecated `channel_annotations_a1` job.
"""

import logging

import requests_mock
from _helpers import get_source


_CONFIG = {
    "credentials": {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "refresh_token": "test_refresh_token",
    },
}

_TOKEN_URL = "https://oauth2.googleapis.com/token"
_JOBS_URL = "https://youtubereporting.googleapis.com/v1/jobs"
_REPORTS_URL = "https://youtubereporting.googleapis.com/v1/jobs/job-basic/reports"
_DOWNLOAD_URL = "https://youtubereporting.example/download/rep1"

# Report type the check stream is expected to use after the fix. `channel_annotations_a1`
# is deprecated and no reporting job exists for it, so it is intentionally absent from the
# mocked jobs list below.
_SUPPORTED_REPORT_TYPE = "channel_basic_a3"
_DEPRECATED_REPORT_TYPE = "channel_annotations_a1"


def _register_common_mocks(mocker: requests_mock.Mocker) -> None:
    mocker.post(_TOKEN_URL, json={"access_token": "test_token", "expires_in": 3600})
    # The Reporting API only has a job for the supported report type; the deprecated
    # report type has no job.
    mocker.get(_JOBS_URL, json={"jobs": [{"id": "job-basic", "reportTypeId": _SUPPORTED_REPORT_TYPE}]})
    # Creating a job for a retired report type fails with a 400, mirroring the real API.
    mocker.post(
        _JOBS_URL,
        status_code=400,
        json={"error": {"code": 400, "message": f"{_DEPRECATED_REPORT_TYPE} is not a valid reportTypeId"}},
    )
    mocker.get(
        _REPORTS_URL,
        json={
            "reports": [
                {
                    "id": "rep1",
                    "startTime": "2020-01-01T00:00:00.000000Z",
                    "createTime": "2020-01-02T00:00:00.000000Z",
                    "downloadUrl": _DOWNLOAD_URL,
                }
            ]
        },
    )
    mocker.get(_DOWNLOAD_URL, text="date,channel_id\n20200101,channel-1\n")


def test_check_succeeds_with_supported_report_type():
    """`check` succeeds when it targets a currently-supported report type."""
    source = get_source(config=_CONFIG)
    with requests_mock.Mocker() as mocker:
        _register_common_mocks(mocker)
        status = source.check(logging.getLogger("test"), _CONFIG)

    assert status.status.value == "SUCCEEDED", status.message


def test_check_does_not_use_deprecated_annotations_stream():
    """`check` must not depend on the retired `channel_annotations_a1` job.

    If the check stream were `channel_annotations_a1`, the connector would attempt to create a
    job for it (the deprecated report type is absent from the jobs list) and the mocked API
    would reject that with a 400, causing the check to fail.
    """
    source = get_source(config=_CONFIG)
    with requests_mock.Mocker() as mocker:
        _register_common_mocks(mocker)
        source.check(logging.getLogger("test"), _CONFIG)
        create_job_attempts = [req for req in mocker.request_history if req.method == "POST" and req.url.rstrip("/") == _JOBS_URL]

    assert create_job_attempts == [], (
        "check attempted to create a reporting job, which happens only when no job exists for the "
        "target report type (e.g. the deprecated channel_annotations_a1)"
    )
