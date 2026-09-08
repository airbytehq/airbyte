#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Behavior of the parent-child REST streams migrated to the manifest (Step 7).

Each of these streams slices on the records of another stream: `PullRequestCommits` read
`PullRequests`, `ProjectColumns` read `Projects` and `ProjectCards` read `ProjectColumns`,
`TeamMembers` read `Teams` and `TeamMemberships` read `TeamMembers`, `IssueTimelineEvents` read
`Issues`, and the two reaction streams read `CommitComments` and `Comments`. The Python classes
read their parent in full refresh from `start_date`, stamped the parent's identifiers onto every
child record, and — for the four incremental ones — filtered client-side on a cursor kept per
parent record. The tests below assert parity with that, or pin the deliberate divergences.
"""

import json
import logging
import os
import shutil
from pathlib import Path

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

from .utils import ProjectsResponsesAPI


MIGRATED_STREAMS = [
    "pull_request_commits",
    "project_columns",
    "project_cards",
    "team_members",
    "team_memberships",
    "issue_timeline_events",
    "commit_comment_reactions",
    "issue_comment_reactions",
]
INCREMENTAL_STREAMS = {"project_columns", "project_cards", "commit_comment_reactions", "issue_comment_reactions"}

_TOKEN_CONFIG = {"credentials": {"personal_access_token": "token"}}
_START_DATE = "2022-01-01T00:00:00Z"
_BEFORE_START = "2021-06-01T00:00:00Z"
_AFTER_START = "2022-06-01T00:00:00Z"
_LATER = "2022-07-01T00:00:00Z"
_REPO = "docker/compose"
_ORG = "docker"
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
    # Parents cache their listings (`use_cache: true`); a second sync in the same test must hit the mocks again.
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


def _mock_repository_resolution(requests_mock, *repositories):
    for index, repository in enumerate(repositories, start=1):
        requests_mock.get(
            f"{_API}/repos/{repository}",
            json={"id": index, "full_name": repository, "organization": {"login": repository.split("/")[0]}},
        )


def _state_message(stream_name, state):
    return [
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(stream_descriptor=StreamDescriptor(name=stream_name), stream_state=AirbyteStateBlob(state)),
        )
    ]


def _partition_cursors(state_message):
    state = state_message.stream.stream_state.__dict__
    return {json.dumps(entry["partition"], sort_keys=True): next(iter(entry["cursor"].values())) for entry in state["states"]}


def _requested(requests_mock, fragment):
    return [request for request in requests_mock.request_history if fragment in request.path]


def _record(**fields):
    return fields


# (stream, [(url, body)], child listing path fragment, expected query params, expected records)
SINGLE_PARENT_CASES = [
    pytest.param(
        "pull_request_commits",
        [
            (f"{_API}/repos/{_REPO}/pulls", [_record(id=1, number=7, updated_at=_AFTER_START, head={}, base={})]),
            (f"{_API}/repos/{_REPO}/pulls/7/commits", [{"sha": "a"}]),
        ],
        "/pulls/7/commits",
        {"per_page": ["100"]},
        [{"sha": "a", "repository": _REPO, "pull_number": 7}],
        id="pull_request_commits",
    ),
    pytest.param(
        "project_columns",
        [
            (f"{_API}/repos/{_REPO}/projects", [_record(id=5, updated_at=_AFTER_START)]),
            (f"{_API}/projects/5/columns", [_record(id=50, updated_at=_AFTER_START)]),
        ],
        "/projects/5/columns",
        {"per_page": ["100"]},
        [{"id": 50, "updated_at": _AFTER_START, "repository": _REPO, "project_id": 5}],
        id="project_columns",
    ),
    pytest.param(
        "project_cards",
        [
            (f"{_API}/repos/{_REPO}/projects", [_record(id=5, updated_at=_AFTER_START)]),
            (f"{_API}/projects/5/columns", [_record(id=50, updated_at=_AFTER_START)]),
            (f"{_API}/projects/columns/50/cards", [_record(id=500, updated_at=_AFTER_START)]),
        ],
        "/projects/columns/50/cards",
        {"per_page": ["100"], "archived_state": ["all"]},
        [{"id": 500, "updated_at": _AFTER_START, "repository": _REPO, "project_id": 5, "column_id": 50}],
        id="project_cards",
    ),
    pytest.param(
        "team_members",
        [
            (f"{_API}/orgs/{_ORG}/teams", [_record(id=1, slug="core")]),
            (f"{_API}/orgs/{_ORG}/teams/core/members", [_record(id=9, login="octo")]),
        ],
        "/teams/core/members",
        {"per_page": ["100"]},
        [{"id": 9, "login": "octo", "organization": _ORG, "team_slug": "core"}],
        id="team_members",
    ),
    pytest.param(
        "team_memberships",
        [
            (f"{_API}/orgs/{_ORG}/teams", [_record(id=1, slug="core")]),
            (f"{_API}/orgs/{_ORG}/teams/core/members", [_record(id=9, login="octo")]),
            (f"{_API}/orgs/{_ORG}/teams/core/memberships/octo", {"url": "u", "role": "member"}),
        ],
        "/teams/core/memberships/octo",
        {"per_page": ["100"]},
        [{"url": "u", "role": "member", "organization": _ORG, "team_slug": "core", "username": "octo"}],
        id="team_memberships",
    ),
    pytest.param(
        "issue_timeline_events",
        [
            (f"{_API}/repos/{_REPO}/issues", [_record(id=30, number=3, updated_at=_AFTER_START)]),
            (f"{_API}/repos/{_REPO}/issues/3/timeline", [{"event": "closed", "actor": {"login": "octo"}}]),
        ],
        "/issues/3/timeline",
        {"per_page": ["100"]},
        [{"closed": {"event": "closed", "actor": {"login": "octo"}}, "repository": _REPO, "issue_number": 3}],
        id="issue_timeline_events",
    ),
    pytest.param(
        "commit_comment_reactions",
        [
            (f"{_API}/repos/{_REPO}/comments", [_record(id=9, updated_at=_AFTER_START)]),
            (f"{_API}/repos/{_REPO}/comments/9/reactions", [_record(id=90, created_at=_AFTER_START)]),
        ],
        "/comments/9/reactions",
        {"per_page": ["100"]},
        [{"id": 90, "created_at": _AFTER_START, "repository": _REPO, "comment_id": 9}],
        id="commit_comment_reactions",
    ),
    pytest.param(
        "issue_comment_reactions",
        [
            (f"{_API}/repos/{_REPO}/issues/comments", [_record(id=8, updated_at=_AFTER_START)]),
            (f"{_API}/repos/{_REPO}/issues/comments/8/reactions", [_record(id=80, created_at=_AFTER_START)]),
        ],
        "/issues/comments/8/reactions",
        {"per_page": ["100"]},
        [{"id": 80, "created_at": _AFTER_START, "repository": _REPO, "comment_id": 8}],
        id="issue_comment_reactions",
    ),
]


@pytest.mark.parametrize(("stream_name", "mocks", "child_path", "expected_params", "expected_records"), SINGLE_PARENT_CASES)
def test_child_requests_follow_the_parent_records(
    stream_name, mocks, child_path, expected_params, expected_records, rate_limit_mock_response, requests_mock
):
    """One child request per parent record, on the legacy path, with the parent's identifiers
    stamped onto every record the way the Python `transform` did."""
    config = _config(_REPO)
    _mock_repository_resolution(requests_mock, _REPO)
    for url, body in mocks:
        requests_mock.get(url, json=body)

    records, statuses, _, error = _read(config, stream_name)

    assert error is None
    assert statuses[-1] == "COMPLETE"
    assert records == expected_records
    (request,) = _requested(requests_mock, child_path)
    assert request.qs == expected_params
    assert request.headers["User-Agent"] == "PostmanRuntime/7.28.0"


def test_streams_are_served_by_the_manifest_only(rate_limit_mock_response, requests_mock):
    config = _config(_REPO)
    _mock_repository_resolution(requests_mock, _REPO)
    requests_mock.get(f"{_API}/repos/{_REPO}/branches", json=[{"name": "master"}])
    source = SourceGithub(config=dict(config), catalog=None, state=None)

    python_names = {stream.name for stream in source.streams(dict(config))}
    discovered = source.discover(logging.getLogger("airbyte"), dict(config)).streams

    assert not python_names & set(MIGRATED_STREAMS)
    assert set(MIGRATED_STREAMS) <= {stream.name for stream in discovered}
    assert len(discovered) == len({stream.name for stream in discovered})
    by_name = {stream.name: stream for stream in discovered}
    assert by_name["pull_request_commits"].source_defined_primary_key == [["sha"]]
    assert by_name["team_members"].source_defined_primary_key == [["id"], ["team_slug"]]
    assert by_name["team_memberships"].source_defined_primary_key == [["url"]]
    assert by_name["issue_timeline_events"].source_defined_primary_key == [["repository"], ["issue_number"]]
    for name in INCREMENTAL_STREAMS:
        assert by_name[name].default_cursor_field == (["created_at"] if name.endswith("reactions") else ["updated_at"])
        assert by_name[name].supported_sync_modes == [SyncMode.full_refresh, SyncMode.incremental]
    for name in set(MIGRATED_STREAMS) - INCREMENTAL_STREAMS:
        assert by_name[name].supported_sync_modes == [SyncMode.full_refresh]


@pytest.mark.parametrize(
    ("stream_name", "parent_url", "parent_records", "expanded_path", "skipped_path"),
    [
        pytest.param(
            "pull_request_commits",
            f"{_API}/repos/{_REPO}/pulls",
            [
                _record(id=2, number=2, updated_at=_AFTER_START, head={}, base={}),
                _record(id=1, number=1, updated_at=_BEFORE_START, head={}, base={}),
            ],
            "/pulls/2/commits",
            "/pulls/1/commits",
            id="pull_request_commits",
        ),
        pytest.param(
            "commit_comment_reactions",
            f"{_API}/repos/{_REPO}/comments",
            [_record(id=9, updated_at=_AFTER_START), _record(id=8, updated_at=_BEFORE_START)],
            "/comments/9/reactions",
            "/comments/8/reactions",
            id="commit_comment_reactions",
        ),
        pytest.param(
            "project_columns",
            f"{_API}/repos/{_REPO}/projects",
            [_record(id=5, updated_at=_AFTER_START), _record(id=4, updated_at=_BEFORE_START)],
            "/projects/5/columns",
            "/projects/4/columns",
            id="project_columns",
        ),
    ],
)
def test_parents_older_than_start_date_are_not_expanded(
    stream_name, parent_url, parent_records, expanded_path, skipped_path, rate_limit_mock_response, requests_mock
):
    """The Python classes read their parent in full refresh, which for the semi-incremental parents
    meant "filtered by `start_date`". The declarative parent read does the same."""
    config = _config(_REPO)
    _mock_repository_resolution(requests_mock, _REPO)
    requests_mock.get(parent_url, json=parent_records)
    requests_mock.get(
        f"{_API}{expanded_path}" if expanded_path.startswith("/projects") else f"{_API}/repos/{_REPO}{expanded_path}", json=[]
    )

    _, statuses, _, error = _read(config, stream_name)

    assert error is None
    assert statuses[-1] == "COMPLETE"
    assert len(_requested(requests_mock, expanded_path)) == 1
    assert _requested(requests_mock, skipped_path) == []


def test_parent_read_ignores_the_parent_streams_own_saved_state(rate_limit_mock_response, requests_mock):
    """Legacy `PullRequestCommits` read `PullRequests` from `start_date` no matter what state the
    `pull_requests` stream itself had saved. A saved `pull_requests` cursor newer than a pull
    request must not stop that pull request's commits from being read."""
    config = _config(_REPO)
    _mock_repository_resolution(requests_mock, _REPO)
    requests_mock.get(f"{_API}/repos/{_REPO}/pulls", json=[_record(id=7, number=7, updated_at=_AFTER_START, head={}, base={})])
    requests_mock.get(f"{_API}/repos/{_REPO}/pulls/7/commits", json=[{"sha": "a"}])
    pull_requests_state = _state_message("pull_requests", {_REPO: {"updated_at": _LATER}})

    records, _, _, error = _read(config, "pull_request_commits", state=pull_requests_state)

    assert error is None
    assert [record["sha"] for record in records] == ["a"]


def test_pull_request_commits_legacy_scenario(rate_limit_mock_response, requests_mock):
    """The scenario `test_stream_pull_request_commits` drove through the Python classes: three pull
    requests, one older than `start_date`, commits fetched for the other two."""
    config = _config("organization/repository", start_date="2022-02-02T10:10:03Z")
    _mock_repository_resolution(requests_mock, "organization/repository")
    requests_mock.get(
        f"{_API}/repos/organization/repository/pulls",
        json=[
            _record(id=1, updated_at="2022-02-02T10:10:02Z", number=1, head={}, base={}),
            _record(id=2, updated_at="2022-02-02T10:10:04Z", number=2, head={}, base={}),
            _record(id=3, updated_at="2022-02-02T10:10:06Z", number=3, head={}, base={}),
        ],
    )
    requests_mock.get(f"{_API}/repos/organization/repository/pulls/2/commits", json=[{"sha": 1}, {"sha": 2}])
    requests_mock.get(f"{_API}/repos/organization/repository/pulls/3/commits", json=[{"sha": 3}, {"sha": 4}])

    records, _, _, error = _read(config, "pull_request_commits")

    assert error is None
    assert sorted(records, key=lambda record: record["sha"]) == [
        {"sha": 1, "repository": "organization/repository", "pull_number": 2},
        {"sha": 2, "repository": "organization/repository", "pull_number": 2},
        {"sha": 3, "repository": "organization/repository", "pull_number": 3},
        {"sha": 4, "repository": "organization/repository", "pull_number": 3},
    ]
    assert _requested(requests_mock, "/pulls/1/commits") == []


def test_project_columns_two_syncs_legacy_scenario(rate_limit_mock_response, requests_mock):
    """`test_stream_project_columns`, ported. The Python filter kept columns strictly newer than
    the per-project cursor; the CDK's is inclusive, so the second sync re-emits the boundary
    column of every project (23 and 32 here) next to the genuinely new ones (24 and 41)."""
    config = _config("organization/repository", start_date="2022-02-01T00:00:00Z")
    _mock_repository_resolution(requests_mock, "organization/repository")
    data = [
        {"updated_at": "2022-01-01T10:00:00Z"},
        {
            "updated_at": "2022-03-01T10:00:00Z",
            "columns": [
                {"updated_at": "2022-01-01T10:00:00Z"},
                {"updated_at": "2022-03-01T09:00:00Z"},
                {"updated_at": "2022-03-01T10:00:00Z"},
            ],
        },
        {"updated_at": "2022-05-01T10:00:00Z", "columns": [{"updated_at": "2022-01-01T10:00:00Z"}, {"updated_at": "2022-05-01T10:00:00Z"}]},
    ]
    ProjectsResponsesAPI.register(data, requests_mock)

    records, _, states, error = _read(config, "project_columns")

    assert error is None
    assert sorted(records, key=lambda record: record["id"]) == [
        {"id": 22, "name": "column_22", "project_id": 2, "repository": "organization/repository", "updated_at": "2022-03-01T09:00:00Z"},
        {"id": 23, "name": "column_23", "project_id": 2, "repository": "organization/repository", "updated_at": "2022-03-01T10:00:00Z"},
        {"id": 32, "name": "column_32", "project_id": 3, "repository": "organization/repository", "updated_at": "2022-05-01T10:00:00Z"},
    ]
    assert _partition_cursors(states[-1]) == {
        '{"parent_slice": {"repository": "organization/repository"}, "project_id": 2}': "2022-03-01T10:00:00Z",
        '{"parent_slice": {"repository": "organization/repository"}, "project_id": 3}': "2022-05-01T10:00:00Z",
    }

    data = [
        {"updated_at": "2022-01-01T10:00:00Z"},
        {
            "updated_at": "2022-04-01T10:00:00Z",
            "columns": [
                {"updated_at": "2022-01-01T10:00:00Z"},
                {"updated_at": "2022-03-01T09:00:00Z"},
                {"updated_at": "2022-03-01T10:00:00Z"},
                {"updated_at": "2022-04-01T10:00:00Z"},
            ],
        },
        {"updated_at": "2022-05-01T10:00:00Z", "columns": [{"updated_at": "2022-01-01T10:00:00Z"}, {"updated_at": "2022-05-01T10:00:00Z"}]},
        {"updated_at": "2022-06-01T10:00:00Z", "columns": [{"updated_at": "2022-06-01T10:00:00Z"}]},
    ]
    ProjectsResponsesAPI.register(data, requests_mock)

    records, _, states, error = _read(
        config, "project_columns", state=_state_message("project_columns", states[-1].stream.stream_state.__dict__)
    )

    assert error is None
    assert sorted(record["id"] for record in records) == [23, 24, 32, 41]
    assert _partition_cursors(states[-1]) == {
        '{"parent_slice": {"repository": "organization/repository"}, "project_id": 2}': "2022-04-01T10:00:00Z",
        '{"parent_slice": {"repository": "organization/repository"}, "project_id": 3}': "2022-05-01T10:00:00Z",
        '{"parent_slice": {"repository": "organization/repository"}, "project_id": 4}': "2022-06-01T10:00:00Z",
    }


def test_project_cards_three_level_chain_legacy_scenario(rate_limit_mock_response, requests_mock):
    """`test_stream_project_cards`, ported: cards are reached through projects then columns, and
    both parent levels are filtered by `start_date` before being expanded. Card 211 sits exactly
    on `start_date`; the Python filter dropped it, the inclusive CDK filter keeps it."""
    config = _config("organization/repository", start_date="2022-03-01T00:00:00Z")
    _mock_repository_resolution(requests_mock, "organization/repository")
    data = [
        {"updated_at": "2022-01-01T00:00:00Z"},
        {
            "updated_at": "2022-06-01T00:00:00Z",
            "columns": [
                {
                    "updated_at": "2022-04-01T00:00:00Z",
                    "cards": [{"updated_at": "2022-03-01T00:00:00Z"}, {"updated_at": "2022-04-01T00:00:00Z"}],
                },
                {"updated_at": "2022-05-01T09:00:00Z"},
                {
                    "updated_at": "2022-06-01T00:00:00Z",
                    "cards": [{"updated_at": "2022-05-01T00:00:00Z"}, {"updated_at": "2022-06-01T00:00:00Z"}],
                },
            ],
        },
        {
            "updated_at": "2022-05-01T00:00:00Z",
            "columns": [
                {"updated_at": "2022-01-01T00:00:00Z"},
                {
                    "updated_at": "2022-05-01T00:00:00Z",
                    "cards": [{"updated_at": "2022-02-01T00:00:00Z"}, {"updated_at": "2022-05-01T00:00:00Z"}],
                },
            ],
        },
    ]
    ProjectsResponsesAPI.register(data, requests_mock)

    records, statuses, states, error = _read(config, "project_cards")

    assert error is None
    assert statuses[-1] == "COMPLETE"
    assert sorted(record["id"] for record in records) == [211, 212, 231, 232, 322]
    assert {(record["project_id"], record["column_id"]) for record in records} == {(2, 21), (2, 23), (3, 32)}
    assert _requested(requests_mock, "/projects/1/columns") == [], "project 1 predates start_date"
    assert _requested(requests_mock, "/projects/columns/31/cards") == [], "column 31 predates start_date"
    # Column 22 has no cards; its partition still closes with the start date as its cursor.
    assert _partition_cursors(states[-1]) == {
        '{"column_id": 21, "parent_slice": {"parent_slice": {"repository": "organization/repository"}, "project_id": 2}}': "2022-04-01T00:00:00Z",
        '{"column_id": 22, "parent_slice": {"parent_slice": {"repository": "organization/repository"}, "project_id": 2}}': "2022-03-01T00:00:00Z",
        '{"column_id": 23, "parent_slice": {"parent_slice": {"repository": "organization/repository"}, "project_id": 2}}': "2022-06-01T00:00:00Z",
        '{"column_id": 32, "parent_slice": {"parent_slice": {"repository": "organization/repository"}, "project_id": 3}}': "2022-05-01T00:00:00Z",
    }


def test_commit_comment_reactions_two_syncs_legacy_scenario(rate_limit_mock_response, requests_mock):
    """`test_stream_commit_comment_reactions_incremental_read`, ported. No `start_date`, so every
    comment is expanded. The second sync re-emits the boundary reaction of each comment (430 and
    431) next to the new ones (432 and 433) — the inclusive CDK filter again."""
    config = _config("airbytehq/integration-test", start_date=None)
    _mock_repository_resolution(requests_mock, "airbytehq/integration-test")
    comments = f"{_API}/repos/airbytehq/integration-test/comments"
    requests_mock.get(
        comments, json=[_record(id=55538825, updated_at="2021-01-01T15:00:00Z"), _record(id=55538826, updated_at="2021-01-01T16:00:00Z")]
    )
    requests_mock.get(
        f"{comments}/55538825/reactions",
        json=[_record(id=154935429, created_at="2022-01-01T15:00:00Z"), _record(id=154935430, created_at="2022-01-01T16:00:00Z")],
    )
    requests_mock.get(f"{comments}/55538826/reactions", json=[_record(id=154935431, created_at="2022-01-01T17:00:00Z")])

    records, _, states, error = _read(config, "commit_comment_reactions")

    assert error is None
    assert sorted(records, key=lambda record: record["id"]) == [
        {"id": 154935429, "created_at": "2022-01-01T15:00:00Z", "repository": "airbytehq/integration-test", "comment_id": 55538825},
        {"id": 154935430, "created_at": "2022-01-01T16:00:00Z", "repository": "airbytehq/integration-test", "comment_id": 55538825},
        {"id": 154935431, "created_at": "2022-01-01T17:00:00Z", "repository": "airbytehq/integration-test", "comment_id": 55538826},
    ]
    assert _partition_cursors(states[-1]) == {
        '{"comment_id": 55538825, "parent_slice": {"repository": "airbytehq/integration-test"}}': "2022-01-01T16:00:00Z",
        '{"comment_id": 55538826, "parent_slice": {"repository": "airbytehq/integration-test"}}': "2022-01-01T17:00:00Z",
    }

    requests_mock.get(
        comments,
        json=[
            _record(id=55538825, updated_at="2021-01-01T15:00:00Z"),
            _record(id=55538826, updated_at="2021-01-01T16:00:00Z"),
            _record(id=55538827, updated_at="2022-02-01T15:00:00Z"),
        ],
    )
    requests_mock.get(
        f"{comments}/55538826/reactions",
        json=[_record(id=154935431, created_at="2022-01-01T17:00:00Z"), _record(id=154935432, created_at="2022-02-01T16:00:00Z")],
    )
    requests_mock.get(f"{comments}/55538827/reactions", json=[_record(id=154935433, created_at="2022-02-01T17:00:00Z")])

    records, _, states, error = _read(
        config, "commit_comment_reactions", state=_state_message("commit_comment_reactions", states[-1].stream.stream_state.__dict__)
    )

    assert error is None
    assert sorted(record["id"] for record in records) == [154935430, 154935431, 154935432, 154935433]
    assert _partition_cursors(states[-1]) == {
        '{"comment_id": 55538825, "parent_slice": {"repository": "airbytehq/integration-test"}}': "2022-01-01T16:00:00Z",
        '{"comment_id": 55538826, "parent_slice": {"repository": "airbytehq/integration-test"}}': "2022-02-01T16:00:00Z",
        '{"comment_id": 55538827, "parent_slice": {"repository": "airbytehq/integration-test"}}': "2022-02-01T17:00:00Z",
    }


@pytest.mark.parametrize(
    ("stream_name", "legacy_state", "mocks", "expected_ids"),
    [
        pytest.param(
            "project_columns",
            {_REPO: {"5": {"updated_at": _AFTER_START}}},
            [
                (f"{_API}/repos/{_REPO}/projects", [_record(id=5, updated_at=_LATER)]),
                (
                    f"{_API}/projects/5/columns",
                    [_record(id=50, updated_at=_LATER), _record(id=51, updated_at=_AFTER_START), _record(id=52, updated_at=_BEFORE_START)],
                ),
            ],
            [50, 51],
            id="project_columns",
        ),
        pytest.param(
            "project_cards",
            {_REPO: {"5": {"50": {"updated_at": _AFTER_START}}}},
            [
                (f"{_API}/repos/{_REPO}/projects", [_record(id=5, updated_at=_LATER)]),
                (f"{_API}/projects/5/columns", [_record(id=50, updated_at=_LATER)]),
                (
                    f"{_API}/projects/columns/50/cards",
                    [
                        _record(id=500, updated_at=_LATER),
                        _record(id=501, updated_at=_AFTER_START),
                        _record(id=502, updated_at=_BEFORE_START),
                    ],
                ),
            ],
            [500, 501],
            id="project_cards",
        ),
        pytest.param(
            "commit_comment_reactions",
            {_REPO: {"9": {"created_at": _AFTER_START}}},
            [
                (f"{_API}/repos/{_REPO}/comments", [_record(id=9, updated_at=_LATER)]),
                (
                    f"{_API}/repos/{_REPO}/comments/9/reactions",
                    [_record(id=90, created_at=_LATER), _record(id=91, created_at=_AFTER_START), _record(id=92, created_at=_BEFORE_START)],
                ),
            ],
            [90, 91],
            id="commit_comment_reactions",
        ),
        pytest.param(
            "issue_comment_reactions",
            {_REPO: {"8": {"created_at": _AFTER_START}}},
            [
                (f"{_API}/repos/{_REPO}/issues/comments", [_record(id=8, updated_at=_LATER)]),
                (
                    f"{_API}/repos/{_REPO}/issues/comments/8/reactions",
                    [_record(id=80, created_at=_LATER), _record(id=81, created_at=_AFTER_START), _record(id=82, created_at=_BEFORE_START)],
                ),
            ],
            [80, 81],
            id="issue_comment_reactions",
        ),
    ],
)
def test_legacy_nested_state_is_migrated_per_partition(
    stream_name, legacy_state, mocks, expected_ids, rate_limit_mock_response, requests_mock
):
    """The Python classes nested their cursor under the repository and each parent id
    (`{repo: {project_id: {column_id: {updated_at}}}}` for cards), which the CDK's
    `LegacyToPerPartitionStateMigration` does not understand. The custom migration in
    `components.py` has to land on exactly the partition the substream router builds, ids as
    integers; if it did not, the record older than the cursor (…2) would be re-emitted."""
    config = _config(_REPO)
    _mock_repository_resolution(requests_mock, _REPO)
    for url, body in mocks:
        requests_mock.get(url, json=body)

    records, _, states, error = _read(config, stream_name, state=_state_message(stream_name, legacy_state))

    assert error is None
    assert [record["id"] for record in records] == expected_ids
    assert len(states[-1].stream.stream_state.__dict__["states"]) == 1


def test_team_members_and_memberships_legacy_scenario(rate_limit_mock_response, requests_mock):
    """`test_stream_team_members_full_refresh`, ported: two teams, a member in both, and a
    membership GitHub answers 404 for, which is skipped while the rest sync."""
    config = _config("org1/repo")
    _mock_repository_resolution(requests_mock, "org1/repo")
    requests_mock.get(f"{_API}/orgs/org1/teams", json=[{"id": 1, "slug": "team1"}, {"id": 2, "slug": "team2"}])
    requests_mock.get(f"{_API}/orgs/org1/teams/team1/members", json=[{"id": 1, "login": "login1"}, {"id": 2, "login": "login2"}])
    requests_mock.get(f"{_API}/orgs/org1/teams/team2/members", json=[{"id": 2, "login": "login2"}, {"id": 3, "login": "login3"}])
    requests_mock.get(f"{_API}/orgs/org1/teams/team1/memberships/login1", json={"url": "1/1", "username": "login1"})
    requests_mock.get(f"{_API}/orgs/org1/teams/team1/memberships/login2", json={"url": "1/2", "username": "login2"})
    requests_mock.get(f"{_API}/orgs/org1/teams/team2/memberships/login2", json={"url": "2/2", "username": "login2"})
    requests_mock.get(f"{_API}/orgs/org1/teams/team2/memberships/login3", status_code=404, json={"message": "Not Found"})

    records, statuses, _, error = _read(config, "team_members")
    assert error is None
    assert sorted(records, key=lambda record: (record["team_slug"], record["login"])) == [
        {"id": 1, "login": "login1", "organization": "org1", "team_slug": "team1"},
        {"id": 2, "login": "login2", "organization": "org1", "team_slug": "team1"},
        {"id": 2, "login": "login2", "organization": "org1", "team_slug": "team2"},
        {"id": 3, "login": "login3", "organization": "org1", "team_slug": "team2"},
    ]

    records, statuses, _, error = _read(config, "team_memberships")
    assert error is None
    assert statuses[-1] == "COMPLETE"
    assert sorted(records, key=lambda record: record["url"]) == [
        {"url": "1/1", "username": "login1", "organization": "org1", "team_slug": "team1"},
        {"url": "1/2", "username": "login2", "organization": "org1", "team_slug": "team1"},
        {"url": "2/2", "username": "login2", "organization": "org1", "team_slug": "team2"},
    ]


def test_issue_timeline_events_expand_every_issue_regardless_of_start_date(rate_limit_mock_response, requests_mock):
    """Legacy `IssueTimelineEvents` built its `Issues` parent without `start_date`, so the timeline
    of every issue was read. The parent here is the `issues` definition with its window opened to
    the epoch, which selects the same issues."""
    config = _config(_REPO)
    _mock_repository_resolution(requests_mock, _REPO)
    requests_mock.get(f"{_API}/repos/{_REPO}/issues", json=[_record(id=30, number=3, updated_at=_BEFORE_START)])
    requests_mock.get(f"{_API}/repos/{_REPO}/issues/3/timeline", json=[{"event": "closed"}])

    records, _, _, error = _read(config, "issue_timeline_events")

    assert error is None
    assert records == [{"closed": {"event": "closed"}, "repository": _REPO, "issue_number": 3}]
    assert [request.qs["since"] for request in _requested(requests_mock, "/issues") if request.path.endswith("/issues")] == [["1970-01-01t00:00:00z"]]


def test_issue_timeline_events_collapse_a_page_into_one_record(rate_limit_mock_response, requests_mock):
    """`test_issues_timeline_events`, ported onto the fixture files it used: the page of timeline
    events becomes one record keyed by event type, plus `repository` and `issue_number`."""
    config = _config("airbytehq/airbyte")
    _mock_repository_resolution(requests_mock, "airbytehq/airbyte")
    requests_mock.get(f"{_API}/repos/airbytehq/airbyte/issues", json=[_record(id=1, number=1, updated_at=_AFTER_START)])
    requests_mock.get(
        f"{_API}/repos/airbytehq/airbyte/issues/1/timeline",
        json=json.load(open(Path(__file__).parent / "responses/issue_timeline_events.json")),
    )

    records, _, _, error = _read(config, "issue_timeline_events")

    assert error is None
    assert records == json.load(open(Path(__file__).parent / "responses/issue_timeline_events_response.json"))


@pytest.mark.parametrize(
    "response",
    [
        pytest.param({"json": []}, id="empty_list"),
        pytest.param({"text": "<html>Bad Gateway</html>"}, id="html_body"),
        pytest.param({"text": ""}, id="empty_body"),
        pytest.param({"json": {"message": "error"}}, id="dict_instead_of_list"),
        pytest.param({"json": "not_a_list"}, id="string_instead_of_list"),
    ],
)
def test_issue_timeline_events_odd_bodies_yield_the_bare_record(response, rate_limit_mock_response, requests_mock):
    """`test_issue_timeline_events_parse_response_defensive`, ported: a body that is not a list
    of events still produces the `repository`/`issue_number` record, never a failure."""
    config = _config(_REPO)
    _mock_repository_resolution(requests_mock, _REPO)
    requests_mock.get(f"{_API}/repos/{_REPO}/issues", json=[_record(id=30, number=3, updated_at=_AFTER_START)])
    requests_mock.get(f"{_API}/repos/{_REPO}/issues/3/timeline", **response)

    records, statuses, _, error = _read(config, "issue_timeline_events")

    assert error is None
    assert statuses[-1] == "COMPLETE"
    assert records == [{"repository": _REPO, "issue_number": 3}]
