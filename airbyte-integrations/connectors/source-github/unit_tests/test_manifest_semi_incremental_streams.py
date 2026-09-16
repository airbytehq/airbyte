#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Behavior of the semi-incremental REST streams migrated to the manifest (Step 5).

These nine streams were the `SemiIncrementalMixin` group: `GithubStream` sliced on the resolved
repository list, requested `repos/{repository}/<endpoint>` with no cursor parameter, paginated on
the `rel="next"` link header, stamped `repository` onto every record and filtered in Python —
keeping records newer than `max(start_date, per-repository state)`. Two of them (`pull_requests`,
`issue_milestones`) are served most-recent-first and also stopped paginating at the first record
older than that point; the other seven read every page. Each test below asserts parity with that
implementation, or pins the deliberate divergence where the CDK cannot reproduce it.

The shared repo-scoped error contract (404/403/409/410 skip the repository, 502 fails the stream,
secondary-limit 403 is retried) is pinned once in `test_manifest_repo_scoped_streams.py`; these
streams reuse the same `skip_inaccessible_error_handler`, so only the 410 `projects` case — the
one this group actually hits — is re-asserted here.
"""

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


# (stream name, endpoint under repos/{repository}/, cursor field, query params beyond per_page)
MIGRATED_STREAMS = [
    ("events", "events", "created_at", {}),
    ("pull_requests", "pulls", "updated_at", {"state": "all", "sort": "updated", "direction": "desc"}),
    ("commit_comments", "comments", "updated_at", {}),
    ("issue_milestones", "milestones", "updated_at", {"state": "all", "sort": "updated", "direction": "desc"}),
    ("stargazers", "stargazers", "starred_at", {}),
    ("projects", "projects", "updated_at", {"state": "all"}),
    ("issue_events", "issues/events", "created_at", {}),
    ("deployments", "deployments", "updated_at", {}),
    ("workflows", "actions/workflows", "updated_at", {}),
]
STREAM_PARAMS = [pytest.param(*stream, id=stream[0]) for stream in MIGRATED_STREAMS]
# Legacy `is_sorted = "desc"`: requested newest-first, pagination stopped at the first stale record.
DATA_FEED_STREAMS = {"pull_requests", "issue_milestones"}
CLIENT_SIDE_PARAMS = [pytest.param(*stream, id=stream[0]) for stream in MIGRATED_STREAMS if stream[0] not in DATA_FEED_STREAMS]
DATA_FEED_PARAMS = [pytest.param(*stream, id=stream[0]) for stream in MIGRATED_STREAMS if stream[0] in DATA_FEED_STREAMS]
# `GithubStream.large_stream`: `per_page` comes from `page_size_for_large_streams` (default 10) rather than 100.
LARGE_STREAMS = {"pull_requests"}
EXTRA_ACCEPT_HEADERS = {
    "stargazers": "application/vnd.github.v3.star+json",
    "projects": "application/vnd.github.inertia-preview+json",
}

_TOKEN_CONFIG = {"credentials": {"personal_access_token": "token"}}
_START_DATE = "2022-01-01T00:00:00Z"
_BEFORE_START = "2021-12-31T00:00:00Z"
_AFTER_START = "2022-06-01T00:00:00Z"
_LATER = "2022-07-01T00:00:00Z"
_LATEST = "2022-08-01T00:00:00Z"


def _config(*repositories, **overrides):
    return {**_TOKEN_CONFIG, "repositories": list(repositories), "start_date": _START_DATE, **overrides}


def _catalog(*stream_names):
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name=stream_name,
                    json_schema={},
                    supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
                ),
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.append,
            )
            for stream_name in stream_names
        ]
    )


def _read_messages(config, *stream_names, state=None):
    catalog = _catalog(*stream_names)
    source = SourceGithub(config=dict(config), catalog=catalog, state=state)
    messages, error = [], None
    try:
        # Appended one at a time so the messages emitted before a failure are still available.
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


def _mock_repository_resolution(requests_mock, *repositories):
    """Explicit `org/repo` entries resolve through the manifest's `repository_stats` stream."""
    for index, repository in enumerate(repositories, start=1):
        requests_mock.get(
            f"https://api.github.com/repos/{repository}",
            json={"id": index, "full_name": repository, "organization": {"login": repository.split("/")[0]}},
        )


def _legacy_state(stream_name, cursor_field, **per_repository_cursor):
    """The state shape the Python streams wrote: `{repository: {cursor_field: ...}}`."""
    return [
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name=stream_name),
                stream_state=AirbyteStateBlob({repository: {cursor_field: cursor} for repository, cursor in per_repository_cursor.items()}),
            ),
        )
    ]


def _state_message(stream_name, state):
    return [
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(stream_descriptor=StreamDescriptor(name=stream_name), stream_state=AirbyteStateBlob(state)),
        )
    ]


def _partition_cursors(state_message):
    """`{repository: cursor value}` out of a per-partition state message."""
    state = state_message.stream.stream_state.__dict__
    return {entry["partition"]["repository"]: next(iter(entry["cursor"].values())) for entry in state["states"]}


def _stored_cursor(stream_name, value):
    """The value a `...Z` timestamp is stored as. `workflows` writes state with `%z` (see the
    manifest on why), so its UTC values come back as `+0000`; every other stream keeps `Z`."""
    return value.replace("Z", "+0000") if stream_name == "workflows" else value


def _next_link(url):
    return {"Link": f'<{url}>; rel="next"'}


def _listings(requests_mock, endpoint):
    return [request for request in requests_mock.request_history if request.path.endswith(f"/{endpoint}")]


def _record(stream_name, record_id, cursor_field, cursor):
    """A GitHub payload record for `stream_name` with the fields the manifest reads."""
    if stream_name == "stargazers":
        return {"starred_at": cursor, "user": {"id": record_id}}
    record = {"id": record_id, cursor_field: cursor}
    if stream_name == "pull_requests":
        record.update({"number": record_id, "head": {"repo": {"id": 100 + record_id}}, "base": {"repo": {"id": 200 + record_id}}})
    return record


def _body(stream_name, records):
    """`workflows` is the one listing wrapped in an envelope."""
    if stream_name == "workflows":
        return {"total_count": len(records), "workflows": records}
    return records


def _ids(stream_name, records):
    key = "user_id" if stream_name == "stargazers" else "id"
    return [record[key] for record in records]


@pytest.mark.parametrize(("stream_name", "endpoint", "cursor_field", "params"), STREAM_PARAMS)
def test_stream_reads_every_repository_and_injects_repository(
    stream_name, endpoint, cursor_field, params, rate_limit_mock_response, requests_mock
):
    config = _config("airbytehq/airbyte", "docker/compose")
    _mock_repository_resolution(requests_mock, *config["repositories"])
    for repository in config["repositories"]:
        requests_mock.get(
            f"https://api.github.com/repos/{repository}/{endpoint}",
            json=_body(stream_name, [_record(stream_name, 1, cursor_field, _AFTER_START), _record(stream_name, 2, cursor_field, _LATER)]),
        )

    records, statuses, _, error = _read(config, stream_name)

    assert error is None
    assert statuses[-1] == "COMPLETE"
    assert len(records) == 4
    # `repository` is absent from the GitHub payload, so it can only come from the manifest's
    # AddFields transformation — the replacement for `GithubStream.transform` (streams.py).
    assert sorted({record["repository"] for record in records}) == ["airbytehq/airbyte", "docker/compose"]


@pytest.mark.parametrize(("stream_name", "endpoint", "cursor_field", "params"), STREAM_PARAMS)
def test_request_shape_matches_legacy(stream_name, endpoint, cursor_field, params, rate_limit_mock_response, requests_mock):
    """Path, `per_page`, the per-stream base params and the two preview `Accept` headers, exactly
    as `GithubStream.request_params`/`request_headers` and the class overrides produced them."""
    config = _config("docker/compose")
    _mock_repository_resolution(requests_mock, "docker/compose")
    requests_mock.get(f"https://api.github.com/repos/docker/compose/{endpoint}", json=_body(stream_name, []))

    _, _, _, error = _read(config, stream_name)

    assert error is None
    (request,) = _listings(requests_mock, endpoint)
    assert request.path == f"/repos/docker/compose/{endpoint}"
    per_page = "10" if stream_name in LARGE_STREAMS else "100"
    assert request.qs == {"per_page": [per_page], **{key: [value] for key, value in params.items()}}
    # Without `User-Agent` GitHub answers 403; a stream that adds an `Accept` must restate it.
    assert request.headers["User-Agent"] == "PostmanRuntime/7.28.0"
    assert request.headers.get("Accept", "*/*") == EXTRA_ACCEPT_HEADERS.get(stream_name, "*/*")


@pytest.mark.parametrize(("stream_name", "endpoint", "cursor_field", "params"), STREAM_PARAMS)
def test_primary_key_and_cursor_match_legacy(stream_name, endpoint, cursor_field, params, rate_limit_mock_response, requests_mock):
    config = _config("docker/compose")
    _mock_repository_resolution(requests_mock, "docker/compose")
    source = SourceGithub(config=dict(config), catalog=None, state=None)

    (stream,) = [stream for stream in source.discover(logging.getLogger("airbyte"), dict(config)).streams if stream.name == stream_name]

    assert stream.source_defined_primary_key == [["user_id"] if stream_name == "stargazers" else ["id"]]
    assert stream.default_cursor_field == [cursor_field]
    assert stream.supported_sync_modes == [SyncMode.full_refresh, SyncMode.incremental]


def test_streams_are_served_by_the_manifest_only(rate_limit_mock_response, requests_mock):
    """`PullRequests`, `Projects` and `CommitComments` survive in streams.py as parents of the
    Step 7 group, so the Python list must not return them or the catalog would list them twice."""
    config = _config("docker/compose")
    _mock_repository_resolution(requests_mock, "docker/compose")
    source = SourceGithub(config=dict(config), catalog=None, state=None)

    python_names = {stream.name for stream in source.streams(dict(config))}
    discovered = [stream.name for stream in source.discover(logging.getLogger("airbyte"), dict(config)).streams]

    migrated = {stream[0] for stream in MIGRATED_STREAMS}
    assert not python_names & migrated
    assert migrated <= set(discovered)
    assert len(discovered) == len(set(discovered))


@pytest.mark.parametrize(("stream_name", "endpoint", "cursor_field", "params"), STREAM_PARAMS)
def test_start_date_filters_older_records_and_keeps_the_boundary(
    stream_name, endpoint, cursor_field, params, rate_limit_mock_response, requests_mock
):
    """The endpoints take no cursor parameter, so the filter has to happen locally. Legacy kept
    `cursor_value > start_point`; the CDK keeps `start <= cursor <= now`, so a record dated
    exactly `start_date` is now emitted where legacy dropped it. Pinned as the accepted
    divergence — the record is unchanged and destinations dedupe it on the primary key."""
    config = _config("docker/compose")
    _mock_repository_resolution(requests_mock, "docker/compose")
    # Newest-first, so the data-feed streams see the stale record last, as GitHub would send it.
    requests_mock.get(
        f"https://api.github.com/repos/docker/compose/{endpoint}",
        json=_body(
            stream_name,
            [
                _record(stream_name, 3, cursor_field, _AFTER_START),
                _record(stream_name, 2, cursor_field, _START_DATE),
                _record(stream_name, 1, cursor_field, _BEFORE_START),
            ],
        ),
    )

    records, statuses, states, error = _read(config, stream_name)

    assert error is None
    assert statuses[-1] == "COMPLETE"
    assert _ids(stream_name, records) == [3, 2]
    assert _partition_cursors(states[-1]) == {"docker/compose": _stored_cursor(stream_name, _AFTER_START)}


@pytest.mark.parametrize(("stream_name", "endpoint", "cursor_field", "params"), STREAM_PARAMS)
def test_legacy_state_is_migrated_and_filters_per_repository(
    stream_name, endpoint, cursor_field, params, rate_limit_mock_response, requests_mock
):
    """An upgraded connection arrives with `{repository: {cursor_field: value}}`. Without
    `LegacyToPerPartitionStateMigration` the CDK would not recognise it and silently re-read
    from `start_date`. The cursor must stay per repository: one shared value would skip records
    in every repository but the most recently updated one."""
    config = _config("airbytehq/airbyte", "docker/compose")
    _mock_repository_resolution(requests_mock, *config["repositories"])
    for repository in config["repositories"]:
        requests_mock.get(
            f"https://api.github.com/repos/{repository}/{endpoint}",
            json=_body(
                stream_name,
                [
                    _record(stream_name, 3, cursor_field, _LATEST),
                    _record(stream_name, 2, cursor_field, _LATER),
                    _record(stream_name, 1, cursor_field, _AFTER_START),
                ],
            ),
        )
    state = _legacy_state(stream_name, cursor_field, **{"airbytehq/airbyte": _LATER, "docker/compose": _AFTER_START})

    records, statuses, states, error = _read(config, stream_name, state=state)

    assert error is None
    assert statuses[-1] == "COMPLETE"
    by_repository = {}
    for record in records:
        by_repository.setdefault(record["repository"], []).append(record)
    assert _ids(stream_name, by_repository["airbytehq/airbyte"]) == [3, 2]
    assert _ids(stream_name, by_repository["docker/compose"]) == [3, 2, 1]
    assert _partition_cursors(states[-1]) == {repository: _stored_cursor(stream_name, _LATEST) for repository in config["repositories"]}


@pytest.mark.parametrize(("stream_name", "endpoint", "cursor_field", "params"), CLIENT_SIDE_PARAMS)
def test_unsorted_streams_read_every_page(stream_name, endpoint, cursor_field, params, rate_limit_mock_response, requests_mock):
    """GitHub gives no ordering guarantee for these listings (commit comments and stargazers are
    documented *ascending*), so a page full of stale records says nothing about the next one.
    Legacy never broke early here (`is_sorted = False`); a data-feed stop condition would end
    pagination after page one and lose the newer record on page two."""
    config = _config("docker/compose")
    _mock_repository_resolution(requests_mock, "docker/compose")
    url = f"https://api.github.com/repos/docker/compose/{endpoint}"
    requests_mock.get(
        url,
        [
            {
                "json": _body(
                    stream_name,
                    [_record(stream_name, 1, cursor_field, _BEFORE_START), _record(stream_name, 2, cursor_field, _BEFORE_START)],
                ),
                "headers": _next_link(f"{url}?page=2"),
            },
            {"json": _body(stream_name, [_record(stream_name, 3, cursor_field, _AFTER_START)])},
        ],
    )

    records, statuses, _, error = _read(config, stream_name)

    assert error is None
    assert statuses[-1] == "COMPLETE"
    assert _ids(stream_name, records) == [3]
    assert [request.qs.get("page") for request in _listings(requests_mock, endpoint)] == [None, ["2"]]


@pytest.mark.parametrize(("stream_name", "endpoint", "cursor_field", "params"), DATA_FEED_PARAMS)
def test_sorted_streams_stop_paginating_at_the_first_stale_record(
    stream_name, endpoint, cursor_field, params, rate_limit_mock_response, requests_mock
):
    """`sort=updated&direction=desc` puts the newest records first, so once a record older than
    the cursor shows up nothing further back can be newer. Legacy broke out of the page loop
    there (`SemiIncrementalMixin.read_records`, `is_sorted == "desc"`); the manifest's
    `is_data_feed` stop condition must end pagination the same way, or every incremental sync of
    a large repository walks its whole pull request history again."""
    config = _config("docker/compose")
    _mock_repository_resolution(requests_mock, "docker/compose")
    url = f"https://api.github.com/repos/docker/compose/{endpoint}"
    requests_mock.get(
        url,
        [
            {
                "json": _body(
                    stream_name,
                    [
                        _record(stream_name, 3, cursor_field, _LATER),
                        _record(stream_name, 2, cursor_field, _AFTER_START),
                        _record(stream_name, 1, cursor_field, _BEFORE_START),
                    ],
                ),
                "headers": _next_link(f"{url}?page=2"),
            },
            {"json": _body(stream_name, [_record(stream_name, 0, cursor_field, _BEFORE_START)])},
        ],
    )

    records, statuses, _, error = _read(config, stream_name)

    assert error is None
    assert statuses[-1] == "COMPLETE"
    assert _ids(stream_name, records) == [3, 2]
    assert len(_listings(requests_mock, endpoint)) == 1, "the cursor stop condition must end pagination on the first stale record"


@pytest.mark.parametrize(("stream_name", "endpoint", "cursor_field", "params"), DATA_FEED_PARAMS)
def test_sorted_streams_keep_paginating_past_a_boundary_record(
    stream_name, endpoint, cursor_field, params, rate_limit_mock_response, requests_mock
):
    """A record dated exactly the cursor is inside the window (see the boundary test above), so
    it neither stops pagination nor is dropped — legacy broke on `<`, not `<=`, too."""
    config = _config("docker/compose")
    _mock_repository_resolution(requests_mock, "docker/compose")
    url = f"https://api.github.com/repos/docker/compose/{endpoint}"
    requests_mock.get(
        url,
        [
            {
                "json": _body(
                    stream_name, [_record(stream_name, 2, cursor_field, _LATER), _record(stream_name, 1, cursor_field, _AFTER_START)]
                ),
                "headers": _next_link(f"{url}?page=2"),
            },
            {"json": _body(stream_name, [_record(stream_name, 0, cursor_field, _BEFORE_START)])},
        ],
    )

    records, _, _, error = _read(config, stream_name, state=_legacy_state(stream_name, cursor_field, **{"docker/compose": _AFTER_START}))

    assert error is None
    assert _ids(stream_name, records) == [2, 1]
    assert len(_listings(requests_mock, endpoint)) == 2


def test_emitted_state_resumes_the_next_sync(rate_limit_mock_response, requests_mock):
    """Round trip: the state the first sync emits, fed back unchanged, filters the second."""
    config = _config("docker/compose")
    _mock_repository_resolution(requests_mock, "docker/compose")
    url = "https://api.github.com/repos/docker/compose/deployments"
    requests_mock.get(url, json=[{"id": 1, "updated_at": _AFTER_START}])
    _, _, states, error = _read(config, "deployments")
    assert error is None

    requests_mock.get(
        url, json=[{"id": 2, "updated_at": _LATER}, {"id": 1, "updated_at": _AFTER_START}, {"id": 0, "updated_at": _START_DATE}]
    )
    records, statuses, states, error = _read(
        config, "deployments", state=_state_message("deployments", states[-1].stream.stream_state.__dict__)
    )

    assert error is None
    assert statuses[-1] == "COMPLETE"
    assert [record["id"] for record in records] == [2, 1]
    assert _partition_cursors(states[-1]) == {"docker/compose": _LATER}


def test_pull_requests_flatten_head_and_base_repositories(rate_limit_mock_response, requests_mock):
    """`PullRequests.transform` replaced `head.repo` with `head.repo_id`. It also meant to do the
    same for `base`, but read the id off the already-popped `head.repo`, so legacy always shipped
    `base.repo_id: null` next to an intact `base.repo`. The schema declares `base.repo_id` an
    integer, so the manifest fills it from `base.repo` — the one deliberate data change in this
    group. `base.repo` stays, as before."""
    config = _config("docker/compose")
    _mock_repository_resolution(requests_mock, "docker/compose")
    requests_mock.get(
        "https://api.github.com/repos/docker/compose/pulls",
        json=[
            {
                "id": 2,
                "number": 2,
                "updated_at": _LATER,
                "head": {"ref": "fix", "repo": {"id": 11}},
                "base": {"ref": "main", "repo": {"id": 22}},
            },
            # A fork that was deleted: GitHub sends `head.repo: null`.
            {
                "id": 1,
                "number": 1,
                "updated_at": _AFTER_START,
                "head": {"ref": "old", "repo": None},
                "base": {"ref": "main", "repo": {"id": 22}},
            },
        ],
    )

    records, _, _, error = _read(config, "pull_requests")

    assert error is None
    assert [record["head"] for record in records] == [{"ref": "fix", "repo_id": 11}, {"ref": "old", "repo_id": None}]
    assert [record["base"] for record in records] == [{"ref": "main", "repo": {"id": 22}, "repo_id": 22}] * 2


@pytest.mark.parametrize(
    ("page_size_config", "expected_per_page"),
    [
        pytest.param({}, "10", id="default_is_the_large_stream_page_size"),
        pytest.param({"page_size_for_large_streams": 3}, "3", id="configured"),
        pytest.param({"page_size_for_large_streams": None}, "10", id="present_but_null_falls_back"),
    ],
)
def test_pull_requests_page_size_comes_from_the_large_stream_setting(
    page_size_config, expected_per_page, rate_limit_mock_response, requests_mock
):
    """`PullRequests.large_stream = True`: `GithubStream.__init__` took `per_page` from the
    deprecated `page_size_for_large_streams` (default `constants.DEFAULT_PAGE_SIZE_FOR_LARGE_STREAM`,
    10) rather than the 100 the other repo-scoped streams send."""
    config = _config("docker/compose", **page_size_config)
    _mock_repository_resolution(requests_mock, "docker/compose")
    requests_mock.get("https://api.github.com/repos/docker/compose/pulls", json=[])

    _, _, _, error = _read(config, "pull_requests")

    assert error is None
    assert [request.qs["per_page"] for request in _listings(requests_mock, "pulls")] == [[expected_per_page]]


def test_commit_comments_rename_reactions(rate_limit_mock_response, requests_mock):
    """`GithubStream.transform` renamed `+1`/`-1` to `plus_one`/`minus_one` (the 2.0.0 breaking
    change); `reactions.json` declares only the renamed keys. A count of 0 is a value and must
    survive; a record without `reactions` must not gain an empty one."""
    config = _config("docker/compose")
    _mock_repository_resolution(requests_mock, "docker/compose")
    requests_mock.get(
        "https://api.github.com/repos/docker/compose/comments",
        json=[
            {"id": 1, "updated_at": _AFTER_START, "reactions": {"url": "u", "total_count": 3, "+1": 2, "-1": 0, "laugh": 1}},
            {"id": 2, "updated_at": _AFTER_START, "reactions": {"url": "u", "total_count": 0}},
            {"id": 3, "updated_at": _AFTER_START},
        ],
    )

    records, _, _, error = _read(config, "commit_comments")

    assert error is None
    assert records[0]["reactions"] == {"url": "u", "total_count": 3, "laugh": 1, "plus_one": 2, "minus_one": 0}
    assert records[1]["reactions"] == {"url": "u", "total_count": 0}
    assert "reactions" not in records[2]


def test_stargazers_promote_the_user_id(rate_limit_mock_response, requests_mock):
    """The star payload has no id of its own, so `Stargazers.transform` copied `user.id` to a
    top-level `user_id` — the primary key — and kept the `user` object. Legacy raised on a null
    `user`; a null `user_id` is the more useful outcome."""
    config = _config("docker/compose")
    _mock_repository_resolution(requests_mock, "docker/compose")
    requests_mock.get(
        "https://api.github.com/repos/docker/compose/stargazers",
        json=[{"starred_at": _AFTER_START, "user": {"id": 7, "login": "octocat"}}, {"starred_at": _LATER, "user": None}],
    )

    records, _, _, error = _read(config, "stargazers")

    assert error is None
    assert records == [
        {"starred_at": _AFTER_START, "user": {"id": 7, "login": "octocat"}, "repository": "docker/compose", "user_id": 7},
        {"starred_at": _LATER, "user": None, "repository": "docker/compose", "user_id": None},
    ]


def test_projects_disabled_repository_is_skipped(rate_limit_mock_response, requests_mock):
    """Classic Projects can be turned off per repository, and GitHub answers 410 "Projects are
    disabled for this repository". Legacy skipped the repository with a warning
    (`is_gone_with_feature_disabled`); `disabled_feature_skip_filter` does the same, and the
    other repositories still sync."""
    config = _config("airbytehq/airbyte", "docker/compose")
    _mock_repository_resolution(requests_mock, *config["repositories"])
    requests_mock.get(
        "https://api.github.com/repos/airbytehq/airbyte/projects",
        status_code=410,
        json={"message": "Projects are disabled for this repository", "documentation_url": "https://docs.github.com/v3/projects"},
    )
    requests_mock.get("https://api.github.com/repos/docker/compose/projects", json=[{"id": 1, "updated_at": _AFTER_START}])

    records, statuses, _, error = _read(config, "projects")

    assert error is None
    assert statuses[-1] == "COMPLETE"
    assert [(record["repository"], record["id"]) for record in records] == [("docker/compose", 1)]


@pytest.mark.parametrize(
    ("response", "expected_ids"),
    [
        pytest.param(
            {"json": {"total_count": 2, "workflows": [{"id": 1, "updated_at": _AFTER_START}, {"id": 2, "updated_at": _LATER}]}},
            [1, 2],
            id="envelope",
        ),
        pytest.param({"json": {"total_count": 0, "workflows": []}}, [], id="empty"),
        pytest.param({"json": {"message": "Server Error"}}, [], id="error_envelope_without_key"),
        pytest.param({"text": "<html>Bad Gateway</html>"}, [], id="html_body"),
        pytest.param({"text": ""}, [], id="empty_body"),
    ],
)
def test_workflows_read_the_envelope_and_tolerate_odd_bodies(response, expected_ids, rate_limit_mock_response, requests_mock):
    """`GET /actions/workflows` wraps the listing in `{"total_count", "workflows"}`
    (`Workflows.parse_response`). Legacy's `_safe_json_list` turned a body without the key, or
    one that is not JSON at all, into zero records rather than a failure; the extractor must too."""
    config = _config("docker/compose")
    _mock_repository_resolution(requests_mock, "docker/compose")
    requests_mock.get("https://api.github.com/repos/docker/compose/actions/workflows", **response)

    records, statuses, _, error = _read(config, "workflows")

    assert error is None
    assert statuses[-1] == "COMPLETE"
    assert [record["id"] for record in records] == expected_ids


def test_workflows_offset_timestamps_keep_their_instant_across_syncs(rate_limit_mock_response, requests_mock):
    """The Actions API stamps records with a UTC offset (`2024-01-01T10:00:00.000+05:00`) where
    every other GitHub listing uses `Z`. Legacy normalised the cursor to UTC before comparing or
    storing it (`Workflows.convert_cursor_value`). The CDK compares aware datetimes, so filtering
    is right as long as the formats parse — but it writes state with `strftime`, which keeps the
    record's own offset. A `...%SZ` output format would therefore store `10:00:00Z` for an instant
    that is `05:00:00Z` and, on the next sync, drop a record updated at `07:00:00Z`. The `%z`
    output format keeps the offset in the stored value, and this test would fail without it."""
    config = _config("docker/compose")
    _mock_repository_resolution(requests_mock, "docker/compose")
    url = "https://api.github.com/repos/docker/compose/actions/workflows"
    requests_mock.get(url, json={"total_count": 1, "workflows": [{"id": 1, "updated_at": "2024-01-01T10:00:00.000+05:00"}]})
    records, _, states, error = _read(config, "workflows")
    assert error is None
    assert [record["updated_at"] for record in records] == ["2024-01-01T10:00:00.000+05:00"], "the record itself is not rewritten"
    assert _partition_cursors(states[-1]) == {"docker/compose": "2024-01-01T10:00:00+0500"}

    requests_mock.get(
        url,
        json={
            "total_count": 3,
            "workflows": [
                {"id": 1, "updated_at": "2024-01-01T10:00:00.000+05:00"},  # == 05:00Z, the boundary
                {"id": 2, "updated_at": "2024-01-01T07:00:00.000Z"},  # newer than the boundary
                {"id": 3, "updated_at": "2024-01-01T04:00:00.000Z"},  # older than the boundary
            ],
        },
    )
    records, _, states, error = _read(config, "workflows", state=_state_message("workflows", states[-1].stream.stream_state.__dict__))

    assert error is None
    assert [record["id"] for record in records] == [1, 2]
    assert _partition_cursors(states[-1]) == {"docker/compose": "2024-01-01T07:00:00+0000"}


def test_workflows_legacy_utc_state_is_understood(rate_limit_mock_response, requests_mock):
    """Legacy stored the normalised `...Z` value; `%z` parses a bare `Z`, so a migrated state
    filters correctly against offset-stamped records."""
    config = _config("docker/compose")
    _mock_repository_resolution(requests_mock, "docker/compose")
    requests_mock.get(
        "https://api.github.com/repos/docker/compose/actions/workflows",
        json={
            "total_count": 2,
            "workflows": [
                {"id": 1, "updated_at": "2024-01-01T10:00:00.000+05:00"},
                {"id": 2, "updated_at": "2024-01-01T10:00:00.000-05:00"},
            ],
        },
    )

    records, _, _, error = _read(
        config, "workflows", state=_legacy_state("workflows", "updated_at", **{"docker/compose": "2024-01-01T08:00:00Z"})
    )

    assert error is None
    # 10:00+05:00 is 05:00Z (older than the 08:00Z cursor); 10:00-05:00 is 15:00Z (newer).
    assert [record["id"] for record in records] == [2]
