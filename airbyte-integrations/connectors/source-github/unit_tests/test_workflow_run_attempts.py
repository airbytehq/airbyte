#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import logging
from unittest.mock import patch

import jsonschema
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


def _run(run_id, run_attempt=1, updated_at="2022-02-01T10:05:00Z", created_at="2022-02-01T10:00:00Z", runs_url=RUNS_URL):
    """A record as the *listing* returns it: always the latest attempt of the run.

    `previous_attempt_url` is GitHub's back-link to the attempt before this one, and null on a run
    that was never re-run.
    """
    return {
        "id": run_id,
        "url": f"{runs_url}/{run_id}",
        "run_attempt": run_attempt,
        "previous_attempt_url": f"{runs_url}/{run_id}/attempts/{run_attempt - 1}" if run_attempt > 1 else None,
        "logs_url": f"{runs_url}/{run_id}/logs",
        "jobs_url": f"{runs_url}/{run_id}/jobs",
        "created_at": created_at,
        "updated_at": updated_at,
        "conclusion": "success",
    }


def _attempt(run_id, run_attempt, updated_at, created_at, conclusion="success", has_previous=None, runs_url=RUNS_URL):
    """A record as the *attempt* endpoint returns it: the same shape, scoped to one attempt."""
    if has_previous is None:
        has_previous = run_attempt > 1
    return {
        "id": run_id,
        "url": f"{runs_url}/{run_id}",
        "run_attempt": run_attempt,
        "previous_attempt_url": f"{runs_url}/{run_id}/attempts/{run_attempt - 1}" if has_previous else None,
        "logs_url": f"{runs_url}/{run_id}/attempts/{run_attempt}/logs",
        "jobs_url": f"{runs_url}/{run_id}/attempts/{run_attempt}/jobs",
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
                                "use_global_cursor": False,
                                "states": [{"partition": {"repository": "org/repos"}, "cursor": {"updated_at": cursor_value}}],
                                "state": {"updated_at": cursor_value},
                            }
                        },
                    }
                ),
            ),
        )
    ]


def _mock_repository(requests_mock, full_name="org/repos", repo_id=1, api="https://api.github.com"):
    requests_mock.get(
        f"{api}/repos/{full_name}",
        json={"id": repo_id, "full_name": full_name, "organization": {"login": full_name.split("/")[0]}},
    )


def _mock_runs(requests_mock, runs, full_name="org/repos", api="https://api.github.com", **kwargs):
    requests_mock.get(f"{api}/repos/{full_name}/actions/runs", json={"total_count": len(runs), "workflow_runs": runs}, **kwargs)


def _mock_attempts(requests_mock, attempts, full_name="org/repos", api="https://api.github.com"):
    """Serve each attempt, and refuse to serve the same one indefinitely.

    A static `requests_mock` body turns any regression that breaks out of the attempt chain into a
    hung suite rather than a failing test — no test name, no diff, just a job burning to the CI
    timeout. Cutting the link after a few repeats makes the walk terminate so an assertion can fail.
    """
    for attempt in attempts:
        requests_mock.get(
            f"{api}/repos/{full_name}/actions/runs/{attempt['id']}/attempts/{attempt['run_attempt']}",
            json=_bounded_responder(attempt),
        )


def _bounded_responder(attempt, repeats_before_giving_up=3):
    calls = {"n": 0}

    def responder(request, context):
        calls["n"] += 1
        if calls["n"] <= repeats_before_giving_up:
            return attempt
        return {**attempt, "previous_attempt_url": None}

    return responder


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


@pytest.mark.parametrize(
    "cursor",
    [
        # Strictly above attempt 1's `updated_at` and strictly below attempt 2's. This is the value
        # that discriminates: a client-side filter on the attempt's own cursor drops attempt 1 here,
        # whereas at exactly 10:04:00Z it would survive, because the CDK's filter compares with `>=`.
        pytest.param("2022-02-02T10:30:00Z", id="cursor_between_the_two_attempts"),
        # Far above attempt 1, still below the run's own cursor.
        pytest.param("2022-02-02T11:00:00Z", id="cursor_just_below_the_run_cursor"),
    ],
)
def test_earlier_attempt_survives_an_incremental_boundary(rate_limit_mock_response, requests_mock, cursor):
    """The regression this stream exists to prevent.

    A sync landing between the first attempt finishing (10:04) and the re-run starting (11:00)
    leaves the cursor in between. On the next sync the run comes back because the *run's* cursor
    moved to 11:05, and attempt 1 has to come with it even though the attempt's own `updated_at` is
    below the cursor. Filtering the attempts themselves — which is what the abandoned PR #70305 did —
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

    records, _, _ = _read(CONFIG, state=_state(cursor))

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


def _paged_listing(requests_mock, first_page, second_page):
    """Two listing pages joined by a `Link: rel="next"` header, the way GitHub serves them."""
    page_two = f"{RUNS_URL}?per_page=100&page=2"
    requests_mock.get(
        RUNS_URL,
        [
            {"json": {"total_count": 2, "workflow_runs": first_page}, "headers": {"Link": f'<{page_two}>; rel="next"'}},
            {"json": {"total_count": 2, "workflow_runs": second_page}},
        ],
    )


def _listing_requests(requests_mock):
    return [request for request in requests_mock.request_history if request.path == "/repos/org/repos/actions/runs"]


def test_the_listing_is_never_filtered_server_side(rate_limit_mock_response, requests_mock):
    """GitHub caps this endpoint at 1000 results as soon as `actor`, `branch`, `check_suite_id`,
    `created`, `event`, `head_sha` or `status` is present, and truncates without saying so: page 11
    of a 23352-run repository comes back empty, with `total_count: 0` and no `rel="next"`. Since the
    cursor advances anyway, a filtered listing would drop history that no later sync goes back for.
    """
    _mock_repository(requests_mock)
    _mock_runs(requests_mock, [])

    _read(CONFIG)

    assert set(_listing_requests(requests_mock)[0].qs) == {"per_page"}


def test_pagination_stops_below_the_32_day_rerun_window(rate_limit_mock_response, requests_mock):
    """The legacy pagination break. GitHub refuses to re-run a workflow more than 32 days after it
    was created, so a page that ends below `start_date - 32 days` is the last page worth reading —
    nothing further down the `created_at`-descending listing can have been updated since."""
    _mock_repository(requests_mock)
    config = {**CONFIG, "start_date": "2022-06-15T00:00:00Z"}
    # 2022-05-13 is one day below the window, which opens at 2022-05-14.
    _paged_listing(
        requests_mock,
        [_run(1, updated_at="2022-06-20T10:05:00Z", created_at="2022-05-13T10:00:00Z")],
        [_run(2, updated_at="2022-06-20T10:05:00Z", created_at="2022-01-01T10:00:00Z")],
    )
    _mock_attempts(requests_mock, [_attempt(1, 1, updated_at="2022-06-20T10:05:00Z", created_at="2022-05-13T10:00:00Z")])

    records, _, _ = _read(config)

    assert len(_listing_requests(requests_mock)) == 1
    assert _keys(records) == [(1, 1)]


def test_pagination_continues_while_runs_are_inside_the_window(rate_limit_mock_response, requests_mock):
    _mock_repository(requests_mock)
    config = {**CONFIG, "start_date": "2022-06-15T00:00:00Z"}
    _paged_listing(
        requests_mock,
        [_run(1, updated_at="2022-06-20T10:05:00Z", created_at="2022-05-20T10:00:00Z")],
        [_run(2, updated_at="2022-06-21T10:05:00Z", created_at="2022-05-19T10:00:00Z")],
    )
    _mock_attempts(
        requests_mock,
        [
            _attempt(1, 1, updated_at="2022-06-20T10:05:00Z", created_at="2022-05-20T10:00:00Z"),
            _attempt(2, 1, updated_at="2022-06-21T10:05:00Z", created_at="2022-05-19T10:00:00Z"),
        ],
    )

    records, _, _ = _read(config)

    assert [request.qs.get("page") for request in _listing_requests(requests_mock)] == [None, ["2"]]
    assert _keys(records) == [(1, 1), (2, 1)]


@pytest.mark.parametrize(
    "start_date",
    [
        # `start_date` is optional, and a present-but-null value is reachable through the API,
        # Terraform and embedded use. Legacy paged the whole history in both cases, because its
        # break point stayed None. A bare `config.get('start_date')` in the stop condition would
        # instead render the string "None", read as true, and end the sync after one page.
        pytest.param({}, id="absent"),
        pytest.param({"start_date": None}, id="null"),
    ],
)
def test_without_a_start_date_the_whole_history_is_paged(rate_limit_mock_response, requests_mock, start_date):
    _mock_repository(requests_mock)
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["org/repos"], **start_date}
    _paged_listing(
        requests_mock,
        [_run(1)],
        [_run(2, updated_at="2015-01-01T10:05:00Z", created_at="2015-01-01T10:00:00Z")],
    )
    _mock_attempts(
        requests_mock,
        [
            _attempt(1, 1, updated_at="2022-02-01T10:05:00Z", created_at="2022-02-01T10:00:00Z"),
            _attempt(2, 1, updated_at="2015-01-01T10:05:00Z", created_at="2015-01-01T10:00:00Z"),
        ],
    )

    records, _, _ = _read(config)

    assert len(_listing_requests(requests_mock)) == 2
    assert _keys(records) == [(1, 1), (2, 1)]


def test_discovered_schema_is_valid_and_describes_the_records(rate_limit_mock_response, requests_mock):
    """The inline schema is copied from a Python stream's file, which uses `$ref: user.json`. That
    is a *manifest* reference inside a manifest, and the resolver replaces such a property with the
    bare string, so the published schema silently stops being JSON Schema at all."""
    _mock_repository(requests_mock)
    source = SourceGithub(config=dict(CONFIG), catalog=_catalog(), state=None)

    schema = next(
        stream for stream in source.discover(logging.getLogger("airbyte"), dict(CONFIG)).streams if stream.name == "workflow_run_attempts"
    ).json_schema

    jsonschema.Draft7Validator.check_schema(schema)
    # The four properties that carry a shared `user.json` reference.
    for field in ("actor", "triggering_actor"):
        assert schema["properties"][field]["properties"]["login"]["type"] == ["null", "string"]
    for field in ("repository", "head_repository"):
        assert schema["properties"][field]["properties"]["owner"]["properties"]["login"]["type"] == ["null", "string"]
    # A record the stream really emits has to validate against it, nulls included.
    record = _attempt(1, 1, updated_at="2022-02-01T10:05:00Z", created_at="2022-02-01T10:00:00Z")
    jsonschema.Draft7Validator(schema).validate({**record, "head_commit": None, "referenced_workflows": None, "pull_requests": None})


def test_internal_parent_is_not_exposed_in_the_catalog(rate_limit_mock_response, requests_mock):
    _mock_repository(requests_mock)
    source = SourceGithub(config=dict(CONFIG), catalog=_catalog(), state=None)

    names = [stream.name for stream in source.discover(logging.getLogger("airbyte"), dict(CONFIG)).streams]

    assert "workflow_runs_for_attempts" not in names
    assert "workflow_run_attempts" in names


def test_a_404_partway_through_the_chain_skips_the_rest_of_that_run(rate_limit_mock_response, requests_mock):
    """Documented, deliberate behaviour: GitHub deletes whole runs, and failing instead would wedge
    the stream forever on a run that vanished between the listing and the read. What must not happen
    is the other runs going down with it."""
    _mock_repository(requests_mock)
    _mock_runs(
        requests_mock,
        [
            _run(2, run_attempt=3, updated_at="2022-02-02T12:05:00Z", created_at="2022-02-02T10:00:00Z"),
            _run(1, updated_at="2022-02-01T10:05:00Z"),
        ],
    )
    _mock_attempts(
        requests_mock,
        [
            _attempt(2, 3, updated_at="2022-02-02T12:05:00Z", created_at="2022-02-02T12:00:00Z"),
            _attempt(1, 1, updated_at="2022-02-01T10:05:00Z", created_at="2022-02-01T10:00:00Z"),
        ],
    )
    requests_mock.get(f"{RUNS_URL}/2/attempts/2", status_code=404, json={"message": "Not Found"})

    records, statuses, _ = _read(CONFIG)

    assert statuses[-1] == "COMPLETE"
    assert _keys(records) == [(1, 1), (2, 3)]
    # Attempt 1 is never requested once the chain breaks at attempt 2.
    assert "/repos/org/repos/actions/runs/2/attempts/1" not in _attempt_requests(requests_mock)


def test_a_403_on_one_repository_does_not_fail_the_stream(rate_limit_mock_response, requests_mock):
    """Legacy skipped a 403 on a repo-scoped stream with a warning (streams.py:176-183). The shared
    manifest error handler fails on 403 so `check` can report bad scopes; these two streams override
    it, because one repository the token cannot read Actions for must not take the others down."""
    _mock_repository(requests_mock, "org/repos")
    _mock_repository(requests_mock, "org/other", repo_id=2)
    _mock_runs(requests_mock, [_run(1)], full_name="org/repos")
    _mock_attempts(requests_mock, [_attempt(1, 1, updated_at="2022-02-01T10:05:00Z", created_at="2022-02-01T10:00:00Z")])
    requests_mock.get(
        "https://api.github.com/repos/org/other/actions/runs",
        status_code=403,
        json={"message": "Resource not accessible by personal access token"},
    )
    config = {**CONFIG, "repositories": ["org/repos", "org/other"]}

    records, statuses, _ = _read(config)

    assert statuses[-1] == "COMPLETE"
    assert _keys(records) == [(1, 1)]


def test_a_200_that_is_not_a_run_is_not_emitted(rate_limit_mock_response, requests_mock):
    """`field_path: []` emits the whole body, and GitHub answers 200 with a `{"message": ...}`
    envelope on some redirect and deprecation paths. Without the record filter that lands in the
    destination as a row whose entire primary key is null."""
    _mock_repository(requests_mock)
    _mock_runs(requests_mock, [_run(1)])
    requests_mock.get(f"{RUNS_URL}/1/attempts/1", json={"message": "Moved Permanently", "url": "https://api.github.com/x"})

    records, statuses, _ = _read(CONFIG)

    assert records == []
    assert statuses[-1] == "COMPLETE"


def test_a_run_without_run_attempt_is_read_as_a_single_attempt(rate_limit_mock_response, requests_mock):
    """`run_attempt` is not required by GitHub's workflow-run schema, and the substream router
    yields None for a missing extra field, which Jinja renders as the literal "None" — the request
    would 404 and the run would be dropped whole."""
    _mock_repository(requests_mock)
    run = _run(1)
    del run["run_attempt"]
    _mock_runs(requests_mock, [run])
    _mock_attempts(requests_mock, [_attempt(1, 1, updated_at="2022-02-01T10:05:00Z", created_at="2022-02-01T10:00:00Z")])

    records, _, _ = _read(CONFIG)

    assert _attempt_requests(requests_mock) == ["/repos/org/repos/actions/runs/1/attempts/1"]
    assert _keys(records) == [(1, 1)]


def test_each_repository_is_partitioned_and_checkpointed_separately(rate_limit_mock_response, requests_mock):
    _mock_repository(requests_mock, "org/repos")
    _mock_repository(requests_mock, "org/other", repo_id=2)
    _mock_runs(requests_mock, [_run(1)], full_name="org/repos")
    other_runs_url = "https://api.github.com/repos/org/other/actions/runs"
    _mock_runs(
        requests_mock,
        [_run(5, updated_at="2022-03-01T10:05:00Z", created_at="2022-03-01T10:00:00Z", runs_url=other_runs_url)],
        full_name="org/other",
    )
    _mock_attempts(requests_mock, [_attempt(1, 1, updated_at="2022-02-01T10:05:00Z", created_at="2022-02-01T10:00:00Z")], "org/repos")
    _mock_attempts(
        requests_mock,
        [_attempt(5, 1, updated_at="2022-03-01T10:05:00Z", created_at="2022-03-01T10:00:00Z", runs_url=other_runs_url)],
        "org/other",
    )
    config = {**CONFIG, "repositories": ["org/repos", "org/other"]}

    records, _, states = _read(config)

    assert _keys(records) == [(1, 1), (5, 1)]
    parent = states[-1].parent_state["workflow_runs_for_attempts"]
    assert sorted(entry["partition"]["repository"] for entry in parent["states"]) == ["org/other", "org/repos"]


def test_every_request_stays_on_a_github_enterprise_host(rate_limit_mock_response, requests_mock):
    """The attempt path is built from the parent record's absolute `url`, so it follows whatever
    host GitHub reports rather than `url_base`. Making that path relative would break GHES."""
    api = "https://ghe.example.com/api/v3"
    quota = {"limit": 5000, "used": 0, "remaining": 5000, "reset": 4070908800}
    requests_mock.get(f"{api}/rate_limit", json={"resources": {"core": dict(quota), "graphql": dict(quota)}})
    _mock_repository(requests_mock, api=api)
    ghe_runs_url = f"{api}/repos/org/repos/actions/runs"
    _mock_runs(requests_mock, [_run(1, runs_url=ghe_runs_url)], api=api)
    requests_mock.get(
        f"{ghe_runs_url}/1/attempts/1",
        json=_attempt(1, 1, "2022-02-01T10:05:00Z", "2022-02-01T10:00:00Z", runs_url=ghe_runs_url),
    )
    config = {**CONFIG, "api_url": api}

    records, _, _ = _read(config)

    assert _keys(records) == [(1, 1)]
    assert {request.hostname for request in requests_mock.request_history} == {"ghe.example.com"}


def test_the_state_the_connector_emits_can_be_fed_back_to_it(rate_limit_mock_response, requests_mock):
    """Every other incremental test here builds state by hand. This one uses what sync 1 actually
    emitted, so a change in the emitted shape cannot pass unnoticed."""
    _mock_repository(requests_mock)
    _mock_runs(requests_mock, [_run(1), _run(3, updated_at="2022-01-15T10:05:00Z", created_at="2022-01-15T10:00:00Z")])
    _mock_attempts(
        requests_mock,
        [
            _attempt(1, 1, updated_at="2022-02-01T10:05:00Z", created_at="2022-02-01T10:00:00Z"),
            _attempt(3, 1, updated_at="2022-01-15T10:05:00Z", created_at="2022-01-15T10:00:00Z"),
        ],
    )

    first_records, _, states = _read(CONFIG)
    emitted = AirbyteStateMessage(
        type=AirbyteStateType.STREAM,
        stream=AirbyteStreamState(stream_descriptor=StreamDescriptor(name="workflow_run_attempts"), stream_state=states[-1]),
    )
    second_records, statuses, _ = _read(CONFIG, state=[emitted])

    assert _keys(first_records) == [(1, 1), (3, 1)]
    assert statuses[-1] == "COMPLETE"
    # Run 3, comfortably below the cursor, is not re-read. Run 1 sits exactly *on* it and is:
    # `ConcurrentCursor.should_be_synced` is inclusive at both ends, where the legacy
    # `SemiIncrementalMixin` compared with a strict `>`. Deduplicating destinations absorb it; an
    # append destination sees one extra copy of the newest run per repository per sync.
    assert _keys(second_records) == [(1, 1)]


def _looping_attempt_responder(run_url, attempt_number, link, gives_up_after):
    """An attempt endpoint that keeps pointing the walk back at itself, then relents.

    Bounded on purpose. A `requests_mock` payload that loops forever turns a broken loop guard into
    a hung suite - no failing test name, no diff, just a job that burns to the CI timeout. Relenting
    after `gives_up_after` calls lets the guard's absence show up as a request count instead.
    """
    calls = {"n": 0}

    def responder(request, context):
        calls["n"] += 1
        body = _attempt(2, attempt_number, updated_at="2022-02-02T11:05:00Z", created_at="2022-02-02T11:00:00Z")
        body["previous_attempt_url"] = link if calls["n"] <= gives_up_after else None
        return body

    return responder


@pytest.mark.parametrize(
    "broken_link",
    [
        # A link that points back at the attempt that produced it.
        pytest.param(lambda url, n: f"{url}/attempts/{n}", id="self_referential"),
        # A link that climbs instead of descending, which oscillates between two attempts.
        pytest.param(lambda url, n: f"{url}/attempts/{n + 1}", id="ascending"),
        # An anchored regex would match neither of these and wave the link through, which is
        # precisely backwards: they are the malformed shapes the guard exists to catch.
        pytest.param(lambda url, n: f"{url}/attempts/{n}/", id="trailing_slash"),
        pytest.param(lambda url, n: f"{url}/attempts/{n}?per_page=1", id="query_string"),
        pytest.param(lambda url, n: f"{url}/attempts/{n}#frag", id="fragment"),
        # A link that leaves the run entirely.
        pytest.param(lambda url, n: "https://api.github.com/repos/org/repos/actions/runs/999/attempts/1", id="different_run"),
        # A link with no attempt number to compare at all.
        pytest.param(lambda url, n: f"{url}/attempts/abc", id="non_numeric"),
    ],
)
def test_a_chain_that_does_not_descend_is_cut_off(rate_limit_mock_response, requests_mock, broken_link):
    """`DefaultPaginator` has no page cap and `stop_condition` never sees the previous page token,
    so a `previous_attempt_url` that fails to descend would page until the platform kills the sync.
    The guard stops on positive proof of non-descent."""
    _mock_repository(requests_mock)
    _mock_runs(requests_mock, [_run(2, run_attempt=2, updated_at="2022-02-02T11:05:00Z", created_at="2022-02-02T10:00:00Z")])
    run_url = f"{RUNS_URL}/2"
    requests_mock.get(f"{run_url}/attempts/2", json=_looping_attempt_responder(run_url, 2, broken_link(run_url, 2), 5))
    requests_mock.get(f"{run_url}/attempts/3", json=_looping_attempt_responder(run_url, 3, broken_link(run_url, 3), 5))
    _mock_attempts(requests_mock, [_attempt(2, 1, updated_at="2022-02-02T10:04:00Z", created_at="2022-02-02T10:00:00Z")])

    records, statuses, _ = _read(CONFIG)

    assert statuses[-1] == "COMPLETE"
    assert _attempt_requests(requests_mock) == ["/repos/org/repos/actions/runs/2/attempts/2"]
    assert _keys(records) == [(2, 2)]


@pytest.mark.parametrize(
    "suffix",
    [
        pytest.param("", id="bare"),
        # The regex deliberately is not anchored on the end of the string. These descend correctly
        # and must be followed; an anchored pattern would read them as unparseable and stop.
        pytest.param("/", id="trailing_slash"),
        pytest.param("?per_page=1", id="query_string"),
        pytest.param("#frag", id="fragment"),
    ],
)
def test_a_descending_link_is_followed_whatever_it_is_suffixed_with(rate_limit_mock_response, requests_mock, suffix):
    _mock_repository(requests_mock)
    _mock_runs(requests_mock, [_run(2, run_attempt=2, updated_at="2022-02-02T11:05:00Z", created_at="2022-02-02T10:00:00Z")])
    requests_mock.get(
        f"{RUNS_URL}/2/attempts/2",
        json={
            **_attempt(2, 2, updated_at="2022-02-02T11:05:00Z", created_at="2022-02-02T11:00:00Z"),
            "previous_attempt_url": f"{RUNS_URL}/2/attempts/1{suffix}",
        },
    )
    # Registered at the suffixed URL, because following the link is exactly what is under test.
    # `requests` keeps the suffix on `PreparedRequest.url`, which is what `requests_mock` matches
    # on, and drops the fragment from `path_url`, which is what goes on the wire — so the fragment
    # case really does reach the same endpoint as the bare one. What differs, and what this pins,
    # is the string the stop condition is handed: anchoring the regex kills three of these four.
    requests_mock.get(
        f"{RUNS_URL}/2/attempts/1{suffix}",
        json=_attempt(2, 1, updated_at="2022-02-02T10:04:00Z", created_at="2022-02-02T10:00:00Z"),
    )

    records, statuses, _ = _read(CONFIG)

    assert statuses[-1] == "COMPLETE"
    assert _keys(records) == [(2, 1), (2, 2)]


def test_a_non_integer_run_attempt_is_skipped_and_does_not_truncate_the_chain(rate_limit_mock_response, requests_mock):
    """A string cannot be half of an integer primary key, and it cannot be compared with `<` either.
    `JinjaInterpolation._eval` swallows a TypeError and hands back the raw template, which
    `InterpolatedBoolean` reads as true — so a stop condition that can raise is a stop condition
    that silently ends the walk one attempt in."""
    _mock_repository(requests_mock)
    _mock_runs(requests_mock, [_run(2, run_attempt=2, updated_at="2022-02-02T11:05:00Z", created_at="2022-02-02T10:00:00Z")])
    requests_mock.get(
        f"{RUNS_URL}/2/attempts/2",
        json={**_attempt(2, 2, updated_at="2022-02-02T11:05:00Z", created_at="2022-02-02T11:00:00Z"), "run_attempt": "2"},
    )
    _mock_attempts(requests_mock, [_attempt(2, 1, updated_at="2022-02-02T10:04:00Z", created_at="2022-02-02T10:00:00Z")])

    records, statuses, _ = _read(CONFIG)

    assert statuses[-1] == "COMPLETE"
    # The unkeyable record is dropped; attempt 1 behind it is still reached.
    assert _keys(records) == [(2, 1)]
    assert len(_attempt_requests(requests_mock)) == 2


def test_an_attempt_payload_without_run_attempt_is_skipped_but_does_not_end_the_walk(rate_limit_mock_response, requests_mock):
    """`run_attempt` is half the primary key and is not a required field of GitHub's schema. The
    attempt number is only knowable from the request path, which no transformation can see, so
    defaulting it to 1 would label a mid-chain attempt as attempt 1 and overwrite the real one on a
    deduplicating destination. The unkeyable record is dropped instead — and only that record."""
    _mock_repository(requests_mock)
    _mock_runs(requests_mock, [_run(2, run_attempt=2, updated_at="2022-02-02T11:05:00Z", created_at="2022-02-02T10:00:00Z")])
    unkeyable = _attempt(2, 2, updated_at="2022-02-02T11:05:00Z", created_at="2022-02-02T11:00:00Z")
    del unkeyable["run_attempt"]
    requests_mock.get(f"{RUNS_URL}/2/attempts/2", json=unkeyable)
    _mock_attempts(requests_mock, [_attempt(2, 1, updated_at="2022-02-02T10:04:00Z", created_at="2022-02-02T10:00:00Z")])

    records, statuses, _ = _read(CONFIG)

    assert statuses[-1] == "COMPLETE"
    assert _keys(records) == [(2, 1)]
    # The chain was still followed past the record that could not be keyed.
    assert len(_attempt_requests(requests_mock)) == 2


def test_the_break_fires_on_a_page_whose_records_are_all_older_than_the_cursor(rate_limit_mock_response, requests_mock):
    """The case the break exists for, and the one an obvious implementation gets wrong.

    `SimpleRetriever` sets `last_record` from records that survived the record selector, and this
    stream's selector filters on the cursor. Deep pages of an old listing therefore contribute no
    surviving record at all, so a stop condition reading `last_record` never fires and the sync
    pages the repository's whole history. The condition reads the raw page tail instead.
    """
    _mock_repository(requests_mock)
    config = {**CONFIG, "start_date": "2022-06-15T00:00:00Z"}
    # Everything on page 1 is far below the cursor, so the record selector drops all of it.
    _paged_listing(
        requests_mock,
        [_run(1, updated_at="2021-01-02T10:05:00Z", created_at="2021-01-01T10:00:00Z")],
        [_run(2, updated_at="2020-01-02T10:05:00Z", created_at="2020-01-01T10:00:00Z")],
    )

    records, statuses, _ = _read(config, state=_state("2022-07-01T00:00:00Z"))

    assert statuses[-1] == "COMPLETE"
    assert records == []
    assert len(_listing_requests(requests_mock)) == 1


def test_a_page_tail_without_a_usable_created_at_does_not_end_the_listing(rate_limit_mock_response, requests_mock):
    """`JinjaInterpolation._eval` swallows a TypeError and returns the raw template, which
    `InterpolatedBoolean` reads as true — so comparing a null `created_at` with `<` would stop the
    walk and lose every page behind it, on a green sync."""
    _mock_repository(requests_mock)
    config = {**CONFIG, "start_date": "2022-06-15T00:00:00Z"}
    head = _run(1, updated_at="2022-06-20T10:05:00Z", created_at="2022-05-20T10:00:00Z")
    head["created_at"] = None
    _paged_listing(requests_mock, [head], [_run(2, updated_at="2022-06-21T10:05:00Z", created_at="2022-05-19T10:00:00Z")])
    _mock_attempts(
        requests_mock,
        [
            _attempt(1, 1, updated_at="2022-06-20T10:05:00Z", created_at="2022-05-20T10:00:00Z"),
            _attempt(2, 1, updated_at="2022-06-21T10:05:00Z", created_at="2022-05-19T10:00:00Z"),
        ],
    )

    records, _, _ = _read(config)

    assert len(_listing_requests(requests_mock)) == 2
    assert (2, 1) in _keys(records)


@pytest.mark.parametrize(
    "endpoint",
    [
        pytest.param("/repos/org/repos/actions/runs", id="run_listing"),
        pytest.param("/repos/org/repos/actions/runs/1/attempts/1", id="attempt"),
    ],
)
@patch("time.sleep")
def test_a_secondary_rate_limit_is_waited_out_not_skipped(sleep_mock, rate_limit_mock_response, requests_mock, endpoint):
    """GitHub reports a secondary rate limit as a 403, and leaves `X-RateLimit-Remaining` positive.

    Both new error handlers skip a 403 instead of failing, which is what a repository the token
    cannot read Actions for needs — but the rate-limit filters have to stay ahead of that skip in
    the filter list, or a throttled response is read as "no access" and the page is dropped for
    good while the cursor advances past it. Three hand-maintained copies of that ordering exist;
    this is what keeps them honest.
    """
    _mock_repository(requests_mock)
    throttled = {
        "status_code": 403,
        "headers": {"X-RateLimit-Remaining": "4999", "X-RateLimit-Reset": "0"},
        "json": {"message": "You have exceeded a secondary rate limit. Please wait a few minutes before you try again."},
    }
    listing = {"json": {"total_count": 1, "workflow_runs": [_run(1)]}}
    attempt = {"json": _attempt(1, 1, updated_at="2022-02-01T10:05:00Z", created_at="2022-02-01T10:00:00Z")}
    requests_mock.get(RUNS_URL, [throttled, listing] if endpoint.endswith("runs") else [listing])
    requests_mock.get(f"{RUNS_URL}/1/attempts/1", [throttled, attempt] if endpoint.endswith("1") else [attempt])

    records, statuses, _ = _read(CONFIG)

    assert statuses[-1] == "COMPLETE"
    assert _keys(records) == [(1, 1)]
    assert sleep_mock.called


def test_a_403_on_one_attempt_does_not_fail_the_stream(rate_limit_mock_response, requests_mock):
    """A fine-grained token can list a repository's runs and still be denied `Actions: read` on
    one of them. The shared handler would turn that into a `config_error` that ends the sync."""
    _mock_repository(requests_mock)
    _mock_runs(requests_mock, [_run(1), _run(2, updated_at="2022-02-03T10:05:00Z", created_at="2022-02-03T10:00:00Z")])
    _mock_attempts(requests_mock, [_attempt(1, 1, updated_at="2022-02-01T10:05:00Z", created_at="2022-02-01T10:00:00Z")])
    requests_mock.get(f"{RUNS_URL}/2/attempts/1", status_code=403, json={"message": "Resource not accessible by integration"})

    records, statuses, _ = _read(CONFIG)

    assert statuses[-1] == "COMPLETE"
    assert _keys(records) == [(1, 1)]


@pytest.mark.parametrize(
    "throttled_endpoint",
    [
        pytest.param("listing", id="run_listing"),
        pytest.param("attempt", id="attempt"),
    ],
)
@patch("time.sleep")
def test_a_200_carrying_retry_after_is_kept(sleep_mock, rate_limit_mock_response, requests_mock, throttled_endpoint):
    """A proxy, a CDN or GHES can throttle on its own account and still answer 200. Without the
    `SUCCESS` short-circuit ahead of the rate-limit filters, that response is classified
    RATE_LIMITED, its record discarded, and the stream fails once retries run out. Both handlers
    carry their own copy of that filter, so both endpoints are exercised."""
    _mock_repository(requests_mock)
    throttle = {"Retry-After": "120"}
    _mock_runs(
        requests_mock,
        [_run(1)],
        headers=throttle if throttled_endpoint == "listing" else {},
    )
    requests_mock.get(
        f"{RUNS_URL}/1/attempts/1",
        json=_attempt(1, 1, updated_at="2022-02-01T10:05:00Z", created_at="2022-02-01T10:00:00Z"),
        headers=throttle if throttled_endpoint == "attempt" else {},
    )

    records, statuses, _ = _read(CONFIG)

    assert statuses[-1] == "COMPLETE"
    assert _keys(records) == [(1, 1)]
    assert _attempt_requests(requests_mock) == ["/repos/org/repos/actions/runs/1/attempts/1"]
    # `time.sleep` is patched so that losing the short-circuit fails in seconds rather than after
    # the full retry ladder — a ten-minute red build reads as a hang, not as a regression.
    assert not sleep_mock.called


def test_a_404_on_the_run_listing_skips_that_repository(rate_limit_mock_response, requests_mock):
    """A repository deleted or renamed between resolution and read must not fail the others."""
    _mock_repository(requests_mock, "org/repos")
    _mock_repository(requests_mock, "org/other", repo_id=2)
    _mock_runs(requests_mock, [_run(1)], full_name="org/repos")
    _mock_attempts(requests_mock, [_attempt(1, 1, updated_at="2022-02-01T10:05:00Z", created_at="2022-02-01T10:00:00Z")])
    requests_mock.get("https://api.github.com/repos/org/other/actions/runs", status_code=404, json={"message": "Not Found"})

    records, statuses, _ = _read({**CONFIG, "repositories": ["org/repos", "org/other"]})

    assert statuses[-1] == "COMPLETE"
    assert _keys(records) == [(1, 1)]


def test_the_break_reads_the_oldest_run_on_the_page_not_the_newest(rate_limit_mock_response, requests_mock):
    """The listing is `created_at` descending, so only the tail of a page says anything about
    whether the next page is still inside the re-run window. Reading the head instead would page on
    past the window, and single-record pages cannot tell the two apart."""
    _mock_repository(requests_mock)
    config = {**CONFIG, "start_date": "2022-06-15T00:00:00Z"}
    # The window opens at 2022-05-14. The head of page 1 is inside it, the tail is below.
    _paged_listing(
        requests_mock,
        [
            _run(1, updated_at="2022-06-20T10:05:00Z", created_at="2022-06-01T10:00:00Z"),
            _run(2, updated_at="2022-06-21T10:05:00Z", created_at="2022-05-13T10:00:00Z"),
        ],
        [_run(3, updated_at="2022-06-22T10:05:00Z", created_at="2022-01-01T10:00:00Z")],
    )
    _mock_attempts(
        requests_mock,
        [
            _attempt(1, 1, updated_at="2022-06-20T10:05:00Z", created_at="2022-06-01T10:00:00Z"),
            _attempt(2, 1, updated_at="2022-06-21T10:05:00Z", created_at="2022-05-13T10:00:00Z"),
        ],
    )

    records, _, _ = _read(config)

    assert len(_listing_requests(requests_mock)) == 1
    assert _keys(records) == [(1, 1), (2, 1)]


@pytest.mark.parametrize(
    "tail_created_at,expected_pages",
    [
        # The window is `start_date - 32 days` = 2022-05-14. A tail on 2022-05-15 is inside it, and
        # would be outside a 30-day window — so this case is what pins the constant itself.
        pytest.param("2022-05-15T10:00:00Z", 2, id="inside_a_32_day_window_but_not_a_30_day_one"),
        # Exactly on the boundary. The comparison is strict, so this page is not the last one.
        pytest.param("2022-05-14T00:00:00Z", 2, id="exactly_on_the_boundary"),
        # One second below it.
        pytest.param("2022-05-13T23:59:59Z", 1, id="one_second_below_the_boundary"),
    ],
)
def test_the_break_is_exactly_32_days_wide(rate_limit_mock_response, requests_mock, tail_created_at, expected_pages):
    _mock_repository(requests_mock)
    config = {**CONFIG, "start_date": "2022-06-15T00:00:00Z"}
    _paged_listing(
        requests_mock,
        [_run(1, updated_at="2021-01-01T10:05:00Z", created_at=tail_created_at)],
        [_run(2, updated_at="2021-01-01T10:05:00Z", created_at="2020-01-01T10:00:00Z")],
    )

    _read(config)

    assert len(_listing_requests(requests_mock)) == expected_pages


def test_the_discovered_schema_covers_exactly_the_attempt_payload(rate_limit_mock_response, requests_mock):
    """The inline schema was hand-copied from the `workflow_runs` stream's file, and the attempt
    endpoint is a different endpoint. CAT gives this stream no live coverage — the acceptance
    repository has no workflow runs at all — so nothing else would notice a property being dropped
    or a new one going undeclared."""
    _mock_repository(requests_mock)
    source = SourceGithub(config=dict(CONFIG), catalog=_catalog(), state=None)

    schema = next(
        stream for stream in source.discover(logging.getLogger("airbyte"), dict(CONFIG)).streams if stream.name == "workflow_run_attempts"
    ).json_schema

    # Verified against a live `GET /actions/runs/{id}/attempts/{n}` response: the attempt endpoint
    # returns this key set exactly, no more and no less.
    assert set(schema["properties"]) == {
        "actor",
        "artifacts_url",
        "cancel_url",
        "check_suite_id",
        "check_suite_node_id",
        "check_suite_url",
        "conclusion",
        "created_at",
        "display_title",
        "event",
        "head_branch",
        "head_commit",
        "head_repository",
        "head_sha",
        "html_url",
        "id",
        "jobs_url",
        "logs_url",
        "name",
        "node_id",
        "path",
        "previous_attempt_url",
        "pull_requests",
        "referenced_workflows",
        "repository",
        "rerun_url",
        "run_attempt",
        "run_number",
        "run_started_at",
        "status",
        "triggering_actor",
        "updated_at",
        "url",
        "workflow_id",
        "workflow_url",
    }
