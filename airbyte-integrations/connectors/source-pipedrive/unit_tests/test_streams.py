# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from conftest import get_source


BASE_URL = "https://api.pipedrive.com/"
CONFIG = {"api_token": "tok", "replication_start_date": "2017-01-25 00:00:00Z"}


def _response(body, status_code=200):
    return HttpResponse(json.dumps(body), status_code)


def _read_stream(name, sync_mode=SyncMode.full_refresh):
    catalog = CatalogBuilder().with_stream(name, sync_mode).build()
    return read(get_source(CONFIG), CONFIG, catalog)


def _request(path, query_params):
    return HttpRequest(f"{BASE_URL}{path}", query_params=query_params)


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
                "api_token": "tok",
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
            _request("v1/callLogs", {"api_token": "tok", "limit": "50"}),
            _response(
                {
                    "data": [{"id": "call-1"}, {"id": "call-2"}],
                    "additional_data": {
                        "pagination": {"more_items_in_collection": True, "next_start": 50}
                    },
                }
            ),
        )
        http_mocker.get(
            _request("v1/callLogs", {"api_token": "tok", "limit": "50", "start": "50"}),
            _response(
                {
                    "data": [{"id": "call-3"}],
                    "additional_data": {"pagination": {"more_items_in_collection": False}},
                }
            ),
        )

        output = _read_stream("call_logs")

    assert [record.record.data["id"] for record in output.records] == ["call-1", "call-2", "call-3"]


def test_lead_sources():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("v1/leadSources", {"api_token": "tok"}),
            _response({"data": [{"name": "Website"}, {"name": "Import"}]}),
        )

        output = _read_stream("lead_sources")

    assert [record.record.data["name"] for record in output.records] == ["Website", "Import"]


def test_legacy_teams_reads_records():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("v1/legacyTeams", {"api_token": "tok"}),
            _response({"data": [{"id": 1, "name": "Sales"}]}),
        )

        output = _read_stream("legacy_teams")

    assert [record.record.data["id"] for record in output.records] == [1]


def test_legacy_teams_ignores_gone_endpoint():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("v1/legacyTeams", {"api_token": "tok"}),
            _response({"success": False}, status_code=410),
        )

        output = _read_stream("legacy_teams")

    assert output.records == []
    assert output.errors == []


def test_projects_paginates_active_and_archived_projects():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("api/v2/projects", {"api_token": "tok", "limit": "100"}),
            _response(
                {
                    "data": [{"id": 1}],
                    "additional_data": {"next_cursor": "abc"},
                }
            ),
        )
        http_mocker.get(
            _request("api/v2/projects", {"api_token": "tok", "limit": "100", "cursor": "abc"}),
            _response({"data": [{"id": 2}], "additional_data": {"next_cursor": None}}),
        )
        http_mocker.get(
            _request("api/v2/projects/archived", {"api_token": "tok", "limit": "100"}),
            _response({"data": [{"id": 3}], "additional_data": {"next_cursor": None}}),
        )

        output = _read_stream("projects")

    assert [record.record.data["id"] for record in output.records] == [1, 2, 3]


def test_projects_ignores_forbidden_endpoints():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("api/v2/projects", {"api_token": "tok", "limit": "100"}),
            _response({"success": False}, status_code=403),
        )
        http_mocker.get(
            _request("api/v2/projects/archived", {"api_token": "tok", "limit": "100"}),
            _response({"success": False}, status_code=403),
        )

        output = _read_stream("projects")

    assert output.records == []
    assert output.errors == []


def test_tasks_paginates():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("api/v2/tasks", {"api_token": "tok", "limit": "100"}),
            _response({"data": [{"id": 1}], "additional_data": {"next_cursor": "abc"}}),
        )
        http_mocker.get(
            _request("api/v2/tasks", {"api_token": "tok", "limit": "100", "cursor": "abc"}),
            _response({"data": [{"id": 2}], "additional_data": {"next_cursor": None}}),
        )

        output = _read_stream("tasks")

    assert [record.record.data["id"] for record in output.records] == [1, 2]


def test_deal_installments_reads_each_deal_partition():
    with HttpMocker() as http_mocker:
        _mock_deals(http_mocker)
        http_mocker.get(
            _request(
                "api/v2/deals/installments",
                {"api_token": "tok", "deal_ids": "1", "limit": "100"},
            ),
            _response({"data": [{"id": 11, "deal_id": 1}], "additional_data": {"next_cursor": None}}),
        )
        http_mocker.get(
            _request(
                "api/v2/deals/installments",
                {"api_token": "tok", "deal_ids": "2", "limit": "100"},
            ),
            _response({"data": [{"id": 22, "deal_id": 2}], "additional_data": {"next_cursor": None}}),
        )

        output = _read_stream("deal_installments")

    assert [record.record.data["deal_id"] for record in output.records] == [1, 2]


def test_deal_flow_flattens_and_filters_records():
    with HttpMocker() as http_mocker:
        _mock_deals(http_mocker)
        flow_response = {
            "data": [
                {
                    "object": "dealChange",
                    "timestamp": "2024-03-01T10:00:00Z",
                    "data": {
                        "id": 101,
                        "item_id": 1,
                        "field_key": "value",
                        "log_time": "2016-01-01 00:00:00",
                    },
                },
                {
                    "object": "dealChange",
                    "timestamp": "2024-03-02T10:00:00Z",
                    "data": {
                        "id": 102,
                        "item_id": 1,
                        "field_key": "value",
                        "log_time": "2024-03-01 10:00:00",
                    },
                }
            ],
            "additional_data": {"pagination": {"more_items_in_collection": False}},
        }
        flow_request_params = {
            "api_token": "tok",
            "limit": "50",
            "items": "dealChange",
            "all_changes": "1",
        }
        http_mocker.get(_request("v1/deals/1/flow", flow_request_params), _response(flow_response))
        http_mocker.get(
            _request("v1/deals/2/flow", flow_request_params),
            _response({"data": [], "additional_data": {"pagination": {"more_items_in_collection": False}}}),
        )

        output = _read_stream("deal_flow", SyncMode.incremental)

    assert [record.record.data["id"] for record in output.records] == [102]
    assert "object" not in output.records[0].record.data
    assert output.state_messages


def test_permission_set_assignments_reads_each_permission_set():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("v1/permissionSets", {"api_token": "tok", "limit": "50"}),
            _response({"data": [{"id": "ps-1", "name": "Admin"}]}),
        )
        http_mocker.get(
            _request(
                "v1/permissionSets/ps-1/assignments",
                {"api_token": "tok", "limit": "50"},
            ),
            _response(
                {
                    "data": [
                        {"permission_set_id": "ps-1", "user_id": 1, "name": "Alice"},
                        {"permission_set_id": "ps-1", "user_id": 2, "name": "Bob"},
                    ],
                    "additional_data": {"pagination": {"more_items_in_collection": False}},
                }
            ),
        )

        output = _read_stream("permission_set_assignments")

    assert [record.record.data["user_id"] for record in output.records] == [1, 2]


def test_permission_set_assignments_ignores_forbidden_endpoint():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("v1/permissionSets", {"api_token": "tok", "limit": "50"}),
            _response({"data": [{"id": "ps-1", "name": "Admin"}]}),
        )
        http_mocker.get(
            _request(
                "v1/permissionSets/ps-1/assignments",
                {"api_token": "tok", "limit": "50"},
            ),
            _response({"success": False}, status_code=403),
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
    assert streams["permission_set_assignments"].source_defined_primary_key == [["permission_set_id"], ["user_id"]]
