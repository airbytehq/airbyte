#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Behavior of the four streams with special logic migrated to the manifest (Step 8).

`commits` slices per branch (configured branches, else the default branch) and filters with
`since`; `workflow_runs` asks GitHub for the runs created in the 32 days before its cursor, because
a run can be re-run for that long; `workflow_jobs` reads the jobs of those runs and keeps one cursor
for the stream; `contributor_activity` retries the 202 GitHub answers while it computes statistics.
Each test asserts parity with the Python classes these streams replaced, or pins the deliberate
divergence.
"""

import json
import logging
import os
import shutil
from pathlib import Path
from unittest.mock import patch

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


MIGRATED_STREAMS = ["commits", "contributor_activity", "workflow_runs", "workflow_jobs"]
INCREMENTAL_STREAMS = {"commits", "workflow_runs", "workflow_jobs"}

_TOKEN_CONFIG = {"credentials": {"personal_access_token": "token"}}
_START_DATE = "2022-01-01T00:00:00Z"
_BEFORE_START = "2021-06-01T00:00:00Z"
_AFTER_START = "2022-06-01T00:00:00Z"
_LATER = "2022-07-01T00:00:00Z"
_REPO = "docker/compose"
_API = "https://api.github.com"


def _config(*repositories, **overrides):
    return {**_TOKEN_CONFIG, "repositories": list(repositories), "start_date": _START_DATE, **overrides}


def _catalog(*stream_names):
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name=stream_name,
                    json_schema={},
                    supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental]
                    if stream_name in INCREMENTAL_STREAMS
                    else [SyncMode.full_refresh],
                ),
                sync_mode=SyncMode.incremental if stream_name in INCREMENTAL_STREAMS else SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
            )
            for stream_name in stream_names
        ]
    )


def _read_messages(config, *stream_names, state=None):
    shutil.rmtree(os.environ["REQUEST_CACHE_PATH"], ignore_errors=True)
    catalog = _catalog(*stream_names)
    source = SourceGithub(config=dict(config), catalog=catalog, state=state)
    messages, error = [], None
    try:
        for message in source.read(logging.getLogger("airbyte"), dict(config), catalog, state or []):
            messages.append(message)
    except Exception as exc:  # noqa: BLE001 - the assertions inspect the failure
        error = exc
    return messages, error


def _read(config, stream_name, state=None):
    messages, error = _read_messages(config, stream_name, state=state)
    records = [message.record.data for message in messages if message.type == Type.RECORD]
    statuses = [
        message.trace.stream_status.status.value for message in messages if message.type == Type.TRACE and message.trace.stream_status
    ]
    states = [message.state for message in messages if message.type == Type.STATE]
    return records, statuses, states, error


def _mock_repository_resolution(requests_mock, *repositories, default_branch="main"):
    for index, repository in enumerate(repositories, start=1):
        requests_mock.get(
            f"{_API}/repos/{repository}",
            json={
                "id": index,
                "full_name": repository,
                "default_branch": default_branch,
                "organization": {"login": repository.split("/")[0]},
            },
        )


def _state_message(stream_name, state):
    return [
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(stream_descriptor=StreamDescriptor(name=stream_name), stream_state=AirbyteStateBlob(state)),
        )
    ]


def _requested(requests_mock, fragment):
    return [
        (request.path + ("?" + request.query if request.query else "")).lower()
        for request in requests_mock.request_history
        if fragment in request.path
    ]


def _partition_cursors(state_message):
    state = state_message.stream.stream_state.__dict__
    return {json.dumps(entry["partition"], sort_keys=True): next(iter(entry["cursor"].values())) for entry in state["states"]}


def _commit(sha, date):
    return {"sha": sha, "commit": {"author": {"date": date}}}


def _run(run_id, created_at, updated_at, repository=_REPO):
    return {"id": run_id, "created_at": created_at, "updated_at": updated_at, "repository": {"full_name": repository}}


def test_streams_are_served_by_the_manifest_only(rate_limit_mock_response, requests_mock):
    config = _config(_REPO)
    _mock_repository_resolution(requests_mock, _REPO)
    source = SourceGithub(config=dict(config), catalog=None, state=None)

    python_names = {stream.name for stream in source.streams(dict(config))}
    discovered = {stream.name: stream for stream in source.discover(logging.getLogger("airbyte"), dict(config)).streams}

    assert not python_names & set(MIGRATED_STREAMS)
    assert set(MIGRATED_STREAMS) <= set(discovered)
    assert discovered["commits"].source_defined_primary_key == [["sha"]] and discovered["commits"].default_cursor_field == ["created_at"]
    assert discovered["workflow_runs"].default_cursor_field == ["updated_at"]
    assert discovered["workflow_jobs"].default_cursor_field == ["completed_at"]
    assert discovered["contributor_activity"].supported_sync_modes == [SyncMode.full_refresh]
    assert "repository_branches_resolver" not in discovered


# ---------------------------------------------------------------------------------------- commits


def test_commits_read_the_default_branch_when_none_is_configured(rate_limit_mock_response, requests_mock):
    """`Commits._validate_branches_to_pull`: a repository without configured branches pulls its
    default branch, with `sha=<branch>` and `since=<start_date>` as the Python class sent them.
    `created_at` is lifted from `commit.author.date` and `branch` and `repository` are stamped."""
    config = _config(_REPO)
    _mock_repository_resolution(requests_mock, _REPO)
    requests_mock.get(f"{_API}/repos/{_REPO}/branches", json=[{"name": "main"}, {"name": "dev"}])
    requests_mock.get(f"{_API}/repos/{_REPO}/commits", json=[_commit("a", _AFTER_START), _commit("b", _LATER)])

    records, statuses, states, error = _read(config, "commits")

    assert error is None
    assert statuses[-1] == "COMPLETE"
    assert records == [
        {"sha": "a", "commit": {"author": {"date": _AFTER_START}}, "repository": _REPO, "branch": "main", "created_at": _AFTER_START},
        {"sha": "b", "commit": {"author": {"date": _LATER}}, "repository": _REPO, "branch": "main", "created_at": _LATER},
    ]
    assert _requested(requests_mock, "/commits") == [f"/repos/{_REPO}/commits?per_page=100&sha=main&since=2022-01-01t00%3a00%3a00z"]
    assert _partition_cursors(states[-1]) == {'{"branch": "main", "parent_slice": {"repository": "docker/compose"}}': _LATER}


@pytest.mark.parametrize(
    ("branches", "expected"),
    [
        pytest.param(
            ["docker/compose/dev", "docker/compose/feature", "docker/compose/missing", "other/repo/x"],
            ["dev", "feature"],
            id="configured_branches_that_exist",
        ),
        pytest.param(["docker/compose/missing"], ["main"], id="no_configured_branch_exists_falls_back_to_default"),
        pytest.param(["other/repo/dev"], ["main"], id="branches_of_another_repository_do_not_count"),
    ],
)
def test_commits_branch_selection(branches, expected, rate_limit_mock_response, requests_mock):
    config = _config(_REPO, branches=branches)
    _mock_repository_resolution(requests_mock, _REPO)
    requests_mock.get(f"{_API}/repos/{_REPO}/branches", json=[{"name": "main"}, {"name": "dev"}, {"name": "feature"}])
    requests_mock.get(f"{_API}/repos/{_REPO}/commits", json=[_commit("a", _AFTER_START)])

    records, _, _, error = _read(config, "commits")

    assert error is None
    assert sorted(record["branch"] for record in records) == expected
    assert sorted(_requested(requests_mock, "/commits")) == sorted(
        f"/repos/{_REPO}/commits?per_page=100&sha={branch}&since=2022-01-01t00%3a00%3a00z" for branch in expected
    )


def test_commits_two_syncs_legacy_scenario(rate_limit_mock_response, requests_mock):
    """`test_stream_commits_incremental_read`, ported. The second sync sends the first sync's
    cursor as `since`; the record dated exactly the cursor comes back and is re-emitted (the
    inclusive CDK filter), where the Python class dropped it."""
    config = _config("organization/repository", start_date="2022-02-02T10:10:03Z", branches=["organization/repository/branch"])
    _mock_repository_resolution(requests_mock, "organization/repository")
    requests_mock.get(f"{_API}/repos/organization/repository/branches", json=[{"name": "branch"}, {"name": "main"}])
    data = [
        _commit(sha, f"2022-02-02T10:10:{seconds:02d}Z") for sha, seconds in ((1, 2), (2, 4), (3, 6), (4, 8), (5, 10), (6, 12), (7, 14))
    ]
    commits = f"{_API}/repos/organization/repository/commits"
    requests_mock.get(f"{commits}?per_page=100&since=2022-02-02T10%3A10%3A03Z&sha=branch", json=data[0:3])
    requests_mock.get(
        f"{commits}?per_page=100&since=2022-02-02T10%3A10%3A06Z&sha=branch",
        json=data[2:5],
        headers={"Link": f'<{commits}?per_page=100&page=2&since=2022-02-02T10%3A10%3A06Z&sha=branch>; rel="next"'},
    )
    requests_mock.get(f"{commits}?per_page=100&page=2&since=2022-02-02T10%3A10%3A06Z&sha=branch", json=data[5:7])

    records, _, states, error = _read(config, "commits")
    assert error is None
    assert [record["sha"] for record in records] == [1, 2, 3], "GitHub's `since` did the filtering; the Python class re-filtered strictly"
    assert _partition_cursors(states[-1]) == {
        '{"branch": "branch", "parent_slice": {"repository": "organization/repository"}}': "2022-02-02T10:10:06Z"
    }

    records, _, states, error = _read(config, "commits", state=_state_message("commits", states[-1].stream.stream_state.__dict__))
    assert error is None
    assert [record["sha"] for record in records] == [3, 4, 5, 6, 7]
    assert _partition_cursors(states[-1]) == {
        '{"branch": "branch", "parent_slice": {"repository": "organization/repository"}}': "2022-02-02T10:10:14Z"
    }


def test_commits_legacy_state_is_migrated_per_branch(rate_limit_mock_response, requests_mock):
    """The Python class kept `{repository: {branch: {created_at}}}`; the migration has to land on
    the `{"branch": ..., "parent_slice": {"repository": ...}}` partition the router builds, and a
    digit-only branch name must stay a string."""
    config = _config(_REPO, branches=["docker/compose/2024"])
    _mock_repository_resolution(requests_mock, _REPO)
    requests_mock.get(f"{_API}/repos/{_REPO}/branches", json=[{"name": "main"}, {"name": "2024"}])
    requests_mock.get(f"{_API}/repos/{_REPO}/commits", json=[_commit("a", _LATER)])

    _, _, states, error = _read(config, "commits", state=_state_message("commits", {_REPO: {"2024": {"created_at": _AFTER_START}}}))

    assert error is None
    assert _requested(requests_mock, "/commits") == [f"/repos/{_REPO}/commits?per_page=100&sha=2024&since=2022-06-01t00%3a00%3a00z"]
    assert _partition_cursors(states[-1]) == {'{"branch": "2024", "parent_slice": {"repository": "docker/compose"}}': _LATER}


def test_commits_empty_repository_is_skipped(rate_limit_mock_response, requests_mock):
    """`test_stream_commits_409_empty_repository`, ported: GitHub answers 409 "Git Repository is
    empty." for a repository with no commits; the repository is skipped and the sync completes."""
    config = _config(_REPO)
    _mock_repository_resolution(requests_mock, _REPO)
    requests_mock.get(f"{_API}/repos/{_REPO}/branches", json=[{"name": "main"}])
    requests_mock.get(f"{_API}/repos/{_REPO}/commits", status_code=409, json={"message": "Git Repository is empty.", "status": "409"})

    records, statuses, _, error = _read(config, "commits")

    assert error is None
    assert records == [] and statuses[-1] == "COMPLETE"


# --------------------------------------------------------------------------- contributor_activity


def test_contributor_activity_flattens_the_author(rate_limit_mock_response, requests_mock):
    """`ContributorActivity.transform`: `author`'s fields are lifted onto the record and the
    `author` key removed; a null author (`test_stream_contributor_activity_parse_empty_author`)
    leaves the record as it came, plus `repository`."""
    config = _config(_REPO)
    _mock_repository_resolution(requests_mock, _REPO)
    requests_mock.get(
        f"{_API}/repos/{_REPO}/stats/contributors",
        json=[
            {"author": {"login": "octo", "id": 7}, "total": 3, "weeks": [{"w": 1713052800, "a": 1, "d": 0, "c": 1}]},
            {"author": None, "total": 0, "weeks": [{"w": 1713052800, "a": 0, "d": 0, "c": 0}]},
        ],
    )

    records, statuses, _, error = _read(config, "contributor_activity")

    assert error is None
    assert statuses[-1] == "COMPLETE"
    assert records == [
        {"total": 3, "weeks": [{"w": 1713052800, "a": 1, "d": 0, "c": 1}], "repository": _REPO, "login": "octo", "id": 7},
        {"total": 0, "weeks": [{"w": 1713052800, "a": 0, "d": 0, "c": 0}], "repository": _REPO},
    ]
    (request,) = [request for request in requests_mock.request_history if "/stats/" in request.path]
    assert request.headers["Accept"] == "application/vnd.github+json"
    assert request.headers["X-GitHub-Api-Version"] == "2022-11-28"
    assert request.headers["User-Agent"] == "PostmanRuntime/7.28.0"


def test_contributor_activity_reads_the_response_fixture(rate_limit_mock_response, requests_mock):
    """`test_stream_contributor_activity_parse_response`, ported onto the same fixture."""
    config = _config("airbytehq/airbyte")
    _mock_repository_resolution(requests_mock, "airbytehq/airbyte")
    requests_mock.get(
        f"{_API}/repos/airbytehq/airbyte/stats/contributors",
        json=json.load(open(Path(__file__).parent / "responses/contributor_activity_response.json")),
    )

    records, _, _, error = _read(config, "contributor_activity")

    assert error is None
    assert len(records) == 1
    assert records[0]["repository"] == "airbytehq/airbyte" and "author" not in records[0] and "login" in records[0]


def test_contributor_activity_empty_response_yields_nothing(rate_limit_mock_response, requests_mock):
    """`test_stream_contributor_activity_parse_empty_response`, ported: GitHub answers 204 with no
    body for a repository without statistics."""
    config = _config(_REPO)
    _mock_repository_resolution(requests_mock, _REPO)
    requests_mock.get(f"{_API}/repos/{_REPO}/stats/contributors", status_code=204, text="")

    records, statuses, _, error = _read(config, "contributor_activity")

    assert error is None
    assert records == [] and statuses[-1] == "COMPLETE"


@patch("time.sleep")
def test_contributor_activity_retries_202_every_90_seconds_then_fails(sleep_mock, rate_limit_mock_response, requests_mock):
    """GitHub answers 202 while it computes the statistics
    (`test_stream_contributor_activity_accepted_response`). Legacy retried five times, 90 seconds
    apart, then logged and skipped the repository; the manifest retries the same way and then
    fails the stream — `DefaultErrorHandler` has no "retry N times, then ignore", the divergence
    every migrated stream carries for exhausted retries."""
    config = _config(_REPO)
    _mock_repository_resolution(requests_mock, _REPO)
    requests_mock.get(f"{_API}/repos/{_REPO}/stats/contributors", status_code=202, text="")

    records, statuses, _, error = _read(config, "contributor_activity")

    assert records == [] and statuses[-1] == "INCOMPLETE"
    assert len([request for request in requests_mock.request_history if "/stats/" in request.path]) == 6
    waits = [call.args[0] for call in sleep_mock.call_args_list if call.args and call.args[0] > 1]
    assert len(waits) >= 5 and all(90 <= wait < 92 for wait in waits)


def test_contributor_activity_other_errors_are_not_swallowed(rate_limit_mock_response, requests_mock):
    """`test_contributor_activity_reraises_non_accepted_status`, ported: only 202 is retried; a
    401 fails the stream instead of being treated like "still computing"."""
    config = _config(_REPO)
    _mock_repository_resolution(requests_mock, _REPO)
    requests_mock.get(f"{_API}/repos/{_REPO}/stats/contributors", status_code=401, json={"message": "Unauthorized"})

    records, statuses, _, error = _read(config, "contributor_activity")

    assert records == [] and statuses[-1] == "INCOMPLETE"
    assert error is not None and "401" in str(error)


# ----------------------------------------------------------------------------------- workflow_runs


def test_workflow_runs_filter_on_updated_at_and_carry_the_window_start(rate_limit_mock_response, requests_mock):
    """`WorkflowRuns.read_records` emitted the runs updated after its cursor, whatever their
    `created_at`, so a re-run of an old run is kept. The slice start is sent as a header for the
    pagination strategy to stop on; no `created` filter, which GitHub caps at 1,000 results."""
    config = _config(_REPO)
    _mock_repository_resolution(requests_mock, _REPO)
    requests_mock.get(
        f"{_API}/repos/{_REPO}/actions/runs",
        json={
            "total_count": 3,
            "workflow_runs": [_run(3, _LATER, _LATER), _run(2, _BEFORE_START, _AFTER_START), _run(1, _BEFORE_START, _BEFORE_START)],
        },
    )

    records, statuses, states, error = _read(config, "workflow_runs")

    assert error is None
    assert statuses[-1] == "COMPLETE"
    assert [record["id"] for record in records] == [3, 2]
    assert records[0]["repository"] == {"full_name": _REPO}, "legacy emitted the payload as is, no `repository` string"
    (request,) = [request for request in requests_mock.request_history if request.path.endswith("/actions/runs")]
    assert request.qs == {"per_page": ["100"]}
    assert request.headers["X-Airbyte-Window-Start"] == _START_DATE
    assert _partition_cursors(states[-1]) == {'{"repository": "docker/compose"}': _LATER}


def test_workflow_runs_legacy_state_becomes_the_window_start(rate_limit_mock_response, requests_mock):
    config = _config(_REPO)
    _mock_repository_resolution(requests_mock, _REPO)
    requests_mock.get(f"{_API}/repos/{_REPO}/actions/runs", json={"total_count": 1, "workflow_runs": [_run(3, _LATER, _LATER)]})

    records, _, _, error = _read(config, "workflow_runs", state=_state_message("workflow_runs", {_REPO: {"updated_at": _AFTER_START}}))

    assert error is None
    assert [record["id"] for record in records] == [3]
    (request,) = [request for request in requests_mock.request_history if request.path.endswith("/actions/runs")]
    assert request.headers["X-Airbyte-Window-Start"] == _AFTER_START


def test_workflow_runs_stop_paging_at_the_first_run_older_than_the_window(rate_limit_mock_response, requests_mock):
    """Legacy broke out of the page loop at the first run created more than 32 days before the
    cursor; `WorkflowRunsPaginationStrategy` does the same, so a busy repository is not read back
    to its first run on every sync."""
    config = _config(_REPO)
    _mock_repository_resolution(requests_mock, _REPO)
    runs = f"{_API}/repos/{_REPO}/actions/runs"
    requests_mock.get(
        runs,
        [
            {
                "json": {"total_count": 3, "workflow_runs": [_run(3, _LATER, _LATER), _run(2, "2021-12-15T00:00:00Z", _AFTER_START)]},
                "headers": {"Link": f'<{runs}?page=2>; rel="next"'},
            },
            {
                "json": {"total_count": 3, "workflow_runs": [_run(1, "2021-11-01T00:00:00Z", _AFTER_START)]},
                "headers": {"Link": f'<{runs}?page=3>; rel="next"'},
            },
            {"json": {"total_count": 3, "workflow_runs": [_run(0, "2021-01-01T00:00:00Z", _LATER)]}},
        ],
    )

    records, statuses, _, error = _read(config, "workflow_runs")

    assert error is None
    assert statuses[-1] == "COMPLETE"
    # run 1 was created outside the window but is on the page that ends pagination, so it is still read; page 3 never is
    assert [record["id"] for record in records] == [3, 2, 1]
    assert [request.qs.get("page") for request in requests_mock.request_history if request.path.endswith("/actions/runs")] == [None, ["2"]]


def test_workflow_runs_keep_paging_while_the_window_holds_even_if_nothing_is_emitted(rate_limit_mock_response, requests_mock):
    """A page whose runs were all created inside the window but not updated since the cursor emits
    nothing, yet pagination must go on: a re-run of an older run may sit on the next page. The
    strategy reads the raw page, not the filtered records, which is what makes this work."""
    config = _config(_REPO)
    _mock_repository_resolution(requests_mock, _REPO)
    runs = f"{_API}/repos/{_REPO}/actions/runs"
    requests_mock.get(
        runs,
        [
            {
                "json": {"total_count": 2, "workflow_runs": [_run(2, _AFTER_START, _AFTER_START)]},
                "headers": {"Link": f'<{runs}?page=2>; rel="next"'},
            },
            {"json": {"total_count": 2, "workflow_runs": [_run(1, "2022-05-20T00:00:00Z", _LATER)]}},
        ],
    )

    records, _, _, error = _read(
        config, "workflow_runs", state=_state_message("workflow_runs", {_REPO: {"updated_at": "2022-06-15T00:00:00Z"}})
    )

    assert error is None
    assert [record["id"] for record in records] == [1]
    assert len([request for request in requests_mock.request_history if request.path.endswith("/actions/runs")]) == 2


def test_workflow_runs_two_syncs_legacy_scenario(rate_limit_mock_response, requests_mock):
    """`test_stream_workflow_runs_read_incremental`, ported: the second sync picks up a new run and
    a re-run of an old one, plus the boundary run (inclusive CDK filter)."""
    config = _config("org/repos")
    _mock_repository_resolution(requests_mock, "org/repos")
    runs = f"{_API}/repos/org/repos/actions/runs"
    data = [
        _run(4, "2022-02-05T00:00:00Z", "2022-02-05T00:00:00Z", "org/repos"),
        _run(3, "2022-01-15T00:00:00Z", "2022-01-15T00:00:00Z", "org/repos"),
        _run(2, "2022-01-03T00:00:00Z", "2022-01-03T00:00:00Z", "org/repos"),
        _run(1, "2022-01-02T00:00:00Z", "2022-01-02T00:00:00Z", "org/repos"),
    ]
    requests_mock.get(runs, json={"total_count": 4, "workflow_runs": data})

    records, _, states, error = _read(config, "workflow_runs")
    assert error is None
    assert [record["id"] for record in records] == [4, 3, 2, 1]
    assert _partition_cursors(states[-1]) == {'{"repository": "org/repos"}': "2022-02-05T00:00:00Z"}

    data.insert(0, _run(5, "2022-02-07T00:00:00Z", "2022-02-07T00:00:00Z", "org/repos"))
    data[2]["updated_at"] = "2022-02-08T00:00:00Z"
    requests_mock.get(runs, json={"total_count": 5, "workflow_runs": data})

    records, _, states, error = _read(
        config, "workflow_runs", state=_state_message("workflow_runs", states[-1].stream.stream_state.__dict__)
    )
    assert error is None
    assert [record["id"] for record in records] == [5, 4, 3]
    assert [request for request in requests_mock.request_history if request.path.endswith("/actions/runs")][-1].headers[
        "X-Airbyte-Window-Start"
    ] == "2022-02-05T00:00:00Z"
    assert _partition_cursors(states[-1]) == {'{"repository": "org/repos"}': "2022-02-08T00:00:00Z"}


# ----------------------------------------------------------------------------------- workflow_jobs


def test_workflow_jobs_two_syncs_legacy_scenario(rate_limit_mock_response, requests_mock):
    """`test_stream_workflow_jobs_read`, ported. Jobs are read for the runs the parent returns,
    with `filter=all`; jobs still running (`completed_at: null`) are dropped; the stream keeps one
    `completed_at` cursor and lets the parent resume from its own state, so the second sync only
    re-reads the runs updated since then."""
    config = _config("org/repo", start_date="2022-09-02T09:05:00Z")
    _mock_repository_resolution(requests_mock, "org/repo")
    runs_url = f"{_API}/repos/org/repo/actions/runs"
    workflow_runs = [
        _run(1, "2022-09-02T09:00:00Z", "2022-09-02T09:10:02Z", "org/repo"),
        _run(2, "2022-09-02T09:06:00Z", "2022-09-02T09:08:00Z", "org/repo"),
    ]
    jobs_1 = [
        {"id": 1, "completed_at": "2022-09-02T09:02:00Z", "run_id": 1},
        {"id": 4, "completed_at": "2022-09-02T09:10:00Z", "run_id": 1},
        {"id": 5, "completed_at": None, "run_id": 1},
    ]
    jobs_2 = [
        {"id": 2, "completed_at": "2022-09-02T09:07:00Z", "run_id": 2},
        {"id": 3, "completed_at": "2022-09-02T09:08:00Z", "run_id": 2},
    ]
    requests_mock.get(runs_url, json={"total_count": 2, "workflow_runs": workflow_runs})
    requests_mock.get(f"{runs_url}/1/jobs", json={"jobs": jobs_1})
    requests_mock.get(f"{runs_url}/2/jobs", json={"jobs": jobs_2})

    records, statuses, states, error = _read(config, "workflow_jobs")
    assert error is None
    assert statuses[-1] == "COMPLETE"
    assert sorted(records, key=lambda record: record["id"]) == [
        {"id": 2, "completed_at": "2022-09-02T09:07:00Z", "run_id": 2, "repository": "org/repo"},
        {"id": 3, "completed_at": "2022-09-02T09:08:00Z", "run_id": 2, "repository": "org/repo"},
        {"id": 4, "completed_at": "2022-09-02T09:10:00Z", "run_id": 1, "repository": "org/repo"},
    ]
    assert all(request.endswith("/jobs?per_page=100&filter=all") for request in _requested(requests_mock, "/jobs"))
    state = states[-1].stream.stream_state.__dict__
    assert state["use_global_cursor"] is True and state["state"] == {"completed_at": "2022-09-02T09:10:00Z"}
    assert state["parent_state"]["workflow_runs"]["states"] == [
        {"partition": {"repository": "org/repo"}, "cursor": {"updated_at": "2022-09-02T09:10:02Z"}}
    ]

    jobs_1[2]["completed_at"] = "2022-09-02T09:12:00Z"
    workflow_runs[0]["updated_at"] = "2022-09-02T09:12:01Z"
    workflow_runs.append(_run(3, "2022-09-02T09:14:00Z", "2022-09-02T09:15:00Z", "org/repo"))
    requests_mock.get(runs_url, json={"total_count": 3, "workflow_runs": workflow_runs})
    requests_mock.get(f"{runs_url}/1/jobs", json={"jobs": jobs_1})
    requests_mock.get(
        f"{runs_url}/3/jobs",
        json={"jobs": [{"id": 6, "completed_at": "2022-09-02T09:15:00Z", "run_id": 3}, {"id": 7, "completed_at": None, "run_id": 3}]},
    )
    before = len(_requested(requests_mock, "/jobs"))

    records, _, states, error = _read(config, "workflow_jobs", state=_state_message("workflow_jobs", state))
    assert error is None
    # 4 is the boundary job (inclusive filter), 5 completed since, 6 is new; run 2 was not updated and is not re-read
    assert sorted(record["id"] for record in records) == [4, 5, 6]
    assert sorted(_requested(requests_mock, "/jobs")[before:]) == [
        f"/repos/org/repo/actions/runs/1/jobs?per_page=100&filter=all",
        f"/repos/org/repo/actions/runs/3/jobs?per_page=100&filter=all",
    ]
    assert states[-1].stream.stream_state.__dict__["state"] == {"completed_at": "2022-09-02T09:15:00Z"}


def test_workflow_jobs_legacy_state_is_migrated(rate_limit_mock_response, requests_mock):
    """The Python class kept `{repository: {completed_at}}` and handed that cursor to its parent as
    `updated_at`. The migration keeps both: the parent resumes per repository from that value and
    the stream's own cursor is the lowest one across repositories."""
    config = _config("org/repo", start_date="2022-09-02T09:05:00Z")
    _mock_repository_resolution(requests_mock, "org/repo")
    runs_url = f"{_API}/repos/org/repo/actions/runs"
    requests_mock.get(
        runs_url,
        json={
            "total_count": 2,
            "workflow_runs": [
                _run(1, "2022-09-02T09:00:00Z", "2022-09-02T09:12:01Z", "org/repo"),
                _run(2, "2022-09-02T09:06:00Z", "2022-09-02T09:08:00Z", "org/repo"),
            ],
        },
    )
    requests_mock.get(
        f"{runs_url}/1/jobs",
        json={
            "jobs": [
                {"id": 4, "completed_at": "2022-09-02T09:10:00Z", "run_id": 1},
                {"id": 5, "completed_at": "2022-09-02T09:12:00Z", "run_id": 1},
            ]
        },
    )
    requests_mock.get(f"{runs_url}/2/jobs", json={"jobs": [{"id": 2, "completed_at": "2022-09-02T09:07:00Z", "run_id": 2}]})

    records, _, states, error = _read(
        config, "workflow_jobs", state=_state_message("workflow_jobs", {"org/repo": {"completed_at": "2022-09-02T09:10:00Z"}})
    )

    assert error is None
    assert sorted(record["id"] for record in records) == [4, 5]
    assert _requested(requests_mock, "/jobs") == [
        "/repos/org/repo/actions/runs/1/jobs?per_page=100&filter=all"
    ], "run 2 predates the migrated parent cursor"
    assert [request for request in requests_mock.request_history if request.path.endswith("/actions/runs")][-1].headers[
        "X-Airbyte-Window-Start"
    ] == "2022-09-02T09:10:00Z"
    state = states[-1].stream.stream_state.__dict__
    assert state["use_global_cursor"] is True and state["state"] == {"completed_at": "2022-09-02T09:12:00Z"}


def test_workflow_jobs_legacy_state_picks_the_earliest_instant():
    """The global cursor must be the earliest instant across repositories, not the smallest string:
    with offsets, text order and time order differ."""
    from source_github.components import WorkflowJobsLegacyStateMigration

    migration = WorkflowJobsLegacyStateMigration(config={}, parameters={})
    legacy = {"org/a": {"completed_at": "2022-09-02T10:00:00+02:00"}, "org/b": {"completed_at": "2022-09-02T09:00:00Z"}}

    assert migration.should_migrate(legacy)
    migrated = migration.migrate(legacy)

    assert migrated["state"] == {"completed_at": "2022-09-02T10:00:00+02:00"}, "08:00Z is earlier than 09:00Z"
    assert migrated["parent_state"] == {
        "workflow_runs": {"org/a": {"updated_at": "2022-09-02T10:00:00+02:00"}, "org/b": {"updated_at": "2022-09-02T09:00:00Z"}}
    }
    assert migrated["use_global_cursor"] is True


@pytest.mark.parametrize(
    ("response", "expected_ids"),
    [
        pytest.param({"json": {"jobs": [{"id": 1, "completed_at": _AFTER_START, "run_id": 1}]}}, [1], id="valid_single_record"),
        pytest.param({"json": {"jobs": [{"id": 1, "completed_at": None, "run_id": 1}]}}, [], id="valid_record_no_cursor"),
        pytest.param({"json": {"jobs": []}}, [], id="valid_empty_list"),
        pytest.param({"text": "<html>Bad Gateway</html>"}, [], id="html_body"),
        pytest.param({"text": ""}, [], id="empty_body"),
        pytest.param({"json": {"message": "error"}}, [], id="missing_key"),
        pytest.param({"json": {"jobs": None}}, [], id="key_is_none"),
    ],
)
def test_workflow_jobs_tolerate_odd_bodies(response, expected_ids, rate_limit_mock_response, requests_mock):
    """`test_workflow_jobs_parse_response_defensive`, ported."""
    config = _config(_REPO)
    _mock_repository_resolution(requests_mock, _REPO)
    requests_mock.get(f"{_API}/repos/{_REPO}/actions/runs", json={"total_count": 1, "workflow_runs": [_run(1, _AFTER_START, _AFTER_START)]})
    requests_mock.get(f"{_API}/repos/{_REPO}/actions/runs/1/jobs", **response)

    records, statuses, _, error = _read(config, "workflow_jobs")

    assert error is None
    assert statuses[-1] == "COMPLETE"
    assert [record["id"] for record in records] == expected_ids


@pytest.mark.parametrize(
    ("response", "expected_ids"),
    [
        pytest.param({"json": {"total_count": 1, "workflow_runs": [_run(1, _AFTER_START, _AFTER_START)]}}, [1], id="valid_single_record"),
        pytest.param({"json": {"total_count": 0, "workflow_runs": []}}, [], id="valid_empty_list"),
        pytest.param({"text": "<html>Bad Gateway</html>"}, [], id="html_body"),
        pytest.param({"text": ""}, [], id="empty_body"),
        pytest.param({"json": {"message": "error"}}, [], id="missing_key"),
        pytest.param({"json": {"workflow_runs": None}}, [], id="key_is_none"),
    ],
)
def test_workflow_runs_tolerate_odd_bodies(response, expected_ids, rate_limit_mock_response, requests_mock):
    """`test_workflow_runs_parse_response_defensive`, ported."""
    config = _config(_REPO)
    _mock_repository_resolution(requests_mock, _REPO)
    requests_mock.get(f"{_API}/repos/{_REPO}/actions/runs", **response)

    records, statuses, _, error = _read(config, "workflow_runs")

    assert error is None
    assert statuses[-1] == "COMPLETE"
    assert [record["id"] for record in records] == expected_ids
