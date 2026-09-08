#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import logging

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
    for attempt in attempts:
        requests_mock.get(f"{api}/repos/{full_name}/actions/runs/{attempt['id']}/attempts/{attempt['run_attempt']}", json=attempt)


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


@pytest.mark.parametrize(
    "broken_link",
    [
        # A link that points back at the attempt that produced it.
        pytest.param(lambda url, n: f"{url}/attempts/{n}", id="self_referential"),
        # A link that climbs instead of descending, which oscillates between two attempts.
        pytest.param(lambda url, n: f"{url}/attempts/{n + 1}", id="ascending"),
    ],
)
def test_a_chain_that_does_not_descend_is_cut_off(rate_limit_mock_response, requests_mock, broken_link):
    """`DefaultPaginator` has no page cap and `stop_condition` never sees the previous page token,
    so a `previous_attempt_url` that fails to descend would page until the platform kills the sync.
    The guard stops on positive proof of non-descent."""
    _mock_repository(requests_mock)
    _mock_runs(requests_mock, [_run(2, run_attempt=3, updated_at="2022-02-02T12:05:00Z", created_at="2022-02-02T10:00:00Z")])
    run_url = f"{RUNS_URL}/2"
    for attempt_number in (2, 3):
        requests_mock.get(
            f"{run_url}/attempts/{attempt_number}",
            json={
                **_attempt(2, attempt_number, updated_at="2022-02-02T12:05:00Z", created_at="2022-02-02T12:00:00Z"),
                "previous_attempt_url": broken_link(run_url, attempt_number),
            },
        )

    records, statuses, _ = _read(CONFIG)

    assert statuses[-1] == "COMPLETE"
    assert len(_attempt_requests(requests_mock)) <= 2
    assert {record["id"] for record in records} == {2}


def test_a_non_integer_run_attempt_does_not_truncate_the_chain(rate_limit_mock_response, requests_mock):
    """A string cannot be compared with `<` against an integer. `JinjaInterpolation._eval` swallows
    a TypeError and hands back the raw template, which `InterpolatedBoolean` reads as true — so a
    stop condition that can raise is a stop condition that silently ends the walk one attempt in."""
    _mock_repository(requests_mock)
    _mock_runs(requests_mock, [_run(2, run_attempt=2, updated_at="2022-02-02T11:05:00Z", created_at="2022-02-02T10:00:00Z")])
    requests_mock.get(
        f"{RUNS_URL}/2/attempts/2",
        json={**_attempt(2, 2, updated_at="2022-02-02T11:05:00Z", created_at="2022-02-02T11:00:00Z"), "run_attempt": "2"},
    )
    _mock_attempts(requests_mock, [_attempt(2, 1, updated_at="2022-02-02T10:04:00Z", created_at="2022-02-02T10:00:00Z")])

    records, statuses, _ = _read(CONFIG)

    assert statuses[-1] == "COMPLETE"
    assert _keys(records) == [(2, 1), (2, 2)]


def test_an_attempt_payload_without_run_attempt_still_gets_a_key(rate_limit_mock_response, requests_mock):
    """`run_attempt` is half the primary key and is not a required field of GitHub's schema. Without
    the transformation the record is emitted with half a null key, or dropped outright."""
    _mock_repository(requests_mock)
    _mock_runs(requests_mock, [_run(1)])
    attempt = _attempt(1, 1, updated_at="2022-02-01T10:05:00Z", created_at="2022-02-01T10:00:00Z")
    del attempt["run_attempt"]
    requests_mock.get(f"{RUNS_URL}/1/attempts/1", json=attempt)

    records, statuses, _ = _read(CONFIG)

    assert statuses[-1] == "COMPLETE"
    assert _keys(records) == [(1, 1)]
