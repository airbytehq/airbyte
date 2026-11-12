#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import Mock
from urllib.parse import parse_qs, urlparse

import pytest
from freezegun import freeze_time

from airbyte_cdk import YamlDeclarativeSource
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover as entrypoint_discover
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.state_builder import StateBuilder

from .conftest import _YAML_FILE_PATH, BASE_CONFIG, GROUPS_LIST_URL, get_source


START_DATE = "2026-06-01T00:00:00Z"
NOW = "2026-10-01T00:00:00Z"
EPOCH = "1970-01-01T00:00:00Z"
PROJECT_CONFIG = BASE_CONFIG | {"projects_list": ["p_1", "p_2"], "start_date": START_DATE}
GROUP_CONFIG = BASE_CONFIG | {"groups_list": ["g_1", "g_2"], "start_date": START_DATE}
PROJECT_IDS = {"p_1": 11, "p_2": 22}
GROUP_IDS = ["g_1", "g_2"]

SERVER_STREAMS = [
    pytest.param("deployments", PROJECT_CONFIG, list(PROJECT_IDS.values()), id="deployments"),
    pytest.param("project_milestones", PROJECT_CONFIG, list(PROJECT_IDS.values()), id="project_milestones"),
    pytest.param("group_milestones", GROUP_CONFIG, GROUP_IDS, id="group_milestones"),
]

SERVER_RECORDS = {
    "deployments": {
        11: [
            {"id": 101, "updated_at": "2018-01-01T00:00:00Z"},
            {"id": 102, "updated_at": "2026-06-10T12:00:00Z"},
        ],
        22: [{"id": 201, "updated_at": "2026-06-20T12:00:00Z"}],
    },
    "project_milestones": {
        11: [
            {"id": 301, "updated_at": "2018-02-01T00:00:00Z"},
            {"id": 302, "updated_at": "2026-06-11T12:00:00Z"},
        ],
        22: [{"id": 401, "updated_at": "2026-06-21T12:00:00Z"}],
    },
    "group_milestones": {
        "g_1": [
            {"id": 501, "updated_at": "2018-03-01T00:00:00Z"},
            {"id": 502, "updated_at": "2026-06-12T12:00:00Z"},
        ],
        "g_2": [{"id": 601, "updated_at": "2026-06-22T12:00:00Z"}],
    },
}


@pytest.fixture(autouse=True)
def _frozen_clock():
    with freeze_time(NOW):
        yield


def _read(stream_name, config, sync_mode=SyncMode.incremental, state=None):
    catalog = CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(stream_name).with_sync_mode(sync_mode)).build()
    state_messages = StateBuilder().with_stream_state(stream_name, state).build() if state is not None else StateBuilder().build()
    source = YamlDeclarativeSource(
        path_to_yaml=str(_YAML_FILE_PATH),
        config=config,
        state=state_messages,
        catalog=catalog,
    )
    source.write_config = Mock()
    output = entrypoint_read(source=source, config=config, catalog=catalog, state=state_messages)
    output.raise_if_errors()
    return output


def _mock_partition_sources(requests_mock, config):
    if "projects_list" in config:
        requests_mock.get(url=GROUPS_LIST_URL, json=[])
        for project_path, project_id in PROJECT_IDS.items():
            requests_mock.get(
                f"/api/v4/projects/{project_path}",
                json=[{"id": project_id, "path_with_namespace": project_path}],
            )
    else:
        for group_id in GROUP_IDS:
            requests_mock.get(f"/api/v4/groups/{group_id}?per_page=50", json=[{"id": group_id}])
            requests_mock.get(f"/api/v4/groups/{group_id}/descendant_groups?per_page=50", json=[])


def _stream_path(stream_name, partition_id):
    if stream_name == "deployments":
        return f"/api/v4/projects/{partition_id}/deployments"
    if stream_name == "project_milestones":
        return f"/api/v4/projects/{partition_id}/milestones"
    return f"/api/v4/groups/{partition_id}/milestones"


def _mock_server_records(requests_mock, stream_name, partition_ids):
    for partition_id in partition_ids:
        requests_mock.get(_stream_path(stream_name, partition_id), json=SERVER_RECORDS[stream_name][partition_id])


def _server_requests(requests_mock, stream_name):
    suffix = "/deployments" if stream_name == "deployments" else "/milestones"
    return [request for request in requests_mock.request_history if urlparse(request.url).path.endswith(suffix)]


def _request_signature(request):
    return urlparse(request.url).path, parse_qs(urlparse(request.url).query)


def _expected_server_requests(stream_name, partition_ids, updated_after):
    expected = []
    for partition_id in partition_ids:
        query = {"per_page": ["50"], "updated_after": [updated_after[partition_id]], "updated_before": [NOW]}
        if stream_name == "deployments":
            query.update({"order_by": ["updated_at"], "sort": ["asc"]})
        expected.append((_stream_path(stream_name, partition_id), query))
    return expected


def _server_cursor_by_partition(output):
    state = output.most_recent_state.stream_state.__dict__
    return {partition_state["partition"]["id"]: partition_state["cursor"]["updated_at"] for partition_state in state["states"]}


def _max_updated_at_by_partition(stream_name, partition_ids):
    return {
        partition_id: max(record["updated_at"] for record in SERVER_RECORDS[stream_name][partition_id]) for partition_id in partition_ids
    }


def _assert_server_query(requests_mock, stream_name, partition_ids, updated_after):
    assert sorted(_request_signature(request) for request in _server_requests(requests_mock, stream_name)) == sorted(
        _expected_server_requests(stream_name, partition_ids, updated_after)
    )


def _discover_catalog(config):
    output = entrypoint_discover(source=get_source(config=config), config=config)
    output.raise_if_errors()
    return {stream.name: stream for stream in output.catalog.catalog.streams}


def test_incremental_stream_discovery():
    discovered = _discover_catalog(PROJECT_CONFIG)
    discovered.update(_discover_catalog(GROUP_CONFIG))

    for stream_name in ("deployments", "project_milestones", "group_milestones"):
        stream = discovered[stream_name]
        assert SyncMode.incremental in stream.supported_sync_modes
        assert stream.source_defined_cursor
        assert stream.default_cursor_field == ["updated_at"]

    stream = discovered["merge_request_commits"]
    assert SyncMode.incremental in stream.supported_sync_modes
    assert stream.source_defined_cursor
    assert stream.default_cursor_field == ["merge_request_updated_at"]


@pytest.mark.parametrize(("stream_name", "config", "partition_ids"), SERVER_STREAMS)
def test_server_side_incremental_first_read_uses_epoch_for_every_partition(requests_mock, stream_name, config, partition_ids):
    _mock_partition_sources(requests_mock, config)
    _mock_server_records(requests_mock, stream_name, partition_ids)

    output = _read(stream_name, config)

    assert len(output.records) == sum(len(SERVER_RECORDS[stream_name][partition_id]) for partition_id in partition_ids)
    _assert_server_query(requests_mock, stream_name, partition_ids, dict.fromkeys(partition_ids, EPOCH))
    assert _server_cursor_by_partition(output) == _max_updated_at_by_partition(stream_name, partition_ids)


@pytest.mark.parametrize(("stream_name", "config", "partition_ids"), SERVER_STREAMS)
def test_server_side_incremental_second_read_uses_partition_cursors(requests_mock, stream_name, config, partition_ids):
    _mock_partition_sources(requests_mock, config)
    _mock_server_records(requests_mock, stream_name, partition_ids)
    first_output = _read(stream_name, config)
    first_state = first_output.most_recent_state.stream_state.__dict__

    requests_mock.reset_mock()
    second_output = _read(stream_name, config, state=first_state)

    _assert_server_query(requests_mock, stream_name, partition_ids, _max_updated_at_by_partition(stream_name, partition_ids))
    assert len(second_output.records) == len(first_output.records)


def test_deployments_full_refresh_uses_epoch_and_returns_every_record(requests_mock):
    _mock_partition_sources(requests_mock, PROJECT_CONFIG)
    _mock_server_records(requests_mock, "deployments", PROJECT_IDS.values())

    output = _read("deployments", PROJECT_CONFIG, sync_mode=SyncMode.full_refresh)

    assert len(output.records) == sum(len(records) for records in SERVER_RECORDS["deployments"].values())
    _assert_server_query(requests_mock, "deployments", PROJECT_IDS.values(), dict.fromkeys(PROJECT_IDS.values(), EPOCH))


MERGE_REQUESTS = {
    11: [{"id": 1101, "iid": 10, "updated_at": "2026-06-10T12:00:00Z"}],
    22: [{"id": 2201, "iid": 20, "updated_at": "2026-06-20T12:00:00Z"}],
}
UPDATED_MERGE_REQUESTS = {
    11: [{"id": 1101, "iid": 10, "updated_at": "2026-09-10T12:00:00Z"}],
    22: [],
}


def _mock_merge_requests(requests_mock):
    _mock_partition_sources(requests_mock, PROJECT_CONFIG)
    for project_id, project_path in ((11, "p_1"), (22, "p_2")):
        endpoint = f"/api/v4/projects/{project_id}/merge_requests"

        def response(request, context, project_id=project_id):
            updated_after = parse_qs(urlparse(request.url).query)["updated_after"][0]
            if updated_after == START_DATE:
                records = MERGE_REQUESTS[project_id]
            else:
                records = UPDATED_MERGE_REQUESTS[project_id]
            return json.dumps(records)

        requests_mock.get(endpoint, text=response)
        for merge_request in MERGE_REQUESTS[project_id]:
            requests_mock.get(
                f"{endpoint}/{merge_request['iid']}/commits",
                json=[{"id": f"commit-{project_path}", "message": "first read"}],
            )
        updated_merge_request = UPDATED_MERGE_REQUESTS[project_id]
        if updated_merge_request:
            requests_mock.get(
                f"{endpoint}/{updated_merge_request[0]['iid']}/commits",
                json=[{"id": f"commit-{project_path}", "message": "second read"}],
            )


def _merge_request_list_requests(requests_mock):
    return [request for request in requests_mock.request_history if urlparse(request.url).path.endswith("/merge_requests")]


def _merge_request_commit_requests(requests_mock):
    return [request for request in requests_mock.request_history if urlparse(request.url).path.endswith("/commits")]


def _expected_merge_request_request(project_id, updated_after):
    return (
        f"/api/v4/projects/{project_id}/merge_requests",
        {"per_page": ["50"], "scope": ["all"], "updated_after": [updated_after], "updated_before": [NOW]},
    )


def _parent_merge_request_cursors(state):
    return {entry["partition"]["id"]: entry["cursor"]["updated_at"] for entry in state["parent_state"]["merge_requests"]["states"]}


def test_merge_request_commits_incrementally_follows_parent_merge_requests(requests_mock):
    _mock_merge_requests(requests_mock)
    output = _read("merge_request_commits", PROJECT_CONFIG)

    first_parent_requests = [_expected_merge_request_request(project_id, START_DATE) for project_id in PROJECT_IDS.values()]
    assert sorted(_request_signature(request) for request in _merge_request_list_requests(requests_mock)) == sorted(first_parent_requests)
    assert sorted(urlparse(request.url).path for request in _merge_request_commit_requests(requests_mock)) == [
        "/api/v4/projects/11/merge_requests/10/commits",
        "/api/v4/projects/22/merge_requests/20/commits",
    ]
    assert {record.record.data["merge_request_updated_at"] for record in output.records} == {
        mr[0]["updated_at"] for mr in MERGE_REQUESTS.values()
    }

    first_state = output.most_recent_state.stream_state.__dict__
    assert first_state["use_global_cursor"] is True
    assert first_state["parent_state"]["merge_requests"]
    assert _parent_merge_request_cursors(first_state) == {project_id: mrs[0]["updated_at"] for project_id, mrs in MERGE_REQUESTS.items()}

    requests_mock.reset_mock()
    second_output = _read("merge_request_commits", PROJECT_CONFIG, state=first_state)

    second_parent_requests = [
        _expected_merge_request_request(project_id, MERGE_REQUESTS[project_id][0]["updated_at"]) for project_id in PROJECT_IDS.values()
    ]
    assert sorted(_request_signature(request) for request in _merge_request_list_requests(requests_mock)) == sorted(second_parent_requests)
    assert [urlparse(request.url).path for request in _merge_request_commit_requests(requests_mock)] == [
        "/api/v4/projects/11/merge_requests/10/commits"
    ]
    assert [record.record.data["merge_request_updated_at"] for record in second_output.records] == [
        UPDATED_MERGE_REQUESTS[11][0]["updated_at"]
    ]
