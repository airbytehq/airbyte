#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

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


def _repo(repo_id, full_name, org=None, updated_at="2026-01-01T00:00:00Z"):
    record = {
        "id": repo_id,
        "full_name": full_name,
        "owner": {"login": full_name.split("/")[0]},
        "updated_at": updated_at,
        "created_at": "2020-01-01T00:00:00Z",
        "pushed_at": updated_at,
    }
    if org:
        record["organization"] = {"login": org}
    return record


def _catalog():
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="repositories",
                    json_schema={},
                    supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
                ),
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.append,
            )
        ]
    )


def _read(config, state=None):
    catalog = _catalog()
    source = SourceGithub(config=dict(config), catalog=catalog, state=state)
    records, statuses, error = [], [], None
    try:
        for message in source.read(logging.getLogger("airbyte"), dict(config), catalog, state or []):
            if message.type == Type.RECORD:
                records.append(message.record.data["full_name"])
            if message.type == Type.TRACE and message.trace.stream_status:
                statuses.append(message.trace.stream_status.status.value)
    except Exception as exc:  # noqa: BLE001 - the assertions inspect the failure
        error = exc
    return records, statuses, error


def test_org_404_is_skipped_and_sync_completes(rate_limit_mock_response, requests_mock):
    """A 404 on one org (renamed/deleted) must not fail the sync for the remaining orgs."""
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["ghost-org/*", "airbytehq/*"]}
    requests_mock.get("https://api.github.com/orgs/ghost-org/repos", status_code=404, json={"message": "Not Found"})
    requests_mock.get("https://api.github.com/orgs/airbytehq/repos", json=[_repo(1, "airbytehq/airbyte", org="airbytehq")])

    records, statuses, error = _read(config)

    assert error is None
    assert records == ["airbytehq/airbyte"]
    assert statuses[-1] == "COMPLETE"


def test_explicit_repo_404_is_skipped_and_sync_completes(rate_limit_mock_response, requests_mock):
    """A deleted explicit repo 404s during partition generation and must be skipped, not fail the sync."""
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["docker/compose", "ghost/deleted-repo"]}
    requests_mock.get("https://api.github.com/repos/docker/compose", json=_repo(2, "docker/compose", org="docker"))
    requests_mock.get("https://api.github.com/repos/ghost/deleted-repo", status_code=404, json={"message": "Not Found"})
    requests_mock.get("https://api.github.com/orgs/docker/repos", json=[_repo(2, "docker/compose", org="docker")])

    records, statuses, error = _read(config)

    assert error is None
    assert sorted(set(records)) == ["docker/compose"]
    assert statuses[-1] == "COMPLETE"


def test_secondary_rate_limit_is_retried(rate_limit_mock_response, requests_mock):
    """GitHub secondary rate limits arrive as 403 + Retry-After and must be waited out, not failed."""
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["docker/*"]}
    requests_mock.get(
        "https://api.github.com/orgs/docker/repos",
        [
            {
                "status_code": 403,
                "headers": {"Retry-After": "0"},
                "json": {"message": "You have exceeded a secondary rate limit"},
            },
            {"json": [_repo(2, "docker/compose", org="docker")]},
        ],
    )

    records, statuses, error = _read(config)

    assert error is None
    assert records == ["docker/compose"]
    assert statuses[-1] == "COMPLETE"


def test_plain_403_fails_stream(rate_limit_mock_response, requests_mock):
    """A plain 403 (bad scopes / SAML SSO) must fail the stream so `check` can surface it."""
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["docker/*"]}
    requests_mock.get("https://api.github.com/orgs/docker/repos", status_code=403, json={"message": "Must have admin rights"})

    records, statuses, error = _read(config)

    assert records == []
    assert error is not None
    assert "403" in str(error)


def test_record_filter_mixed_wildcard_and_explicit_config(rate_limit_mock_response, requests_mock):
    """With wildcards present, only records matching the wildcard patterns are emitted —
    explicit repos outside the wildcard orgs drop, replicating the legacy pattern-from-wildcards behavior."""
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["airbytehq/*", "docker/compose"]}
    requests_mock.get("https://api.github.com/orgs/airbytehq/repos", json=[_repo(1, "airbytehq/airbyte", org="airbytehq")])
    requests_mock.get("https://api.github.com/repos/docker/compose", json=_repo(2, "docker/compose", org="docker"))
    requests_mock.get(
        "https://api.github.com/orgs/docker/repos",
        json=[_repo(2, "docker/compose", org="docker"), _repo(3, "docker/docker-py", org="docker")],
    )

    records, _, error = _read(config)

    assert error is None
    assert sorted(set(records)) == ["airbytehq/airbyte"]


def test_record_filter_explicit_only_config_emits_all_org_repos(rate_limit_mock_response, requests_mock):
    """With no wildcard patterns all repos of the explicit repos' orgs pass the filter,
    replicating the legacy `Repositories(pattern=None)` behavior."""
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["docker/compose"]}
    requests_mock.get("https://api.github.com/repos/docker/compose", json=_repo(2, "docker/compose", org="docker"))
    requests_mock.get(
        "https://api.github.com/orgs/docker/repos",
        json=[_repo(2, "docker/compose", org="docker"), _repo(3, "docker/docker-py", org="docker")],
    )

    records, _, error = _read(config)

    assert error is None
    assert sorted(set(records)) == ["docker/compose", "docker/docker-py"]


def test_legacy_state_migration_round_trip(rate_limit_mock_response, requests_mock):
    """Legacy `{org: {updated_at: ...}}` state must migrate to per-partition state and
    re-attach to the org partition so records at or below the cursor are filtered out."""
    config = {"credentials": {"personal_access_token": "token"}, "repositories": ["docker/*"]}
    legacy_state = [
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name="repositories"),
                stream_state=AirbyteStateBlob({"docker": {"updated_at": "2025-06-01T00:00:00Z"}}),
            ),
        )
    ]
    requests_mock.get(
        "https://api.github.com/orgs/docker/repos",
        json=[
            _repo(2, "docker/compose", org="docker", updated_at="2026-01-01T00:00:00Z"),
            _repo(3, "docker/old-repo", org="docker", updated_at="2024-01-01T00:00:00Z"),
        ],
    )

    records, statuses, error = _read(config, state=legacy_state)

    assert error is None
    assert records == ["docker/compose"]
    assert statuses[-1] == "COMPLETE"
