#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""`check` must not depend on a report type YouTube has retired.

`channel_annotations_a1` was retired by YouTube on 2025-10-31: no report files are generated
for it anymore, so its listing is empty and a check against it fails with "no stream slices
were found" for every account. These tests drive the real `check` entrypoint against a
mocked YouTube Reporting API that behaves that way and assert the check succeeds by reading
the actively generated `channel_basic_a3` report.
"""

import tempfile
import time
from pathlib import Path

import pytest
import requests_mock
from _helpers import get_source

from airbyte_cdk.models import Status
from airbyte_cdk.test.entrypoint_wrapper import _run_command, make_file


_API = "https://youtubereporting.googleapis.com/v1"
_TOKEN_URL = "https://oauth2.googleapis.com/token"
_BASIC_JOB_ID = "job-basic"
_ANNOTATIONS_JOB_ID = "job-annotations"
_BASIC_REPORT_ID = "report-basic"
_BASIC_CSV = "date,channel_id,video_id,live_or_on_demand,subscribed_status,country_code,views\n20261018,channel-1,video-1,on_demand,subscribed,US,5\n"


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda _: None)


def _check(config):
    with tempfile.TemporaryDirectory() as tmp_directory:
        config_file = make_file(Path(tmp_directory) / "config.json", config)
        return _run_command(get_source(config), ["check", "--config", config_file])


def _register_basic_report(mocker: requests_mock.Mocker) -> None:
    mocker.get(
        f"{_API}/jobs/{_BASIC_JOB_ID}/reports",
        json={
            "reports": [
                {
                    "id": _BASIC_REPORT_ID,
                    "jobId": _BASIC_JOB_ID,
                    "startTime": "2026-10-18T07:00:00Z",
                    "endTime": "2026-10-19T07:00:00Z",
                    "createTime": "2026-10-20T00:00:00Z",
                    "downloadUrl": f"{_API}/media/CHANNEL/{_BASIC_REPORT_ID}?alt=media",
                }
            ]
        },
    )
    mocker.get(f"{_API}/media/CHANNEL/{_BASIC_REPORT_ID}", text=_BASIC_CSV)


def _retired_job_still_listed_without_reports(mocker: requests_mock.Mocker) -> None:
    """An account that created an annotations job before the retirement: the job is listed, but no reports are."""
    mocker.get(
        f"{_API}/jobs",
        json={
            "jobs": [
                {"id": _ANNOTATIONS_JOB_ID, "reportTypeId": "channel_annotations_a1"},
                {"id": _BASIC_JOB_ID, "reportTypeId": "channel_basic_a3"},
            ]
        },
    )
    # The API returns {} rather than {"reports": []} for an empty listing.
    mocker.get(f"{_API}/jobs/{_ANNOTATIONS_JOB_ID}/reports", json={})


def _retired_job_never_listed(mocker: requests_mock.Mocker) -> None:
    """An account with no annotations job: creating one does not make it appear in the listing."""
    mocker.get(f"{_API}/jobs", json={"jobs": [{"id": _BASIC_JOB_ID, "reportTypeId": "channel_basic_a3"}]})
    mocker.post(f"{_API}/jobs", json={})


@pytest.mark.parametrize(
    "register_jobs",
    [_retired_job_still_listed_without_reports, _retired_job_never_listed],
    ids=["retired-job-listed-without-reports", "retired-job-never-listed"],
)
def test_check_succeeds_when_retired_annotations_report_has_no_files(config, register_jobs):
    with requests_mock.Mocker() as mocker:
        mocker.post(_TOKEN_URL, json={"access_token": "token", "expires_in": 3600})
        register_jobs(mocker)
        _register_basic_report(mocker)

        output = _check(config)
        requested_paths = [request.path for request in mocker.request_history if request.method == "GET"]

    statuses = output.connection_status_messages
    assert len(statuses) == 1
    assert statuses[0].connectionStatus.status == Status.SUCCEEDED, statuses[0].connectionStatus.message
    # The check reads the actively generated channel_basic_a3 report, not the retired one.
    assert f"/v1/jobs/{_BASIC_JOB_ID}/reports" in requested_paths
    assert f"/v1/media/channel/{_BASIC_REPORT_ID}" in requested_paths
    assert f"/v1/jobs/{_ANNOTATIONS_JOB_ID}/reports" not in requested_paths
    # The basic job already exists, so the check must not create another one.
    assert not [request for request in mocker.request_history if request.method == "POST" and request.path == "/v1/jobs"]
