#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Behavior of the server-side incremental REST streams migrated to the manifest.

`comments`, `issues` and `review_comments` were the connector's `IncrementalMixin` streams:
`GithubStream` sliced on the resolved repository list, sent `since=max(start_date, state)` so
GitHub filtered by `updated_at` server-side, paginated on the `rel="next"` link header, stamped
`repository` onto every record and renamed the `+1`/`-1` reaction counts. Each test below asserts
parity with that implementation.

The shared repo-scoped error contract (404/403/409/410 skip the repository, 502 fails the stream,
secondary-limit 403 is retried) is pinned once in `test_manifest_repo_scoped_streams.py`; these
three streams reuse the same `skip_inaccessible_error_handler`, so only `comments`'s raised retry
budget is re-asserted here.
"""

import logging
from unittest.mock import patch

import pytest
from source_github.source import SourceGithub
from source_github.streams import Comments, Issues

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


# (stream name, endpoint segment under repos/{repository}/)
MIGRATED_STREAMS = [
    ("comments", "issues/comments"),
    ("issues", "issues"),
    ("review_comments", "pulls/comments"),
]

_TOKEN_CONFIG = {"credentials": {"personal_access_token": "token"}}
_START_DATE = "2022-02-02T10:10:01Z"


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


def _legacy_state(stream_name, **per_repository_cursor):
    """The state shape the Python streams wrote: `{repository: {updated_at: ...}}`."""
    return [
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name=stream_name),
                stream_state=AirbyteStateBlob({repository: {"updated_at": cursor} for repository, cursor in per_repository_cursor.items()}),
            ),
        )
    ]


def _next_link(url):
    return {"Link": f'<{url}>; rel="next"'}


def _listings(requests_mock, endpoint):
    return [request for request in requests_mock.request_history if request.path.endswith(f"/{endpoint}")]


@pytest.mark.parametrize(("stream_name", "endpoint"), MIGRATED_STREAMS)
def test_stream_reads_every_repository_and_injects_repository(stream_name, endpoint, rate_limit_mock_response, requests_mock):
    config = _config("airbytehq/airbyte", "docker/compose")
    _mock_repository_resolution(requests_mock, *config["repositories"])
    for repository in config["repositories"]:
        requests_mock.get(
            f"https://api.github.com/repos/{repository}/{endpoint}",
            json=[{"id": 1, "updated_at": "2022-03-01T00:00:00Z"}, {"id": 2, "updated_at": "2022-03-02T00:00:00Z"}],
        )

    records, statuses, _, error = _read(config, stream_name)

    assert error is None
    assert statuses[-1] == "COMPLETE"
    assert len(records) == 4
    # `repository` is absent from the GitHub payload, so it can only come from the manifest's
    # AddFields transformation — the replacement for `GithubStream.transform` (streams.py).
    assert sorted({record["repository"] for record in records}) == ["airbytehq/airbyte", "docker/compose"]


@pytest.mark.parametrize(("stream_name", "endpoint"), MIGRATED_STREAMS)
def test_endpoint_path_matches_legacy(stream_name, endpoint, rate_limit_mock_response, requests_mock):
    """Two of the three paths do not follow from the stream name: `comments` reads
    `issues/comments` (plain `comments` is `commit_comments`) and `review_comments` reads
    `pulls/comments`. Legacy overrode `path()` for both."""
    config = _config("docker/compose")
    _mock_repository_resolution(requests_mock, "docker/compose")
    requests_mock.get(f"https://api.github.com/repos/docker/compose/{endpoint}", json=[{"id": 1, "updated_at": "2022-03-01T00:00:00Z"}])

    records, _, _, error = _read(config, stream_name)

    assert error is None
    assert len(records) == 1
    assert [request.path for request in _listings(requests_mock, endpoint)] == [f"/repos/docker/compose/{endpoint}"]


@pytest.mark.parametrize(("stream_name", "endpoint"), MIGRATED_STREAMS)
def test_start_date_is_sent_as_since_on_a_first_sync(stream_name, endpoint, rate_limit_mock_response, requests_mock):
    """`since` is the whole point of this group: GitHub filters by `updated_at >= since`
    server-side, so losing the parameter would make every sync a full re-read."""
    config = _config("docker/compose")
    _mock_repository_resolution(requests_mock, "docker/compose")
    requests_mock.get(f"https://api.github.com/repos/docker/compose/{endpoint}", json=[])

    _, _, _, error = _read(config, stream_name)

    assert error is None
    assert [request.qs["since"] for request in _listings(requests_mock, endpoint)] == [[_START_DATE.lower()]]


@pytest.mark.parametrize(("stream_name", "endpoint"), MIGRATED_STREAMS)
def test_missing_start_date_sends_2008(stream_name, endpoint, rate_limit_mock_response, requests_mock):
    """Legacy sent no `since` at all with no `start_date` (`get_starting_point` returned "").
    `DatetimeBasedCursor` requires a start, so the manifest falls back to 2008-01-01, which predates
    every GitHub repository and selects the same records. Not the epoch: GitHub answers
    `since=1970-01-01T00:00:00Z` on the issues endpoint with an empty list. A present-but-null
    `start_date` must take that path too rather than rendering as the literal "None"."""
    config = {**_config("docker/compose"), "start_date": None}
    _mock_repository_resolution(requests_mock, "docker/compose")
    requests_mock.get(f"https://api.github.com/repos/docker/compose/{endpoint}", json=[])

    _, _, _, error = _read(config, stream_name)

    assert error is None
    assert [request.qs["since"] for request in _listings(requests_mock, endpoint)] == [["2008-01-01t00:00:00z"]]


@pytest.mark.parametrize(("stream_name", "endpoint"), MIGRATED_STREAMS)
def test_emitted_state_is_per_repository_and_resumes_the_next_sync(stream_name, endpoint, rate_limit_mock_response, requests_mock):
    """The cursor must be tracked per repository, not globally: legacy kept one `updated_at` per
    repository, and a single shared value would skip records in every repository but the most
    recently updated one."""
    config = _config("airbytehq/airbyte", "docker/compose")
    _mock_repository_resolution(requests_mock, *config["repositories"])
    requests_mock.get(
        f"https://api.github.com/repos/airbytehq/airbyte/{endpoint}",
        json=[{"id": 1, "updated_at": "2022-03-01T00:00:00Z"}],
    )
    requests_mock.get(
        f"https://api.github.com/repos/docker/compose/{endpoint}",
        json=[{"id": 2, "updated_at": "2022-04-01T00:00:00Z"}],
    )

    _, _, states, error = _read(config, stream_name)

    assert error is None
    assert states, f"the {stream_name} stream emitted no state message"
    assert sorted(states[-1].stream.stream_state.states, key=lambda entry: entry["partition"]["repository"]) == [
        {"partition": {"repository": "airbytehq/airbyte"}, "cursor": {"updated_at": "2022-03-01T00:00:00Z"}},
        {"partition": {"repository": "docker/compose"}, "cursor": {"updated_at": "2022-04-01T00:00:00Z"}},
    ]

    _, _, _, error = _read(config, stream_name, state=[states[-1]])

    assert error is None
    # Each repository resumes from its own cursor, exactly as `get_starting_point` did.
    assert sorted(request.qs["since"][0] for request in _listings(requests_mock, endpoint)[-2:]) == [
        "2022-03-01t00:00:00z",
        "2022-04-01t00:00:00z",
    ]


@pytest.mark.parametrize(("stream_name", "endpoint"), MIGRATED_STREAMS)
def test_legacy_state_migrates_to_per_partition_state(stream_name, endpoint, rate_limit_mock_response, requests_mock):
    """Existing connections carry `{repository: {updated_at: ...}}`. Without
    `LegacyToPerPartitionStateMigration` the CDK would not recognise it, drop it, and re-read
    every repository from `start_date`."""
    config = _config("docker/compose")
    _mock_repository_resolution(requests_mock, "docker/compose")
    requests_mock.get(f"https://api.github.com/repos/docker/compose/{endpoint}", json=[])

    state = _legacy_state(stream_name, **{"docker/compose": "2025-06-01T00:00:00Z"})
    _, _, states, error = _read(config, stream_name, state=state)

    assert error is None
    assert [request.qs["since"] for request in _listings(requests_mock, endpoint)] == [["2025-06-01t00:00:00z"]]
    assert states[-1].stream.stream_state.states == [
        {"partition": {"repository": "docker/compose"}, "cursor": {"updated_at": "2025-06-01T00:00:00Z"}}
    ]


@pytest.mark.parametrize(("stream_name", "endpoint"), MIGRATED_STREAMS)
def test_page_size_comes_from_page_size_for_large_streams(stream_name, endpoint, rate_limit_mock_response, requests_mock):
    """All three were `large_stream = True`, so their `per_page` came from
    `page_size_for_large_streams` — not the 100 the full-refresh group sends."""
    config = _config("docker/compose", page_size_for_large_streams=42)
    _mock_repository_resolution(requests_mock, "docker/compose")
    requests_mock.get(f"https://api.github.com/repos/docker/compose/{endpoint}", json=[])

    _, _, _, error = _read(config, stream_name)

    assert error is None
    assert [request.qs["per_page"] for request in _listings(requests_mock, endpoint)] == [["42"]]


@pytest.mark.parametrize(("stream_name", "endpoint"), MIGRATED_STREAMS)
def test_page_size_defaults_to_ten(stream_name, endpoint, rate_limit_mock_response, requests_mock):
    """`constants.DEFAULT_PAGE_SIZE_FOR_LARGE_STREAM`. A present-but-null value must fall back
    to it as well rather than reaching GitHub as `per_page=None`."""
    config = _config("docker/compose", page_size_for_large_streams=None)
    _mock_repository_resolution(requests_mock, "docker/compose")
    requests_mock.get(f"https://api.github.com/repos/docker/compose/{endpoint}", json=[])

    _, _, _, error = _read(config, stream_name)

    assert error is None
    assert [request.qs["per_page"] for request in _listings(requests_mock, endpoint)] == [["10"]]


@pytest.mark.parametrize(("stream_name", "endpoint"), MIGRATED_STREAMS)
def test_pagination_follows_link_header(stream_name, endpoint, rate_limit_mock_response, requests_mock):
    """GitHub's end-of-data signal is the absence of `rel="next"`, not a short page — and every
    page must keep carrying `since`, or page 2 would be unfiltered."""
    config = _config("docker/compose")
    _mock_repository_resolution(requests_mock, "docker/compose")
    requests_mock.get(
        f"https://api.github.com/repos/docker/compose/{endpoint}",
        [
            {
                "json": [{"id": 1, "updated_at": "2022-03-01T00:00:00Z"}],
                "headers": _next_link(f"https://api.github.com/repos/docker/compose/{endpoint}?page=2"),
            },
            {"json": [{"id": 2, "updated_at": "2022-03-02T00:00:00Z"}]},
        ],
    )

    records, _, _, error = _read(config, stream_name)

    assert error is None
    assert [record["id"] for record in records] == [1, 2]
    listings = _listings(requests_mock, endpoint)
    assert [request.qs.get("page") for request in listings] == [None, ["2"]]
    assert all(request.qs["since"] == [_START_DATE.lower()] for request in listings)


def test_issues_sends_the_legacy_base_params(rate_limit_mock_response, requests_mock):
    """`Issues.stream_base_params`. `state=all` is the load-bearing one: without it GitHub
    returns open issues only and every closed issue silently disappears from the stream."""
    config = _config("docker/compose", page_size_for_large_streams=25)
    _mock_repository_resolution(requests_mock, "docker/compose")
    requests_mock.get("https://api.github.com/repos/docker/compose/issues", json=[])

    _, _, _, error = _read(config, "issues")

    assert error is None
    (request,) = _listings(requests_mock, "issues")
    assert request.qs["state"] == ["all"]
    assert request.qs["sort"] == ["updated"]
    assert request.qs["direction"] == ["asc"]
    # Restating `request_parameters` on the stream replaces the requester's dict rather than
    # merging into it, so `per_page` has to be restated with it.
    assert request.qs["per_page"] == ["25"]


@pytest.mark.parametrize(("stream_name", "endpoint"), MIGRATED_STREAMS)
def test_reaction_counts_are_renamed(stream_name, endpoint, rate_limit_mock_response, requests_mock):
    """`GithubStream.transform` renamed `+1`/`-1` to `plus_one`/`minus_one` and popped the
    originals. `schemas/shared/reactions.json` declares only the renamed keys, so dropping the
    rename would lose both counts."""
    config = _config("docker/compose")
    _mock_repository_resolution(requests_mock, "docker/compose")
    requests_mock.get(
        f"https://api.github.com/repos/docker/compose/{endpoint}",
        json=[
            {
                "id": 1,
                "updated_at": "2022-03-01T00:00:00Z",
                "reactions": {"total_count": 5, "+1": 2, "-1": 1, "heart": 2},
            }
        ],
    )

    records, _, _, error = _read(config, stream_name)

    assert error is None
    (reactions,) = [record["reactions"] for record in records]
    assert reactions == {"total_count": 5, "plus_one": 2, "minus_one": 1, "heart": 2}


@pytest.mark.parametrize(
    ("reactions", "expected"),
    [
        pytest.param({"total_count": 0, "+1": 0, "-1": 0}, {"total_count": 0, "plus_one": 0, "minus_one": 0}, id="zero_counts_are_kept"),
        pytest.param({"total_count": 3, "heart": 3}, {"total_count": 3, "heart": 3}, id="absent_counts_are_not_invented"),
        pytest.param({}, {}, id="empty_reactions_object_is_left_alone"),
    ],
)
def test_reaction_rename_edge_cases(reactions, expected, rate_limit_mock_response, requests_mock):
    """A count of 0 renders as "0" and must survive the `value is not none` condition, and a
    record with no `+1`/`-1` must not gain them — `dpath.new` would otherwise create the keys
    (and the parent object) out of nothing."""
    config = _config("docker/compose")
    _mock_repository_resolution(requests_mock, "docker/compose")
    requests_mock.get(
        "https://api.github.com/repos/docker/compose/issues/comments",
        json=[{"id": 1, "updated_at": "2022-03-01T00:00:00Z", "reactions": reactions}],
    )

    records, _, _, error = _read(config, "comments")

    assert error is None
    assert [record["reactions"] for record in records] == [expected]


def test_reaction_less_record_does_not_gain_a_reactions_object(rate_limit_mock_response, requests_mock):
    """Legacy's transform was guarded by `if "reactions" in record and record["reactions"]`."""
    config = _config("docker/compose")
    _mock_repository_resolution(requests_mock, "docker/compose")
    requests_mock.get(
        "https://api.github.com/repos/docker/compose/pulls/comments",
        json=[{"id": 1, "updated_at": "2022-03-01T00:00:00Z"}],
    )

    records, _, _, error = _read(config, "review_comments")

    assert error is None
    assert "reactions" not in records[0]


@patch("time.sleep")
def test_comments_retries_seven_times(sleep_mock, rate_limit_mock_response, requests_mock):
    """`Comments.max_retries = 7`, against the base 5 every other repo-scoped stream used.
    `DefaultErrorHandler` defaults to 5, so `comments_error_handler` exists only to keep this."""
    config = _config("docker/compose")
    _mock_repository_resolution(requests_mock, "docker/compose")
    listing = requests_mock.get(
        "https://api.github.com/repos/docker/compose/issues/comments",
        status_code=502,
        json={"message": "Server Error"},
    )

    _, statuses, _, error = _read(config, "comments")

    assert statuses[-1] == "INCOMPLETE"
    assert error is not None
    assert listing.call_count == 8  # the first attempt plus seven retries


@patch("time.sleep")
def test_review_comments_retries_five_times(sleep_mock, rate_limit_mock_response, requests_mock):
    """The raised budget is `comments`-only; the other two keep the CDK default, which matches
    the `GithubStreamABC.max_retries` they inherited."""
    config = _config("docker/compose")
    _mock_repository_resolution(requests_mock, "docker/compose")
    listing = requests_mock.get(
        "https://api.github.com/repos/docker/compose/pulls/comments",
        status_code=502,
        json={"message": "Server Error"},
    )

    _, statuses, _, error = _read(config, "review_comments")

    assert statuses[-1] == "INCOMPLETE"
    assert error is not None
    assert listing.call_count == 6  # the first attempt plus five retries


@pytest.mark.parametrize(("stream_name", "endpoint"), MIGRATED_STREAMS)
def test_stream_primary_key_and_sync_modes_match_legacy(stream_name, endpoint):
    """`GithubStreamABC.primary_key = "id"` and `cursor_field = "updated_at"`. Changing either
    would make existing destinations deduplicate on a different key."""
    config = _config("docker/compose")
    source = SourceGithub(config=config)
    # `super()` skips `SourceGithub.streams()`, which returns the Python streams only.
    manifest_streams = {stream.name: stream for stream in super(SourceGithub, source).streams(config=config)}

    airbyte_stream = manifest_streams[stream_name].as_airbyte_stream()
    assert airbyte_stream.source_defined_primary_key == [["id"]]
    assert airbyte_stream.default_cursor_field == ["updated_at"]
    assert set(airbyte_stream.supported_sync_modes) == {SyncMode.full_refresh, SyncMode.incremental}


def test_streams_are_served_by_the_manifest_only(rate_limit_mock_response, requests_mock):
    """The Python `streams()` override must no longer return these three, and `discover` must
    still report each of them exactly once."""
    config = _config("docker/compose")
    _mock_repository_resolution(requests_mock, "docker/compose")
    requests_mock.get("https://api.github.com/repos/docker/compose/branches", json=[{"name": "master"}])

    migrated = {name for name, _ in MIGRATED_STREAMS}
    assert {stream.name for stream in SourceGithub(config=dict(config)).streams(config=dict(config))} & migrated == set()

    discovered = [stream.name for stream in SourceGithub(config=dict(config)).discover(logging.getLogger("airbyte"), dict(config)).streams]
    for name in migrated:
        assert discovered.count(name) == 1


@pytest.mark.parametrize(
    ("technical_stream", "child", "fields"),
    [
        (Comments, "IssueCommentReactions", ["repository", "id"]),
        (Issues, "IssueTimelineEvents", ["repository", "number"]),
    ],
)
def test_technical_parent_streams_still_answer_get_json_schema(technical_stream, child, fields):
    """`Comments` and `Issues` stay in `streams.py` after this step because `{child}` constructs
    them as its parent and is only migrated in Step 7. Their schema files were deleted with the
    migration, so both override `get_json_schema` rather than falling back to the missing file."""
    stream = technical_stream(repositories=["docker/compose"], page_size_for_large_streams=10)

    schema = stream.get_json_schema()

    assert schema["type"] == "object"
    assert set(fields) <= set(schema["properties"])


def test_comments_two_sync_parity_with_legacy(rate_limit_mock_response, requests_mock):
    """The scenario `test_stream_comments` used to drive through the Python `Comments` class:
    two repositories, `page_size_for_large_streams = 2`, three linked pages on the second sync.

    Two syncs, and the first sync's state drives the second — the same shape the legacy test
    asserted, with one deliberate difference called out below.
    """
    config = _config("organization/repository", "airbytehq/airbyte", page_size_for_large_streams=2)
    _mock_repository_resolution(requests_mock, *config["repositories"])

    # `updated_at` values per repository, ordered ascending, as GitHub serves them.
    data = {
        "organization/repository": [
            {"id": 1, "updated_at": "2022-02-02T10:10:02Z"},
            {"id": 2, "updated_at": "2022-02-02T10:10:04Z"},
            {"id": 3, "updated_at": "2022-02-02T10:12:06Z"},
            {"id": 4, "updated_at": "2022-02-02T10:12:08Z"},
            {"id": 5, "updated_at": "2022-02-02T10:12:10Z"},
            {"id": 6, "updated_at": "2022-02-02T10:12:12Z"},
        ],
        "airbytehq/airbyte": [
            {"id": 1, "updated_at": "2022-02-02T10:11:02Z"},
            {"id": 2, "updated_at": "2022-02-02T10:11:04Z"},
            {"id": 3, "updated_at": "2022-02-02T10:13:06Z"},
            {"id": 4, "updated_at": "2022-02-02T10:13:08Z"},
            {"id": 5, "updated_at": "2022-02-02T10:13:10Z"},
            {"id": 6, "updated_at": "2022-02-02T10:13:12Z"},
        ],
    }

    for repository, records in data.items():
        url = f"https://api.github.com/repos/{repository}/issues/comments"
        second_sync_since = records[1]["updated_at"]
        # First sync: `since` is the config start date and GitHub answers one unlinked page.
        requests_mock.get(f"{url}?per_page=2&since={_START_DATE}", json=records[0:2])
        # Second sync: `since` is the cursor the first sync stored, and the listing is three
        # linked pages. GitHub's `since` is inclusive, so the boundary record comes back.
        requests_mock.get(f"{url}?per_page=2&since={second_sync_since}", json=records[1:3], headers=_next_link(f"{url}?page=2"))
        requests_mock.get(f"{url}?per_page=2&page=2&since={second_sync_since}", json=records[3:5], headers=_next_link(f"{url}?page=3"))
        requests_mock.get(f"{url}?per_page=2&page=3&since={second_sync_since}", json=records[5:])

    records, statuses, states, error = _read(config, "comments")

    assert error is None
    assert statuses[-1] == "COMPLETE"
    assert sorted((record["repository"], record["id"]) for record in records) == [
        ("airbytehq/airbyte", 1),
        ("airbytehq/airbyte", 2),
        ("organization/repository", 1),
        ("organization/repository", 2),
    ]
    assert sorted(states[-1].stream.stream_state.states, key=lambda entry: entry["partition"]["repository"]) == [
        {"partition": {"repository": "airbytehq/airbyte"}, "cursor": {"updated_at": "2022-02-02T10:11:04Z"}},
        {"partition": {"repository": "organization/repository"}, "cursor": {"updated_at": "2022-02-02T10:10:04Z"}},
    ]

    records, statuses, states, error = _read(config, "comments", state=[states[-1]])

    assert error is None
    assert statuses[-1] == "COMPLETE"
    # DELIBERATE DIVERGENCE from the legacy test, which expected ids 3-6 per repository. `since`
    # is inclusive, so id 2 — whose `updated_at` is exactly the stored cursor — is on the first
    # page again. Legacy dropped it in `SemiIncrementalMixin.read_records` (`cursor_value >
    # start_point`, strictly greater); the manifest carries no client-side filter because the
    # CDK's is inclusive at the start and so would not drop it either. The record is unchanged
    # and destinations dedupe it on `id`. See `server_side_since_cursor` in the manifest.
    assert sorted((record["repository"], record["id"]) for record in records) == [
        ("airbytehq/airbyte", 2),
        ("airbytehq/airbyte", 3),
        ("airbytehq/airbyte", 4),
        ("airbytehq/airbyte", 5),
        ("airbytehq/airbyte", 6),
        ("organization/repository", 2),
        ("organization/repository", 3),
        ("organization/repository", 4),
        ("organization/repository", 5),
        ("organization/repository", 6),
    ]
    assert sorted(states[-1].stream.stream_state.states, key=lambda entry: entry["partition"]["repository"]) == [
        {"partition": {"repository": "airbytehq/airbyte"}, "cursor": {"updated_at": "2022-02-02T10:13:12Z"}},
        {"partition": {"repository": "organization/repository"}, "cursor": {"updated_at": "2022-02-02T10:12:12Z"}},
    ]
