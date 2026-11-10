# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from urllib.parse import parse_qs, urlparse

import jsonschema
import pytest
import requests_cache
from source_asana.source import SourceAsana

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover, read


BASE = "https://app.asana.com/api/1.0"


@pytest.fixture(autouse=True)
def clear_cache(monkeypatch, mocker):
    monkeypatch.delenv("REQUEST_CACHE_PATH", raising=False)
    requests_cache.SQLiteCache("file::memory:?cache=shared").clear()
    mocker.patch("time.sleep")


@pytest.fixture(params=["pat", "oauth"])
def goal_config(request, requests_mock):
    credentials = {"option_title": "PAT Credentials", "personal_access_token": "token"}
    if request.param == "oauth":
        credentials = {"option_title": "OAuth Credentials", "client_id": "client", "client_secret": "secret", "refresh_token": "refresh"}
        requests_mock.post("https://app.asana.com/-/oauth_token", json={"access_token": "token", "expires_in": 3600})
    return {"credentials": credentials, "enable_goal_streams": True}


def source(config):
    return SourceAsana(config=config, catalog=None, state=None)


def read_goal_stream(config, stream="goals", expecting_exception=False):
    return read(
        source(config), config, CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build(), expecting_exception=expecting_exception
    )


def goal(gid="g1"):
    return {
        "gid": gid,
        "resource_type": "goal",
        "name": "Example goal",
        "notes": None,
        "html_notes": None,
        "start_on": "2026-01-01",
        "due_on": None,
        "is_workspace_level": True,
        "status": "achieved",
        "owner": {"gid": "owner", "name": "Example"},
        "workspace": {"gid": "w1"},
        "team": None,
        "time_period": {"gid": "t1", "display_name": "FY26"},
        "metric": {
            "gid": "metric",
            "resource_subtype": "number",
            "precision": 2,
            "unit": "percentage",
            "current_number_value": 0.75,
            "initial_number_value": 0,
            "target_number_value": 1,
            "currency_code": None,
        },
    }


def test_discovery_preserves_old_catalog(goal_config):
    old_config = {"credentials": goal_config["credentials"]}
    old = discover(source(old_config), old_config).catalog.catalog.streams
    expanded = discover(source(goal_config), goal_config).catalog.catalog.streams
    assert len(old) == 20
    assert {s.name for s in expanded} == {s.name for s in old} | {"goals", "time_periods"}
    old_streams = {s.name: s for s in old}
    assert all(s == old_streams[s.name] for s in expanded if s.name in old_streams)
    for stream in expanded:
        if stream.name in {"goals", "time_periods"}:
            assert stream.source_defined_primary_key == [["gid"]]
            assert stream.supported_sync_modes == [SyncMode.full_refresh]


def test_explicit_fields_preserve_metrics(goal_config, requests_mock):
    requests_mock.get(f"{BASE}/workspaces", json={"data": [{"gid": "w1"}]})
    endpoint = requests_mock.get(f"{BASE}/goals", json={"data": [goal()]})
    output = read_goal_stream(goal_config)
    assert len(output.records) == 1
    data = output.records[0].record.data
    assert data["metric"]["current_number_value"] == 0.75
    assert data["owner"]["gid"] == "owner"
    assert data["time_period"]["gid"] == "t1"
    assert data["workspace_gid"] == "w1"
    fields = set(endpoint.last_request.qs["opt_fields"][0].split(","))
    assert {"metric.current_number_value", "metric.target_number_value", "owner.gid", "time_period.gid", "workspace.gid"} <= fields
    assert endpoint.last_request.qs["workspace"] == ["w1"]
    assert endpoint.last_request.headers["Authorization"] == "Bearer token"
    assert endpoint.call_count == 1  # No detail request per goal.
    schema = next(s for s in source(goal_config).streams(goal_config) if s.name == "goals").get_json_schema()
    assert set(data) <= set(schema["properties"])
    jsonschema.validate(data, schema, format_checker=jsonschema.FormatChecker())


@pytest.mark.parametrize("stream", ["goals", "time_periods"])
def test_multiple_workspaces_independent_pagination(goal_config, requests_mock, stream):
    requests_mock.get(f"{BASE}/workspaces", json={"data": [{"gid": "w1"}, {"gid": "w2"}]})

    def response(request, context):
        workspace = request.qs["workspace"][0]
        token = parse_qs(urlparse(request.url).query).get("offset")
        if token is None:
            return {"data": [{"gid": f"{workspace}-1"}], "next_page": {"offset": f"{workspace}-AbC+/="}}
        assert token == [f"{workspace}-AbC+/="]
        return {"data": [{"gid": f"{workspace}-2"}], "next_page": None}

    endpoint = requests_mock.get(f"{BASE}/{stream}", json=response)
    output = read_goal_stream(goal_config, stream)
    assert {(r.record.data["gid"], r.record.data["workspace_gid"]) for r in output.records} == {
        (f"w{i}-{j}", f"w{i}") for i in [1, 2] for j in [1, 2]
    }
    assert endpoint.call_count == 4
    assert all(r.qs["limit"] == ["100"] for r in endpoint.request_history)


@pytest.mark.parametrize("stream", ["goals", "time_periods"])
@pytest.mark.parametrize("terminal", [{}, {"next_page": None}, {"next_page": {}}])
def test_empty_workspace_and_terminal_page(goal_config, requests_mock, stream, terminal):
    requests_mock.get(f"{BASE}/workspaces", json={"data": [{"gid": "w1"}]})
    endpoint = requests_mock.get(f"{BASE}/{stream}", json={"data": [], **terminal})
    output = read_goal_stream(goal_config, stream)
    assert not output.records
    assert not output.errors
    assert endpoint.call_count == 1


@pytest.mark.parametrize("stream", ["goals", "time_periods"])
@pytest.mark.parametrize("status", [401, 402, 403, 404])
def test_permissions_and_entitlement_fail(goal_config, requests_mock, stream, status):
    requests_mock.get(f"{BASE}/workspaces", json={"data": [{"gid": "w1"}]})
    endpoint = requests_mock.get(f"{BASE}/{stream}", status_code=status, json={"errors": [{"message": "Denied"}]})
    output = read_goal_stream(goal_config, stream, expecting_exception=True)
    assert output.errors
    assert endpoint.call_count == 1
    assert "Asana" in output.errors[0].trace.error.message


@pytest.mark.parametrize("status,headers", [(429, {"Retry-After": "0"}), (429, {}), (500, {}), (503, {})])
def test_transient_failures_retry(goal_config, requests_mock, status, headers):
    requests_mock.get(f"{BASE}/workspaces", json={"data": [{"gid": "w1"}]})
    endpoint = requests_mock.get(
        f"{BASE}/goals",
        [
            {"status_code": status, "json": {"errors": [{"message": "Temporary"}]}, "headers": headers},
            {"json": {"data": [goal()]}},
        ],
    )
    assert len(read_goal_stream(goal_config).records) == 1
    assert endpoint.call_count == 2


def test_workspace_denial_does_not_silently_skip_goal_data(goal_config, requests_mock):
    requests_mock.get(f"{BASE}/workspaces", status_code=403, json={"errors": [{"message": "Denied"}]})
    assert read_goal_stream(goal_config, expecting_exception=True).errors


def test_old_selected_stream_does_not_call_goals(goal_config, requests_mock):
    endpoint = requests_mock.get(f"{BASE}/workspaces", json={"data": [{"gid": "w1", "resource_type": "workspace"}], "next_page": None})
    config = {"credentials": goal_config["credentials"]}
    output = read_goal_stream(config, "workspaces")
    assert len(output.records) == 1
    assert endpoint.call_count == 1
    assert all(not r.path.endswith(("/goals", "/time_periods")) for r in requests_mock.request_history)


@pytest.mark.parametrize("stream", ["goals", "time_periods"])
def test_empty_nonterminal_page_continues(goal_config, requests_mock, stream):
    requests_mock.get(f"{BASE}/workspaces", json={"data": [{"gid": "w1"}]})
    endpoint = requests_mock.get(
        f"{BASE}/{stream}",
        [
            {"json": {"data": [], "next_page": {"offset": "next"}}},
            {"json": {"data": [{"gid": "record"}], "next_page": None}},
        ],
    )
    output = read_goal_stream(goal_config, stream)
    assert len(output.records) == 1
    assert endpoint.call_count == 2


def test_both_streams_share_workspace_enumeration_and_reset_tokens(goal_config, requests_mock):
    workspaces = requests_mock.get(f"{BASE}/workspaces", json={"data": [{"gid": "w1"}]})
    for stream in ["goals", "time_periods"]:
        requests_mock.get(
            f"{BASE}/{stream}",
            [
                {"json": {"data": [{"gid": stream + "-1"}], "next_page": {"offset": stream + "-next"}}},
                {"json": {"data": [{"gid": stream + "-2"}], "next_page": None}},
            ],
        )
    catalog = CatalogBuilder().with_stream("goals", SyncMode.full_refresh).with_stream("time_periods", SyncMode.full_refresh).build()
    output = read(source(goal_config), goal_config, catalog)
    assert len(output.records) == 4
    assert workspaces.call_count <= 2  # Concurrent reads may race before the cache is populated.
    for stream in ["goals", "time_periods"]:
        requests = [r for r in requests_mock.request_history if r.path.endswith("/" + stream)]
        assert "offset" not in requests[0].qs
        assert requests[1].qs["offset"] == [stream + "-next"]


def test_retries_are_bounded(goal_config, requests_mock):
    requests_mock.get(f"{BASE}/workspaces", json={"data": [{"gid": "w1"}]})
    endpoint = requests_mock.get(f"{BASE}/goals", status_code=503, json={"errors": [{"message": "Temporary"}]})
    assert read_goal_stream(goal_config, expecting_exception=True).errors
    assert endpoint.call_count == 6


def test_no_accessible_workspaces_is_successfully_empty(goal_config, requests_mock):
    endpoint = requests_mock.get(f"{BASE}/workspaces", json={"data": [], "next_page": None})
    output = read_goal_stream(goal_config)
    assert not output.errors
    assert not output.records
    assert endpoint.call_count == 1


@pytest.mark.parametrize("body", [{}, {"errors": []}, {"errors": None}])
def test_empty_permission_error_body_is_still_actionable(goal_config, requests_mock, body):
    requests_mock.get(f"{BASE}/workspaces", json={"data": [{"gid": "w1"}]})
    requests_mock.get(f"{BASE}/goals", status_code=403, json=body)
    output = read_goal_stream(goal_config, expecting_exception=True)
    assert output.errors
    assert "goals:read" in output.errors[0].trace.error.message
