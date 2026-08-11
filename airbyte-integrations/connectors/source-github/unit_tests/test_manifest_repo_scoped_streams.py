#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Behavior of the repo-scoped full-refresh REST streams migrated to the manifest.

Each test asserts parity with the Python implementation these streams replaced:
`GithubStream` sliced on the resolved repository list, requested
`repos/{repository}/<endpoint>?per_page=100`, paginated on GitHub's `rel="next"` link
header, stamped `repository` onto every record, and warned-and-continued on 404/403/409
for a single repository instead of failing the whole sync.
"""

import logging
from unittest.mock import patch

import pytest
from source_github.source import SourceGithub

from airbyte_cdk.models import (
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type,
)


# (stream name, endpoint segment under repos/{repository}/, primary key)
MIGRATED_STREAMS = [
    ("assignees", "assignees", ["id"]),
    ("branches", "branches", ["repository", "name"]),
    ("collaborators", "collaborators", ["id"]),
    ("issue_labels", "labels", ["id"]),
    ("tags", "tags", ["repository", "name"]),
]

_TOKEN_CONFIG = {"credentials": {"personal_access_token": "token"}}


def _config(*repositories):
    return {**_TOKEN_CONFIG, "repositories": list(repositories)}


def _catalog(*stream_names):
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name=stream_name, json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            )
            for stream_name in stream_names
        ]
    )


def _read_messages(config, *stream_names):
    """Return (messages, error); the caller decides what to assert on."""
    catalog = _catalog(*stream_names)
    source = SourceGithub(config=dict(config), catalog=catalog, state=[])
    messages, error = [], None
    try:
        # Appended one at a time so the messages emitted before a failure are still available.
        for message in source.read(logging.getLogger("airbyte"), dict(config), catalog, []):
            messages.append(message)
    except Exception as exc:  # noqa: BLE001 - the assertions inspect the failure
        error = exc
    return messages, error


def _read(config, stream_name):
    messages, error = _read_messages(config, stream_name)
    records = [message.record.data for message in messages if message.type == Type.RECORD]
    statuses = [
        message.trace.stream_status.status.value for message in messages if message.type == Type.TRACE and message.trace.stream_status
    ]
    return records, statuses, error


def _mock_repository_resolution(requests_mock, *repositories):
    """Explicit `org/repo` entries resolve through the manifest's `repository_stats` stream."""
    for index, repository in enumerate(repositories, start=1):
        requests_mock.get(
            f"https://api.github.com/repos/{repository}",
            json={"id": index, "full_name": repository, "organization": {"login": repository.split("/")[0]}},
        )


def _next_link(url):
    return {"Link": f'<{url}>; rel="next"'}


@pytest.mark.parametrize(("stream_name", "endpoint", "primary_key"), MIGRATED_STREAMS)
def test_stream_reads_every_repository_and_injects_repository(stream_name, endpoint, primary_key, rate_limit_mock_response, requests_mock):
    config = _config("airbytehq/airbyte", "docker/compose")
    _mock_repository_resolution(requests_mock, *config["repositories"])
    for repository in config["repositories"]:
        requests_mock.get(
            f"https://api.github.com/repos/{repository}/{endpoint}",
            json=[{"id": 1, "name": "first"}, {"id": 2, "name": "second"}],
        )

    records, statuses, error = _read(config, stream_name)

    assert error is None
    assert statuses[-1] == "COMPLETE"
    assert len(records) == 4
    # `repository` is absent from the GitHub payload, so it can only come from the manifest's
    # AddFields transformation — the replacement for `GithubStream.transform` (streams.py).
    assert sorted({record["repository"] for record in records}) == ["airbytehq/airbyte", "docker/compose"]

    listings = [request for request in requests_mock.request_history if request.path.endswith(f"/{endpoint}")]
    assert len(listings) == 2
    for request in listings:
        assert request.qs["per_page"] == ["100"]
        # The first request must carry no `page`; CursorPagination has no initial token.
        assert "page" not in request.qs


@pytest.mark.parametrize(("stream_name", "endpoint", "primary_key"), MIGRATED_STREAMS)
def test_stream_primary_key_matches_legacy(stream_name, endpoint, primary_key):
    """The primary keys the Python classes declared must survive the migration, otherwise
    existing destinations would start deduplicating on a different key."""
    config = _config("airbytehq/airbyte")
    source = SourceGithub(config=config)
    # `super()` skips `SourceGithub.streams()`, which returns the Python streams only.
    manifest_streams = {stream.name: stream for stream in super(SourceGithub, source).streams(config=config)}

    airbyte_stream = manifest_streams[stream_name].as_airbyte_stream()
    assert airbyte_stream.source_defined_primary_key == [[field] for field in primary_key]
    assert airbyte_stream.supported_sync_modes == [SyncMode.full_refresh]


def test_streams_are_served_by_the_manifest_only(rate_limit_mock_response, requests_mock):
    """The Python `streams()` override must no longer return these streams, and `discover`
    must still report each of them exactly once."""
    config = _config("airbytehq/airbyte")
    _mock_repository_resolution(requests_mock, "airbytehq/airbyte")
    requests_mock.get("https://api.github.com/repos/airbytehq/airbyte/branches", json=[{"name": "master"}])

    source = SourceGithub(config=dict(config))
    migrated = {name for name, _, _ in MIGRATED_STREAMS}

    assert {stream.name for stream in source.streams(config=dict(config))} & migrated == set()

    discovered = [stream.name for stream in source.discover(logging.getLogger("airbyte"), dict(config)).streams]
    for name in migrated:
        assert discovered.count(name) == 1


def test_pagination_follows_link_header(rate_limit_mock_response, requests_mock):
    """A short page carrying a next link must still be followed: GitHub's documented
    end-of-data signal is the absence of `rel="next"`, not a page shorter than `per_page`."""
    config = _config("airbytehq/airbyte")
    _mock_repository_resolution(requests_mock, "airbytehq/airbyte")
    requests_mock.get(
        "https://api.github.com/repos/airbytehq/airbyte/tags",
        [
            {"json": [{"name": "v1"}], "headers": _next_link("https://api.github.com/repos/airbytehq/airbyte/tags?page=2")},
            {"json": [{"name": "v2"}]},
        ],
    )

    records, _, error = _read(config, "tags")

    assert error is None
    assert [record["name"] for record in records] == ["v1", "v2"]
    listings = [request for request in requests_mock.request_history if request.path.endswith("/tags")]
    assert [request.qs.get("page") for request in listings] == [None, ["2"]]


@pytest.mark.parametrize(
    ("status_code", "body", "expected_log"),
    [
        (404, {"message": "Not Found"}, "Syncing this stream isn't available"),
        (403, {"message": "Resource not accessible by personal access token"}, "GitHub denied access to this repository"),
        (409, {"message": "Git Repository is empty."}, "The repository is likely empty"),
    ],
)
@patch("time.sleep")
def test_inaccessible_repository_is_skipped(sleep_mock, status_code, body, expected_log, rate_limit_mock_response, requests_mock, caplog):
    """Legacy warned and continued on 404/403/409 for a single repository (streams.py
    `GithubStreamABC.read_records`). One unreadable repository must not fail the stream or
    drop the repositories that follow it, and the skip must leave a trace in the log."""
    config = _config("ghost/deleted-repo", "docker/compose")
    _mock_repository_resolution(requests_mock, *config["repositories"])
    requests_mock.get("https://api.github.com/repos/ghost/deleted-repo/tags", status_code=status_code, json=body)
    requests_mock.get("https://api.github.com/repos/docker/compose/tags", json=[{"name": "v1"}])

    with caplog.at_level(logging.INFO):
        records, statuses, error = _read(config, "tags")

    assert error is None
    assert statuses[-1] == "COMPLETE"
    assert [record["repository"] for record in records] == ["docker/compose"]
    # The declarative IGNORE path logs the filter's `error_message` at INFO. It carries no slice
    # context, so this cannot assert *which* repository was skipped — see the "KNOWN GAP" note in
    # the manifest's error-handling block.
    assert any(expected_log in message for message in caplog.messages)


@patch("time.sleep")
def test_repeated_502_fails_the_stream(sleep_mock, rate_limit_mock_response, requests_mock):
    """Deliberate divergence from legacy, pinned here so it cannot change silently.

    5xx is left to the CDK default mapping (RETRY), so a repository that keeps returning 502
    fails the stream once the retries are exhausted. Legacy retried the same way but
    `GithubStreamABC.read_records` caught the exhausted-retries exception for 502/504, warned and
    moved on — reporting a COMPLETE sync with that repository's records missing. See the
    "DELIBERATE DIVERGENCE" note in the manifest's error-handling block.
    """
    config = _config("docker/compose")
    _mock_repository_resolution(requests_mock, "docker/compose")
    listing = requests_mock.get(
        "https://api.github.com/repos/docker/compose/tags",
        status_code=502,
        json={"message": "Server Error"},
    )

    records, statuses, error = _read(config, "tags")

    assert records == []
    assert statuses[-1] == "INCOMPLETE"
    assert error is not None
    # Retried before giving up rather than skipping the repository on the first blip.
    assert listing.call_count > 1


@patch("time.sleep")
def test_secondary_rate_limit_403_is_retried_not_skipped(sleep_mock, rate_limit_mock_response, requests_mock):
    """GitHub reports secondary rate limits as 403. Those must be waited out rather than
    treated as an inaccessible repository — the rate-limit filters run before the 403 IGNORE
    filter, and swapping that order would silently drop the repository's records."""
    config = _config("docker/compose")
    _mock_repository_resolution(requests_mock, "docker/compose")
    requests_mock.get(
        "https://api.github.com/repos/docker/compose/tags",
        [
            {
                "status_code": 403,
                "headers": {"Retry-After": "120"},
                "json": {"message": "You have exceeded a secondary rate limit"},
            },
            {"json": [{"name": "v1"}]},
        ],
    )

    records, statuses, error = _read(config, "tags")

    assert error is None
    assert statuses[-1] == "COMPLETE"
    assert [record["name"] for record in records] == ["v1"]
    assert max(call.args[0] for call in sleep_mock.call_args_list) > 100


def test_repository_resolution_is_shared_across_streams(rate_limit_mock_response, requests_mock):
    """Every migrated stream builds its own copy of the partition router, so without the
    resolver's `use_cache: true` a five-stream catalog would resolve each repository five times.

    `num_workers: 1` pins the count: concurrent streams can race on a cold cache and duplicate a
    few resolutions, so at the default concurrency this is "roughly one request per repository",
    not exactly one.
    """
    config = {**_config("airbytehq/airbyte", "docker/compose"), "num_workers": 1}
    _mock_repository_resolution(requests_mock, *config["repositories"])
    for _, endpoint, _ in MIGRATED_STREAMS:
        for repository in config["repositories"]:
            requests_mock.get(f"https://api.github.com/repos/{repository}/{endpoint}", json=[{"id": 1, "name": "first"}])

    stream_names = [name for name, _, _ in MIGRATED_STREAMS]
    messages, error = _read_messages(config, *stream_names)

    assert error is None
    records = [message.record for message in messages if message.type == Type.RECORD]
    assert {record.stream for record in records} == set(stream_names)

    resolution_paths = [f"/repos/{repository}" for repository in config["repositories"]]
    resolutions = [request.path for request in requests_mock.request_history if request.path in resolution_paths]
    assert sorted(resolutions) == sorted(resolution_paths)


def test_repository_404_during_resolution_does_not_fail_the_stream(rate_limit_mock_response, requests_mock):
    """A repository deleted between syncs 404s while partitions are generated. It is skipped,
    and the remaining repositories are still synced."""
    config = _config("ghost/deleted-repo", "docker/compose")
    requests_mock.get("https://api.github.com/repos/ghost/deleted-repo", status_code=404, json={"message": "Not Found"})
    _mock_repository_resolution(requests_mock, "docker/compose")
    requests_mock.get("https://api.github.com/repos/docker/compose/collaborators", json=[{"id": 1, "login": "octocat"}])

    records, statuses, error = _read(config, "collaborators")

    assert error is None
    assert statuses[-1] == "COMPLETE"
    assert [record["repository"] for record in records] == ["docker/compose"]
