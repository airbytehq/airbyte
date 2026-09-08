#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import logging

import pytest
from source_github.source import SourceGithub

from airbyte_cdk.models import (
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStream,
    AirbyteStreamState,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    StreamDescriptor,
    SyncMode,
    Type,
)


CONFIG = {
    "credentials": {"personal_access_token": "token"},
    "repositories": ["org/repos"],
    "start_date": "2022-01-01T00:00:00Z",
}

REPO_URL = "https://api.github.com/repos/org/repos"
RUNS_URL = f"{REPO_URL}/actions/runs"


def _run(run_id, run_attempt=1, updated_at="2022-02-01T10:05:00Z", created_at="2022-02-01T10:00:00Z"):
    """A record as the *listing* returns it: always the latest attempt of the run.

    `previous_attempt_url` is GitHub's back-link to the attempt before this one, and null on a run
    that was never re-run.
    """
    return {
        "id": run_id,
        "url": f"{RUNS_URL}/{run_id}",
        "run_attempt": run_attempt,
        "previous_attempt_url": f"{RUNS_URL}/{run_id}/attempts/{run_attempt - 1}" if run_attempt > 1 else None,
        "logs_url": f"{RUNS_URL}/{run_id}/logs",
        "jobs_url": f"{RUNS_URL}/{run_id}/jobs",
        "created_at": created_at,
        "updated_at": updated_at,
        "conclusion": "success",
    }


def _attempt(run_id, run_attempt, updated_at, created_at, conclusion="success", has_previous=None):
    """A record as the *attempt* endpoint returns it: the same shape, scoped to one attempt."""
    if has_previous is None:
        has_previous = run_attempt > 1
    return {
        "id": run_id,
        "url": f"{RUNS_URL}/{run_id}",
        "run_attempt": run_attempt,
        "previous_attempt_url": f"{RUNS_URL}/{run_id}/attempts/{run_attempt - 1}" if has_previous else None,
        "logs_url": f"{RUNS_URL}/{run_id}/attempts/{run_attempt}/logs",
        "jobs_url": f"{RUNS_URL}/{run_id}/attempts/{run_attempt}/jobs",
        "created_at": created_at,
        "updated_at": updated_at,
        "conclusion": conclusion,
    }


def _catalog():
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="workflow_run_attempts",
                    json_schema={},
                    supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
                ),
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.append,
            )
        ]
    )


def _state(cursor_value):
    """A resumed state as the connector emits it: an inert child cursor next to the parent state
    that actually decides which runs are re-read."""
    return [
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name="workflow_run_attempts"),
                stream_state=AirbyteStateBlob(
                    {
                        "use_global_cursor": True,
                        "state": {"updated_at": cursor_value},
                        "parent_state": {
                            "workflow_runs_for_attempts": {
                                "use_global_cursor": True,
                                "state": {"updated_at": cursor_value},
                            }
                        },
                    }
                ),
            ),
        )
    ]


def _mock_repository(requests_mock):
    requests_mock.get(REPO_URL, json={"id": 1, "full_name": "org/repos", "organization": {"login": "org"}})


def _mock_runs(requests_mock, runs):
    requests_mock.get(RUNS_URL, json={"total_count": len(runs), "workflow_runs": runs})


def _mock_attempts(requests_mock, attempts):
    for attempt in attempts:
        requests_mock.get(f"{RUNS_URL}/{attempt['id']}/attempts/{attempt['run_attempt']}", json=attempt)


def _read(config, state=None):
    catalog = _catalog()
    source = SourceGithub(config=dict(config), catalog=catalog, state=state)
    records, statuses, states = [], [], []
    for message in source.read(logging.getLogger("airbyte"), dict(config), catalog, state or []):
        if message.type == Type.RECORD:
            records.append(message.record.data)
        elif message.type == Type.STATE:
            states.append(message.state.stream.stream_state)
        elif message.type == Type.TRACE and message.trace.stream_status:
            statuses.append(message.trace.stream_status.status.value)
    return records, statuses, states


def _keys(records):
    return sorted((record["id"], record["run_attempt"]) for record in records)


def _attempt_requests(requests_mock):
    return [request.path for request in requests_mock.request_history if "/attempts/" in request.path]


def test_primary_key_is_composite(rate_limit_mock_response, requests_mock):
    """All attempts of a run share the same `id`, so `run_attempt` is what makes a record unique.
    This is the whole point of oncall#8827 — the reported fix (adding `run_attempt` to
    `workflow_runs`' key) could not help, because that stream never emits an earlier attempt."""
    _mock_repository(requests_mock)
    source = SourceGithub(config=dict(CONFIG), catalog=_catalog(), state=None)

    stream = next(s for s in source.discover(logging.getLogger("airbyte"), dict(CONFIG)).streams if s.name == "workflow_run_attempts")

    assert stream.source_defined_primary_key == [["id"], ["run_attempt"]]
    assert SyncMode.incremental in stream.supported_sync_modes


def test_every_attempt_of_a_rerun_is_emitted(rate_limit_mock_response, requests_mock):
    _mock_repository(requests_mock)
    _mock_runs(requests_mock, [_run(2, run_attempt=3, updated_at="2022-02-02T12:05:00Z", created_at="2022-02-02T10:00:00Z")])
    _mock_attempts(
        requests_mock,
        [
            _attempt(2, 1, updated_at="2022-02-02T10:04:00Z", created_at="2022-02-02T10:00:00Z", conclusion="failure"),
            _attempt(2, 2, updated_at="2022-02-02T11:05:00Z", created_at="2022-02-02T11:00:00Z", conclusion="failure"),
            _attempt(2, 3, updated_at="2022-02-02T12:05:00Z", created_at="2022-02-02T12:00:00Z"),
        ],
    )

    records, statuses, _ = _read(CONFIG)

    assert statuses[-1] == "COMPLETE"
    assert _keys(records) == [(2, 1), (2, 2), (2, 3)]
    # Each attempt reports its own start time, unlike the listing record which always reports the
    # run's — which is why the latest attempt is fetched too instead of reusing the listing payload.
    assert sorted(record["created_at"] for record in records) == [
        "2022-02-02T10:00:00Z",
        "2022-02-02T11:00:00Z",
        "2022-02-02T12:00:00Z",
    ]
    # The chain is walked backwards from the latest attempt via `previous_attempt_url`.
    assert _attempt_requests(requests_mock) == [
        "/repos/org/repos/actions/runs/2/attempts/3",
        "/repos/org/repos/actions/runs/2/attempts/2",
        "/repos/org/repos/actions/runs/2/attempts/1",
    ]


def test_run_that_was_never_rerun_costs_a_single_request(rate_limit_mock_response, requests_mock):
    """A run with one attempt still costs one request: the declarative retriever has no way to emit
    a parent record as a child record, so the attempt endpoint is called even though the listing
    payload already differs only in `logs_url` and `jobs_url`."""
    _mock_repository(requests_mock)
    _mock_runs(requests_mock, [_run(1)])
    _mock_attempts(requests_mock, [_attempt(1, 1, updated_at="2022-02-01T10:05:00Z", created_at="2022-02-01T10:00:00Z")])

    records, _, _ = _read(CONFIG)

    assert _keys(records) == [(1, 1)]
    assert _attempt_requests(requests_mock) == ["/repos/org/repos/actions/runs/1/attempts/1"]
    # Attempt-scoped URLs, not the run-scoped ones the listing carries.
    assert records[0]["logs_url"] == f"{RUNS_URL}/1/attempts/1/logs"
    assert records[0]["jobs_url"] == f"{RUNS_URL}/1/attempts/1/jobs"


def test_earlier_attempt_survives_an_incremental_boundary(rate_limit_mock_response, requests_mock):
    """The regression this stream exists to prevent.

    A sync landing between the first attempt finishing (10:04) and the re-run starting (11:00)
    leaves the cursor at 10:04. On the next sync the run comes back because the *run's* cursor moved
    to 11:05, and attempt 1 has to come with it even though the attempt's own `updated_at` is not
    past the cursor. Filtering the attempts themselves — which is what the abandoned PR #70305 did —
    drops attempt 1 permanently, since no later sync ever revisits it either.
    """
    _mock_repository(requests_mock)
    _mock_runs(requests_mock, [_run(2, run_attempt=2, updated_at="2022-02-02T11:05:00Z", created_at="2022-02-02T10:00:00Z")])
    _mock_attempts(
        requests_mock,
        [
            _attempt(2, 1, updated_at="2022-02-02T10:04:00Z", created_at="2022-02-02T10:00:00Z", conclusion="failure"),
            _attempt(2, 2, updated_at="2022-02-02T11:05:00Z", created_at="2022-02-02T11:00:00Z"),
        ],
    )

    records, _, _ = _read(CONFIG, state=_state("2022-02-02T10:04:00Z"))

    assert _keys(records) == [(2, 1), (2, 2)]


def test_run_not_updated_since_the_last_sync_is_skipped(rate_limit_mock_response, requests_mock):
    """The parent filters on the run's own `updated_at`, so an untouched run costs no attempt call."""
    _mock_repository(requests_mock)
    _mock_runs(requests_mock, [_run(1, updated_at="2022-02-01T10:05:00Z")])

    records, statuses, _ = _read(CONFIG, state=_state("2022-03-01T00:00:00Z"))

    assert records == []
    assert statuses[-1] == "COMPLETE"
    assert _attempt_requests(requests_mock) == []


def test_state_tracks_the_run_cursor_and_carries_parent_state(rate_limit_mock_response, requests_mock):
    """The emitted state is what the next sync narrows on: a global child cursor (no per-run entry,
    since a run is never revisited) plus the parent's per-repository resumption point."""
    _mock_repository(requests_mock)
    _mock_runs(
        requests_mock,
        [
            _run(1, updated_at="2022-02-01T10:05:00Z"),
            _run(2, run_attempt=2, updated_at="2022-02-02T11:05:00Z", created_at="2022-02-02T10:00:00Z"),
        ],
    )
    _mock_attempts(
        requests_mock,
        [
            _attempt(1, 1, updated_at="2022-02-01T10:05:00Z", created_at="2022-02-01T10:00:00Z"),
            _attempt(2, 1, updated_at="2022-02-02T10:04:00Z", created_at="2022-02-02T10:00:00Z", conclusion="failure"),
            _attempt(2, 2, updated_at="2022-02-02T11:05:00Z", created_at="2022-02-02T11:00:00Z"),
        ],
    )

    _, _, states = _read(CONFIG)

    final = states[-1]
    assert final.use_global_cursor is True
    # 11:05 is the newest run's `updated_at`; attempt 1's older 10:04 must not pull the cursor back.
    assert final.state == {"updated_at": "2022-02-02T11:05:00Z"}
    # No per-run entry: `global_substream_cursor` keeps the state one value wide however many runs
    # the sync walked.
    assert not hasattr(final, "states")
    parent = final.parent_state["workflow_runs_for_attempts"]
    assert parent["states"] == [{"partition": {"repository": "org/repos"}, "cursor": {"updated_at": "2022-02-02T11:05:00Z"}}]


@pytest.mark.parametrize(
    "state_value,expected_created",
    [
        pytest.param(None, ">=2021-11-30", id="first_sync_uses_the_config_start_date"),
        pytest.param("2022-06-15T00:00:00Z", ">=2022-05-14", id="resumed_sync_uses_the_cursor"),
    ],
)
def test_listing_is_bounded_to_the_32_day_rerun_window(rate_limit_mock_response, requests_mock, state_value, expected_created):
    """GitHub refuses to re-run a workflow more than 32 days after it was created, so no run created
    before that window can still be updated after the cursor. Bounding `created` server-side is what
    keeps an incremental sync from walking the repository's entire run history, and replaces the
    legacy pagination break in `WorkflowRuns.read_records`."""
    _mock_repository(requests_mock)
    _mock_runs(requests_mock, [])

    _read(CONFIG, state=_state(state_value) if state_value else None)

    listing = next(request for request in requests_mock.request_history if request.path == "/repos/org/repos/actions/runs")
    assert listing.qs["created"] == [expected_created]
    assert listing.qs["per_page"] == ["100"]
