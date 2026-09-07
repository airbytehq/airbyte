#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import pytest
from source_github.streams import WorkflowRunAttempts, WorkflowRuns

from airbyte_cdk.models import SyncMode


_REPO_ARGS = {
    "repositories": ["org/repos"],
    "page_size_for_large_streams": 30,
    "start_date": "2022-01-01T00:00:00Z",
}

RUNS_URL = "https://api.github.com/repos/org/repos/actions/runs"

# A run that was never re-run: `previous_attempt_url` is null and the list payload is the only attempt there is.
SINGLE_ATTEMPT_RUN = {
    "id": 1,
    "url": "https://api.github.com/repos/org/repos/actions/runs/1",
    "run_attempt": 1,
    "previous_attempt_url": None,
    "logs_url": "https://api.github.com/repos/org/repos/actions/runs/1/logs",
    "jobs_url": "https://api.github.com/repos/org/repos/actions/runs/1/jobs",
    "created_at": "2022-02-01T10:00:00Z",
    "updated_at": "2022-02-01T10:05:00Z",
    "conclusion": "success",
    "repository": {"full_name": "org/repos"},
}

# A run that was re-run. The list endpoint reports the latest attempt only, and its `created_at` is the moment the
# run was first created, not the moment this attempt started.
RERUN_LIST_RECORD = {
    "id": 2,
    "url": "https://api.github.com/repos/org/repos/actions/runs/2",
    "run_attempt": 2,
    "previous_attempt_url": "https://api.github.com/repos/org/repos/actions/runs/2/attempts/1",
    "logs_url": "https://api.github.com/repos/org/repos/actions/runs/2/logs",
    "jobs_url": "https://api.github.com/repos/org/repos/actions/runs/2/jobs",
    "created_at": "2022-02-02T10:00:00Z",
    "updated_at": "2022-02-02T11:05:00Z",
    "conclusion": "success",
    "repository": {"full_name": "org/repos"},
}

RERUN_ATTEMPT_1 = {
    **RERUN_LIST_RECORD,
    "run_attempt": 1,
    "previous_attempt_url": None,
    "logs_url": "https://api.github.com/repos/org/repos/actions/runs/2/attempts/1/logs",
    "jobs_url": "https://api.github.com/repos/org/repos/actions/runs/2/attempts/1/jobs",
    "created_at": "2022-02-02T10:00:00Z",
    "updated_at": "2022-02-02T10:04:00Z",
    "conclusion": "failure",
}

RERUN_ATTEMPT_2 = {
    **RERUN_LIST_RECORD,
    "logs_url": "https://api.github.com/repos/org/repos/actions/runs/2/attempts/2/logs",
    "jobs_url": "https://api.github.com/repos/org/repos/actions/runs/2/attempts/2/jobs",
    "created_at": "2022-02-02T11:00:00Z",
    "updated_at": "2022-02-02T11:05:00Z",
}


def _stream():
    return WorkflowRunAttempts(parent=WorkflowRuns(**_REPO_ARGS), **_REPO_ARGS)


def _mock_runs(requests_mock, runs):
    requests_mock.get(RUNS_URL, json={"total_count": len(runs), "workflow_runs": runs})


def _mock_attempts(requests_mock, run_id, attempts):
    for attempt in attempts:
        requests_mock.get(f"{RUNS_URL}/{run_id}/attempts/{attempt['run_attempt']}", json=attempt)


def test_primary_key_is_composite():
    assert _stream().primary_key == ["id", "run_attempt"]


def test_run_that_was_never_rerun_costs_no_extra_request(requests_mock):
    _mock_runs(requests_mock, [SINGLE_ATTEMPT_RUN])
    stream = _stream()

    records = list(stream.read_records(sync_mode=SyncMode.incremental, stream_slice={"repository": "org/repos"}, stream_state={}))

    assert records == [
        {
            **SINGLE_ATTEMPT_RUN,
            "logs_url": "https://api.github.com/repos/org/repos/actions/runs/1/attempts/1/logs",
            "jobs_url": "https://api.github.com/repos/org/repos/actions/runs/1/attempts/1/jobs",
        }
    ]
    # Only the parent listing was fetched: no request went to the attempts endpoint.
    assert [request.path for request in requests_mock.request_history] == ["/repos/org/repos/actions/runs"]


def test_every_attempt_of_a_rerun_is_emitted(requests_mock):
    _mock_runs(requests_mock, [RERUN_LIST_RECORD])
    _mock_attempts(requests_mock, 2, [RERUN_ATTEMPT_1, RERUN_ATTEMPT_2])
    stream = _stream()

    records = list(stream.read_records(sync_mode=SyncMode.incremental, stream_slice={"repository": "org/repos"}, stream_state={}))

    assert records == [RERUN_ATTEMPT_1, RERUN_ATTEMPT_2]
    # Both attempts carry the same id and are told apart by the composite primary key alone.
    assert {record["id"] for record in records} == {2}
    assert [record["run_attempt"] for record in records] == [1, 2]
    # Each attempt reports its own start time, unlike the list record which always reports the run's.
    assert [record["created_at"] for record in records] == ["2022-02-02T10:00:00Z", "2022-02-02T11:00:00Z"]


def test_earlier_attempt_survives_an_incremental_boundary(requests_mock):
    """
    The regression this stream exists to prevent.

    A sync that lands between the first attempt finishing (10:04) and the re-run starting (11:00) leaves the cursor at
    10:04. On the next sync the run comes back because its own cursor moved to 11:05, and attempt 1 has to be emitted
    with it even though the attempt's own `updated_at` is not past the cursor.
    """
    _mock_runs(requests_mock, [RERUN_LIST_RECORD])
    _mock_attempts(requests_mock, 2, [RERUN_ATTEMPT_1, RERUN_ATTEMPT_2])
    stream = _stream()
    state = {"org/repos": {"updated_at": "2022-02-02T10:04:00Z"}}

    records = list(stream.read_records(sync_mode=SyncMode.incremental, stream_slice={"repository": "org/repos"}, stream_state=state))

    assert [record["run_attempt"] for record in records] == [1, 2]
    assert stream.state == {"org/repos": {"updated_at": "2022-02-02T11:05:00Z"}}


def test_run_not_updated_since_the_last_sync_is_skipped(requests_mock):
    _mock_runs(requests_mock, [SINGLE_ATTEMPT_RUN])
    stream = _stream()
    state = {"org/repos": {"updated_at": "2022-03-01T00:00:00Z"}}

    records = list(stream.read_records(sync_mode=SyncMode.incremental, stream_slice={"repository": "org/repos"}, stream_state=state))

    assert records == []


def test_state_tracks_the_run_cursor_not_the_attempt_cursor(requests_mock):
    _mock_runs(requests_mock, [SINGLE_ATTEMPT_RUN, RERUN_LIST_RECORD])
    _mock_attempts(requests_mock, 2, [RERUN_ATTEMPT_1, RERUN_ATTEMPT_2])
    stream = _stream()

    list(stream.read_records(sync_mode=SyncMode.incremental, stream_slice={"repository": "org/repos"}, stream_state={}))

    # 11:05 is the run's `updated_at`; attempt 1's older 10:04 must not pull the cursor back.
    assert stream.state == {"org/repos": {"updated_at": "2022-02-02T11:05:00Z"}}


@pytest.mark.parametrize(
    "run_attempt,expected_suffix",
    [pytest.param(1, "attempts/1", id="first_attempt"), pytest.param(4, "attempts/4", id="fourth_attempt")],
)
def test_derived_record_gets_attempt_scoped_urls(run_attempt, expected_suffix):
    derived = WorkflowRunAttempts._attempt_from_run({**SINGLE_ATTEMPT_RUN, "run_attempt": run_attempt})

    assert derived["logs_url"] == f"https://api.github.com/repos/org/repos/actions/runs/1/{expected_suffix}/logs"
    assert derived["jobs_url"] == f"https://api.github.com/repos/org/repos/actions/runs/1/{expected_suffix}/jobs"
    # Everything else is passed through untouched, and the source record is not mutated.
    assert derived["created_at"] == SINGLE_ATTEMPT_RUN["created_at"]
    assert SINGLE_ATTEMPT_RUN["logs_url"] == "https://api.github.com/repos/org/repos/actions/runs/1/logs"
