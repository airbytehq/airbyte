# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


BASE_URL = "https://api.pipedrive.com/"
CONFIG = {"api_token": "tok", "replication_start_date": "2017-01-25 00:00:00Z"}
V1_PAGE_DONE = {"pagination": {"start": 0, "limit": 500, "more_items_in_collection": False}}


def _response(body, status_code=200):
    return HttpResponse(json.dumps(body), status_code)


def _read_stream(name, sync_mode=SyncMode.full_refresh):
    catalog = CatalogBuilder().with_stream(name, sync_mode).build()
    return read(get_source(CONFIG), CONFIG, catalog)


def _request(path, query_params):
    return HttpRequest(f"{BASE_URL}{path}", query_params=query_params)


def _ids(output, field="id"):
    return sorted(record.record.data[field] for record in output.records)


def _deals_response():
    return {
        "success": True,
        "data": [
            {"item": "deal", "id": 1, "data": {"id": 1, "update_time": "2024-01-01 00:00:00"}},
            {"item": "deal", "id": 2, "data": {"id": 2, "update_time": "2024-01-02 00:00:00"}},
        ],
        "additional_data": {"pagination": {"more_items_in_collection": False}},
    }


def _mock_deals(http_mocker):
    http_mocker.get(
        _request(
            "v1/recents",
            {
                "limit": "50",
                "items": "deal",
                "since_timestamp": "2017-01-25 00:00:00",
            },
        ),
        _response(_deals_response()),
    )


def test_call_logs_paginates():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("v1/callLogs", {"limit": "50"}),
            _response(
                {
                    "data": [{"id": "call-1"}, {"id": "call-2"}],
                    "additional_data": {"pagination": {"more_items_in_collection": True, "next_start": 50}},
                }
            ),
        )
        http_mocker.get(
            _request("v1/callLogs", {"limit": "50", "start": "50"}),
            _response({"data": [{"id": "call-3"}], "additional_data": {"pagination": {"more_items_in_collection": False}}}),
        )

        output = _read_stream("call_logs")

    assert _ids(output) == ["call-1", "call-2", "call-3"]


def test_call_logs_response_without_additional_data_is_a_single_page():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("v1/callLogs", {"limit": "50"}),
            _response({"success": True, "data": [{"id": "call-1"}]}),
        )

        output = _read_stream("call_logs")

    assert _ids(output) == ["call-1"]
    assert output.errors == []


def test_lead_sources():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("v1/leadSources", {}),
            _response({"data": [{"name": "Website"}, {"name": "Import"}], "additional_data": None}),
        )

        output = _read_stream("lead_sources")

    assert _ids(output, "name") == ["Import", "Website"]


def test_legacy_teams_reads_records():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("v1/legacyTeams", {}),
            _response({"data": [{"id": 1, "name": "Sales"}]}),
        )

        output = _read_stream("legacy_teams")

    assert _ids(output) == [1]


@pytest.mark.parametrize(
    "status_code, body",
    [
        pytest.param(403, {"success": False, "error": "Teams feature is not enabled in your company"}, id="feature_disabled"),
        pytest.param(410, {"success": False}, id="endpoint_retired"),
    ],
)
def test_legacy_teams_ignores_unavailable_endpoint(status_code, body):
    with HttpMocker() as http_mocker:
        http_mocker.get(_request("v1/legacyTeams", {}), _response(body, status_code=status_code))

        output = _read_stream("legacy_teams")

    assert output.records == []
    assert output.errors == []


def test_projects_paginates_active_and_archived_projects():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("api/v2/projects", {"limit": "500"}),
            _response({"data": [{"id": 1}], "additional_data": {"next_cursor": "abc"}}),
        )
        http_mocker.get(
            _request("api/v2/projects", {"limit": "500", "cursor": "abc"}),
            _response({"data": [{"id": 2}], "additional_data": {"next_cursor": None}}),
        )
        http_mocker.get(
            _request("api/v2/projects/archived", {"limit": "500"}),
            _response({"data": [{"id": 3}], "additional_data": {"next_cursor": None}}),
        )

        output = _read_stream("projects")

    assert _ids(output) == [1, 2, 3]


@pytest.mark.parametrize(
    "status_code, body",
    [
        pytest.param(402, {"success": False, "error": "Required suites missing", "errorCode": 402}, id="projects_suite_missing"),
        pytest.param(403, {"success": False}, id="forbidden"),
    ],
)
def test_projects_ignores_unavailable_endpoints(status_code, body):
    with HttpMocker() as http_mocker:
        http_mocker.get(_request("api/v2/projects", {"limit": "500"}), _response(body, status_code=status_code))
        http_mocker.get(_request("api/v2/projects/archived", {"limit": "500"}), _response(body, status_code=status_code))

        output = _read_stream("projects")

    assert output.records == []
    assert output.errors == []


def test_tasks_paginates():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("api/v2/tasks", {"limit": "500"}),
            _response({"data": [{"id": 1}], "additional_data": {"next_cursor": "abc"}}),
        )
        http_mocker.get(
            _request("api/v2/tasks", {"limit": "500", "cursor": "abc"}),
            _response({"data": [{"id": 2}]}),
        )

        output = _read_stream("tasks")

    assert _ids(output) == [1, 2]
    assert output.errors == []


def test_tasks_ignores_missing_projects_suite():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("api/v2/tasks", {"limit": "500"}),
            _response({"success": False, "error": "Required suites missing", "errorCode": 402}, status_code=402),
        )

        output = _read_stream("tasks")

    assert output.records == []
    assert output.errors == []


def test_deal_installments_batches_parent_deals_into_one_request():
    with HttpMocker() as http_mocker:
        _mock_deals(http_mocker)
        http_mocker.get(
            _request("api/v2/deals/installments", {"deal_ids": "1,2", "limit": "500"}),
            _response(
                {
                    "data": [{"id": 11, "deal_id": 1}, {"id": 22, "deal_id": 2}],
                    "additional_data": {"next_cursor": None},
                }
            ),
        )

        output = _read_stream("deal_installments")

    assert _ids(output, "deal_id") == [1, 2]


def test_deal_installments_ignores_plan_without_installments():
    with HttpMocker() as http_mocker:
        _mock_deals(http_mocker)
        http_mocker.get(
            _request("api/v2/deals/installments", {"deal_ids": "1,2", "limit": "500"}),
            _response({"success": False, "error": "The company does not have access to this feature"}, status_code=403),
        )

        output = _read_stream("deal_installments")

    assert output.records == []
    assert output.errors == []


def _flow_request(deal_id, start=None):
    params = {"limit": "500", "items": "dealChange", "all_changes": "1"}
    if start is not None:
        params["start"] = str(start)
    return _request(f"v1/deals/{deal_id}/flow", params)


def _flow_change(change_id, log_time, new_value="value"):
    return {
        "object": "dealChange",
        "timestamp": log_time,
        "data": {"id": change_id, "item_id": 1, "field_key": "value", "log_time": log_time, "old_value": None, "new_value": new_value},
    }


def test_deal_flow_flattens_filters_and_paginates():
    with HttpMocker() as http_mocker:
        _mock_deals(http_mocker)
        http_mocker.get(
            _flow_request(1),
            _response(
                {
                    "data": [_flow_change(101, "2016-01-01 00:00:00"), _flow_change(102, "2024-03-01 10:00:00", 100)],
                    "additional_data": {"pagination": {"start": 0, "limit": 500, "more_items_in_collection": True, "next_start": 500}},
                }
            ),
        )
        http_mocker.get(
            _flow_request(1, start=500),
            _response({"data": [_flow_change(103, "2024-03-02 10:00:00")], "additional_data": V1_PAGE_DONE}),
        )
        http_mocker.get(_flow_request(2), _response({"data": [], "additional_data": V1_PAGE_DONE}))

        output = _read_stream("deal_flow", SyncMode.incremental)

    assert _ids(output) == [102, 103]
    assert all("object" not in record.record.data for record in output.records)
    assert output.records[0].record.data["new_value"] in (100, "value")
    state = output.most_recent_state.stream_state.__dict__
    assert "parent_state" in state and "deals" in state["parent_state"]


def test_deal_flow_response_without_additional_data_is_a_single_page():
    with HttpMocker() as http_mocker:
        _mock_deals(http_mocker)
        http_mocker.get(_flow_request(1), _response({"success": True, "data": [_flow_change(101, "2024-03-01 10:00:00")]}))
        http_mocker.get(_flow_request(2), _response({"success": True, "data": []}))

        output = _read_stream("deal_flow", SyncMode.incremental)

    assert _ids(output) == [101]
    assert output.errors == []


def test_deal_flow_skips_a_deleted_parent_deal():
    with HttpMocker() as http_mocker:
        _mock_deals(http_mocker)
        http_mocker.get(_flow_request(1), _response({"data": [_flow_change(101, "2024-03-01 10:00:00")], "additional_data": V1_PAGE_DONE}))
        http_mocker.get(_flow_request(2), _response({"success": False, "error": "Deal not found"}, status_code=404))

        output = _read_stream("deal_flow", SyncMode.incremental)

    assert _ids(output) == [101]
    assert output.errors == []


def _mock_permission_sets(http_mocker):
    http_mocker.get(
        _request("v1/permissionSets", {"limit": "50"}),
        _response({"data": [{"id": "ps-1", "name": "Admin"}]}),
    )


def test_permission_set_assignments_reads_each_permission_set():
    with HttpMocker() as http_mocker:
        _mock_permission_sets(http_mocker)
        http_mocker.get(
            _request("v1/permissionSets/ps-1/assignments", {"limit": "500"}),
            _response(
                {
                    "data": [
                        {
                            "permission_set_id": "ps-1",
                            "user_id": 1,
                            "name": "Alice",
                            "permission_set_app": "sales",
                            "permission_set_type": "admin",
                        },
                        {
                            "permission_set_id": "ps-1",
                            "user_id": 2,
                            "name": "Bob",
                            "permission_set_app": "sales",
                            "permission_set_type": "admin",
                        },
                    ],
                    "additional_data": V1_PAGE_DONE,
                }
            ),
        )

        output = _read_stream("permission_set_assignments")

    assert _ids(output, "user_id") == [1, 2]


def test_permission_set_assignments_ignores_forbidden_endpoint():
    with HttpMocker() as http_mocker:
        _mock_permission_sets(http_mocker)
        http_mocker.get(
            _request("v1/permissionSets/ps-1/assignments", {"limit": "500"}),
            _response({"success": False, "error": "forbidden"}, status_code=403),
        )

        output = _read_stream("permission_set_assignments")

    assert output.records == []
    assert output.errors == []


def test_discover_lists_new_streams():
    catalog = get_source(CONFIG).discover(logging.getLogger(__name__), CONFIG)
    streams = {stream.name: stream for stream in catalog.streams}

    assert len(streams) == 34
    assert {
        "call_logs",
        "lead_sources",
        "legacy_teams",
        "projects",
        "tasks",
        "deal_installments",
        "deal_flow",
        "permission_set_assignments",
    }.issubset(streams)
    assert streams["deal_flow"].source_defined_primary_key == [["id"]]
    assert streams["deal_flow"].default_cursor_field == ["log_time"]
    assert streams["permission_set_assignments"].source_defined_primary_key == [["permission_set_id"], ["user_id"]]
