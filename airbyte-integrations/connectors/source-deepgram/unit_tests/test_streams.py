# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for `source-deepgram` declarative streams."""

from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import requests_mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


def _get_manifest_path() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_MANIFEST_PATH = _get_manifest_path() / "manifest.yaml"
_CONFIG = {"api_key": "test-key", "start_date": "2024-01-01T00:00:00Z"}
_BASE_URL = "https://api.deepgram.com"
_STREAM_NAMES = ["projects", "requests", "keys", "balances", "usage", "usage_fields"]

_PROJECTS = {
    "projects": [
        {"project_id": "proj-1", "name": "Project One"},
        {"project_id": "proj-2", "name": "Project Two"},
    ]
}


def _get_source():
    return YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=CatalogBuilder().build(),
        config=_CONFIG,
        state=StateBuilder().build(),
    )


def _read(stream_name, sync_mode=SyncMode.full_refresh):
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    return read(_get_source(), _CONFIG, catalog)


def _mock_projects(mocker):
    mocker.get(f"{_BASE_URL}/v1/projects", json=_PROJECTS)


def _query(request):
    return parse_qs(urlsplit(request.url).query)


def _first_page_matcher(request):
    # PageIncrement does not inject the page token on the first request
    return _query(request).get("page") in (None, ["0"])


def _page_matcher(page):
    def _match(request):
        return _query(request).get("page") == [str(page)]

    return _match


def test_projects_stream():
    with requests_mock.Mocker() as mocker:
        _mock_projects(mocker)
        output = _read("projects")

    records = [message.record.data for message in output.records]
    assert len(records) == 2
    assert {record["project_id"] for record in records} == {"proj-1", "proj-2"}


def test_auth_header():
    with requests_mock.Mocker() as mocker:
        _mock_projects(mocker)
        _read("projects")

        projects_requests = [r for r in mocker.request_history if r.path == "/v1/projects"]
        assert projects_requests
        assert all(r.headers["Authorization"] == "Token test-key" for r in projects_requests)


def test_requests_pagination_and_incremental():
    page_0_body = {
        "requests": [
            {"request_id": "req-1", "created": "2024-03-01T10:00:00.000Z"},
            {"request_id": "req-2", "created": "2024-03-02T10:00:00.000Z"},
        ]
    }
    empty_body = {"requests": []}

    with requests_mock.Mocker() as mocker:
        _mock_projects(mocker)
        mocker.get(
            f"{_BASE_URL}/v1/projects/proj-1/requests",
            json=page_0_body,
            additional_matcher=_first_page_matcher,
        )
        mocker.get(
            f"{_BASE_URL}/v1/projects/proj-1/requests",
            json=empty_body,
            additional_matcher=_page_matcher(1),
        )
        mocker.get(f"{_BASE_URL}/v1/projects/proj-2/requests", json=empty_body)
        output = _read("requests", SyncMode.incremental)

        records = [message.record.data for message in output.records]
        assert [record["request_id"] for record in records] == ["req-1", "req-2"]

        requests_calls = [r for r in mocker.request_history if r.path.endswith("/requests")]
        first_query = _query(requests_calls[0])
        assert first_query["limit"] == ["1000"]
        assert first_query.get("page") in (None, ["0"])
        assert first_query["start"] == ["2024-01-01T00:00:00"]
        assert "end" in first_query
        # A partial page (2 < limit=1000) ends pagination, so page=1 is never requested.
        assert all(_query(call)["limit"] == ["1000"] for call in requests_calls)

    state_messages = output.state_messages
    assert state_messages
    stream_state = vars(state_messages[-1].state.stream.stream_state)
    assert stream_state["state"]["created"] == "2024-03-02T10:00:00"
    partition_cursors = {
        partition_state["partition"]["project_id"]: partition_state["cursor"]["created"] for partition_state in stream_state["states"]
    }
    assert partition_cursors["proj-1"] == "2024-03-02T10:00:00"
    assert partition_cursors["proj-2"] == "2024-01-01T00:00:00"


def test_keys_flattening():
    keys_body = {
        "api_keys": [
            {
                "member": {"member_id": "member-1", "email": "user@example.com"},
                "api_key": {"api_key_id": "key-1", "comment": "test key", "scopes": ["member"]},
            }
        ]
    }

    with requests_mock.Mocker() as mocker:
        _mock_projects(mocker)
        mocker.get(f"{_BASE_URL}/v1/projects/proj-1/keys", json=keys_body)
        mocker.get(f"{_BASE_URL}/v1/projects/proj-2/keys", json={"api_keys": []})
        output = _read("keys")

    records = [message.record.data for message in output.records]
    assert len(records) == 1
    assert records[0]["api_key_id"] == "key-1"
    assert records[0]["project_id"] == "proj-1"


def test_balances():
    def _balances_body(project_id):
        return {"balances": [{"balance_id": f"bal-{project_id}", "amount": 100.0, "units": "credits"}]}

    with requests_mock.Mocker() as mocker:
        _mock_projects(mocker)
        mocker.get(f"{_BASE_URL}/v1/projects/proj-1/balances", json=_balances_body("proj-1"))
        mocker.get(f"{_BASE_URL}/v1/projects/proj-2/balances", json=_balances_body("proj-2"))
        output = _read("balances")

    records = [message.record.data for message in output.records]
    assert len(records) == 2
    assert {record["project_id"] for record in records} == {"proj-1", "proj-2"}


def _usage_body():
    return {
        "start": "2024-01-01",
        "end": "2024-03-02",
        "resolution": {"units": "day", "amount": 1},
        "results": [{"start": "2024-01-01", "hours": 1.5, "requests": 3}],
    }


def _usage_fields_body():
    return {
        "tags": [],
        "models": [{"name": "nova-2", "language": "en", "version": "2024-01-01", "model_id": "model-1"}],
        "processing_methods": ["async"],
        "features": ["diarization"],
    }


def test_usage_and_usage_fields():
    with requests_mock.Mocker() as mocker:
        _mock_projects(mocker)
        for project_id in ("proj-1", "proj-2"):
            mocker.get(f"{_BASE_URL}/v1/projects/{project_id}/usage", json=_usage_body())
            mocker.get(f"{_BASE_URL}/v1/projects/{project_id}/usage/fields", json=_usage_fields_body())

        usage_output = _read("usage")
        usage_records = [message.record.data for message in usage_output.records]
        assert len(usage_records) == 2
        assert {record["project_id"] for record in usage_records} == {"proj-1", "proj-2"}

        usage_calls = [r for r in mocker.request_history if r.path.endswith("/usage")]
        assert all(_query(r)["start"] == ["2024-01-01"] for r in usage_calls)
        assert all("end" in _query(r) for r in usage_calls)

        fields_output = _read("usage_fields")
        fields_records = [message.record.data for message in fields_output.records]
        assert len(fields_records) == 2
        assert {record["project_id"] for record in fields_records} == {"proj-1", "proj-2"}

        fields_calls = [r for r in mocker.request_history if r.path.endswith("/usage/fields")]
        assert all(_query(r)["start"] == ["2024-01-01"] for r in fields_calls)
        assert all("end" in _query(r) for r in fields_calls)


def test_all_streams_present():
    assert {stream.name for stream in _get_source().streams(_CONFIG)} == set(_STREAM_NAMES)
