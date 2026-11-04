# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests_mock
import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover, read


def _get_manifest_path() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_MANIFEST_PATH = _get_manifest_path() / "manifest.yaml"
_CONFIG = {"credentials": {"auth_method": "api_key", "api_key": "key"}}
_BASE_URL = "https://api.airtable.com/v0"
_STREAM = "base_collaborators"
_BASES = {"app1": "Base One", "app2": "Base Two"}


def _collaborator(user_id, permission_level):
    return {
        "userId": user_id,
        "email": f"{user_id}@example.com",
        "permissionLevel": permission_level,
        "createdTime": "2026-01-01T00:00:00.000Z",
        "grantedByUserId": "usr0",
    }


# usr1 was added to both bases; usr2 owns the workspace without being added to either base.
_COLLABORATORS = {
    "app1": {"baseCollaborators": [_collaborator("usr1", "create")], "workspaceCollaborators": [_collaborator("usr2", "owner")]},
    "app2": {"baseCollaborators": [_collaborator("usr1", "read")], "workspaceCollaborators": [_collaborator("usr2", "owner")]},
}


def _base_response(request, context):
    base_id = urlparse(request.url).path.split("/")[-1]
    body = {
        "id": base_id,
        "name": _BASES[base_id],
        "permissionLevel": "create",
        "workspaceId": "wsp1",
        "createdTime": "2026-01-01T00:00:00.000Z",
    }
    # Like the API, collaborators are only returned when requested.
    if "collaborators" in parse_qs(urlparse(request.url).query).get("include[]", []):
        body["individualCollaborators"] = _COLLABORATORS[base_id]
        body["groupCollaborators"] = {"baseCollaborators": [], "workspaceCollaborators": []}
    return body


def _get_source():
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    return ConcurrentDeclarativeSource(source_config=manifest, config=_CONFIG, catalog=None, state=None)


def _mock_api(mocker):
    mocker.get(
        f"{_BASE_URL}/meta/bases",
        json={"bases": [{"id": base_id, "name": name, "permissionLevel": "create"} for base_id, name in _BASES.items()]},
    )
    for base_id in _BASES:
        mocker.get(
            f"{_BASE_URL}/meta/bases/{base_id}/tables",
            json={"tables": [{"id": "tbl1", "name": "Table", "fields": [{"name": "Name", "type": "singleLineText"}]}]},
        )
        mocker.get(f"{_BASE_URL}/meta/bases/{base_id}", json=_base_response)


def _read():
    catalog = CatalogBuilder().with_stream(_STREAM, SyncMode.full_refresh).build()
    with requests_mock.Mocker() as mocker:
        _mock_api(mocker)
        output = read(_get_source(), _CONFIG, catalog)
    return [message.record.data for message in output.records], mocker.request_history


def test_discover_lists_base_collaborators_next_to_table_streams():
    with requests_mock.Mocker() as mocker:
        _mock_api(mocker)
        output = discover(_get_source(), _CONFIG)

    streams = {stream.name: stream for stream in output.catalog.catalog.streams}
    assert set(streams) == {_STREAM, "base_one/table/tbl1", "base_two/table/tbl1"}
    assert streams[_STREAM].source_defined_primary_key == [["base_id"], ["userId"]]
    assert {mode.value for mode in streams[_STREAM].supported_sync_modes} == {"full_refresh"}


def test_reads_direct_base_collaborators_with_include_parameter():
    records, requests = _read()

    base_requests = [request for request in requests if urlparse(request.url).path in {"/v0/meta/bases/app1", "/v0/meta/bases/app2"}]
    assert len(base_requests) == 2
    assert all(parse_qs(urlparse(request.url).query) == {"include[]": ["collaborators"]} for request in base_requests)
    assert {record["userId"] for record in records} == {"usr1"}


def test_primary_key_is_unique_across_bases():
    records, _ = _read()

    assert sorted((record["base_id"], record["base_name"], record["userId"], record["permissionLevel"]) for record in records) == [
        ("app1", "Base One", "usr1", "create"),
        ("app2", "Base Two", "usr1", "read"),
    ]
