#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Behavior of the organization-scoped full-refresh REST streams migrated to the manifest.

Each test asserts parity with the Python implementation these streams replaced: `Organizations`
and its two subclasses sliced on the resolved organization list, requested
`orgs/{organization}[/...]?per_page=100`, paginated on GitHub's `rel="next"` link header, and
warned-and-continued on 404/403 for a single organization rather than failing the sync.

One deliberate asymmetry is pinned here: `Teams` and `Users` stamped `organization` onto every
record, `Organizations` did not — its `parse_response` yielded the API payload untouched, and
`organizations.json` never declared the field.
"""

import logging

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


# (stream name, path under orgs/{organization}, whether the legacy transform injected `organization`)
MIGRATED_STREAMS = [
    ("organizations", "", False),
    ("teams", "/teams", True),
    ("users", "/members", True),
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


def _read(config, stream_name):
    catalog = _catalog(stream_name)
    source = SourceGithub(config=dict(config), catalog=catalog, state=[])
    messages, error = [], None
    try:
        for message in source.read(logging.getLogger("airbyte"), dict(config), catalog, []):
            messages.append(message)
    except Exception as exc:  # noqa: BLE001 - the assertions inspect the failure
        error = exc
    records = [message.record.data for message in messages if message.type == Type.RECORD]
    statuses = [
        message.trace.stream_status.status.value for message in messages if message.type == Type.TRACE and message.trace.stream_status
    ]
    return records, statuses, error


def _mock_repository_resolution(requests_mock, *repositories):
    """Explicit `org/repo` entries resolve through the manifest's `repository_stats` stream, which
    is also what supplies the organization partitions these streams slice on."""
    for index, repository in enumerate(repositories, start=1):
        requests_mock.get(
            f"https://api.github.com/repos/{repository}",
            json={"id": index, "full_name": repository, "organization": {"login": repository.split("/")[0]}},
        )


def _payload(stream_name):
    if stream_name == "organizations":
        return {"id": 1, "login": "airbytehq", "node_id": "MDEyOk9yZ2FuaXphdGlvbjE="}
    return [{"id": 1, "login": "first", "slug": "first"}, {"id": 2, "login": "second", "slug": "second"}]


@pytest.mark.parametrize(("stream_name", "path", "injects_organization"), MIGRATED_STREAMS)
def test_stream_reads_every_organization(stream_name, path, injects_organization, rate_limit_mock_response, requests_mock):
    config = _config("airbytehq/airbyte", "docker/compose")
    _mock_repository_resolution(requests_mock, *config["repositories"])
    for organization in ("airbytehq", "docker"):
        requests_mock.get(f"https://api.github.com/orgs/{organization}{path}", json=_payload(stream_name))

    records, statuses, error = _read(config, stream_name)

    assert error is None
    assert statuses[-1] == "COMPLETE"
    assert len(records) == (2 if stream_name == "organizations" else 4)

    expected_paths = {f"/orgs/{organization}{path}" for organization in ("airbytehq", "docker")}
    listings = [request for request in requests_mock.request_history if request.path in expected_paths]
    assert len(listings) == 2
    for request in listings:
        assert request.qs["per_page"] == ["100"]
        assert "page" not in request.qs


@pytest.mark.parametrize(("stream_name", "path", "injects_organization"), MIGRATED_STREAMS)
def test_organization_injection_matches_legacy(stream_name, path, injects_organization, rate_limit_mock_response, requests_mock):
    """`Teams.parse_response` and `Users.parse_response` called `transform`, which set
    `record["organization"]`. `Organizations.parse_response` did not, so adding the field there
    would emit something the Python implementation never produced."""
    config = _config("airbytehq/airbyte")
    _mock_repository_resolution(requests_mock, *config["repositories"])
    requests_mock.get(f"https://api.github.com/orgs/airbytehq{path}", json=_payload(stream_name))

    records, _, error = _read(config, stream_name)

    assert error is None
    assert records
    if injects_organization:
        assert {record["organization"] for record in records} == {"airbytehq"}
    else:
        assert "organization" not in records[0]


@pytest.mark.parametrize(("stream_name", "path", "injects_organization"), MIGRATED_STREAMS)
def test_stream_primary_key_matches_legacy(stream_name, path, injects_organization):
    """All three declared `id`; changing it would re-key existing destinations."""
    config = _config("airbytehq/airbyte")
    source = SourceGithub(config=config)
    manifest_streams = {stream.name: stream for stream in super(SourceGithub, source).streams(config=config)}

    assert manifest_streams[stream_name]._primary_key == ["id"]


@pytest.mark.parametrize(
    ("status_code", "body"), [(404, {"message": "Not Found"}), (403, {"message": "Resource protected by organization SAML enforcement"})]
)
def test_inaccessible_organization_is_skipped(status_code, body, rate_limit_mock_response, requests_mock):
    """Legacy `read_records` caught both and warned — "isn't available for organization" on 404,
    "may be missing the `read:org` scope" on 403 — then carried on with the next organization."""
    config = _config("airbytehq/airbyte", "docker/compose")
    _mock_repository_resolution(requests_mock, *config["repositories"])
    requests_mock.get("https://api.github.com/orgs/airbytehq/teams", status_code=status_code, json=body)
    requests_mock.get("https://api.github.com/orgs/docker/teams", json=[{"id": 2, "slug": "compose"}])

    records, statuses, error = _read(config, "teams")

    assert error is None
    assert statuses[-1] == "COMPLETE"
    assert [record["id"] for record in records] == [2]


def test_pagination_follows_link_header(rate_limit_mock_response, requests_mock):
    config = _config("airbytehq/airbyte")
    _mock_repository_resolution(requests_mock, *config["repositories"])
    requests_mock.get(
        "https://api.github.com/orgs/airbytehq/members",
        [
            {
                "json": [{"id": 1, "login": "first"}],
                "headers": {"Link": '<https://api.github.com/orgs/airbytehq/members?page=2>; rel="next"'},
            },
            {"json": [{"id": 2, "login": "second"}]},
        ],
    )

    records, _, error = _read(config, "users")

    assert error is None
    assert [record["id"] for record in records] == [1, 2]
