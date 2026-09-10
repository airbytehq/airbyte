# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


BASE_URL = "https://api.pipedrive.com/"
CONFIG = {"api_token": "tok", "replication_start_date": "2017-01-25 00:00:00Z"}
V1_PAGE_DONE = {"pagination": {"start": 0, "limit": 500, "more_items_in_collection": False}}


def _response(body, status_code=200):
    return HttpResponse(json.dumps(body), status_code)


def _read_stream(name, sync_mode=SyncMode.full_refresh, state=None):
    catalog = CatalogBuilder().with_stream(name, sync_mode).build()
    return read(get_source(CONFIG, state), CONFIG, catalog, state=state)


def _request(path, query_params):
    return HttpRequest(f"{BASE_URL}{path}", query_params=query_params)


def _ids(output, field="id"):
    return sorted(record.record.data[field] for record in output.records)


def _deals_response():
    return {
        "success": True,
        "data": [
            {"id": 1, "update_time": "2024-01-01T00:00:00Z"},
            {"id": 2, "update_time": "2024-01-02T00:00:00Z"},
        ],
        "additional_data": {"next_cursor": None},
    }


_DEALS_QUERY = {
    "api_token": "tok",
    "limit": "500",
    "sort_by": "update_time",
    "sort_direction": "asc",
    "status": "open,won,lost,deleted",
    "updated_since": "2017-01-25T00:00:00Z",
}


def _mock_deals(http_mocker, archived=None):
    """The deal child streams expand both parents: `deals` and `deals_archived`."""
    http_mocker.get(_request("api/v2/deals", _DEALS_QUERY), _response(_deals_response()))
    http_mocker.get(
        _request("api/v2/deals/archived", _DEALS_QUERY),
        _response({"success": True, "data": archived or [], "additional_data": {"next_cursor": None}}),
    )


def test_call_logs_paginates():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("v1/callLogs", {"api_token": "tok", "limit": "50"}),
            _response(
                {
                    "data": [{"id": "call-1"}, {"id": "call-2"}],
                    "additional_data": {"pagination": {"more_items_in_collection": True, "next_start": 50}},
                }
            ),
        )
        http_mocker.get(
            _request("v1/callLogs", {"api_token": "tok", "limit": "50", "start": "50"}),
            _response({"data": [{"id": "call-3"}], "additional_data": {"pagination": {"more_items_in_collection": False}}}),
        )

        output = _read_stream("call_logs")

    assert _ids(output) == ["call-1", "call-2", "call-3"]


def test_call_logs_response_without_additional_data_is_a_single_page():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("v1/callLogs", {"api_token": "tok", "limit": "50"}),
            _response({"success": True, "data": [{"id": "call-1"}]}),
        )

        output = _read_stream("call_logs")

    assert _ids(output) == ["call-1"]
    assert output.errors == []


def test_lead_sources():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("v1/leadSources", {"api_token": "tok"}),
            _response({"data": [{"name": "Website"}, {"name": "Import"}], "additional_data": None}),
        )

        output = _read_stream("lead_sources")

    assert _ids(output, "name") == ["Import", "Website"]


def test_legacy_teams_reads_records():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("v1/legacyTeams", {"api_token": "tok"}),
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
        http_mocker.get(_request("v1/legacyTeams", {"api_token": "tok"}), _response(body, status_code=status_code))

        output = _read_stream("legacy_teams")

    assert output.records == []
    assert output.errors == []


def test_projects_paginates_active_and_archived_projects():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("api/v2/projects", {"api_token": "tok", "limit": "500"}),
            _response({"data": [{"id": 1}], "additional_data": {"next_cursor": "abc"}}),
        )
        http_mocker.get(
            _request("api/v2/projects", {"api_token": "tok", "limit": "500", "cursor": "abc"}),
            _response({"data": [{"id": 2}], "additional_data": {"next_cursor": None}}),
        )
        http_mocker.get(
            _request("api/v2/projects/archived", {"api_token": "tok", "limit": "500"}),
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
        http_mocker.get(_request("api/v2/projects", {"api_token": "tok", "limit": "500"}), _response(body, status_code=status_code))
        http_mocker.get(
            _request("api/v2/projects/archived", {"api_token": "tok", "limit": "500"}), _response(body, status_code=status_code)
        )

        output = _read_stream("projects")

    assert output.records == []
    assert output.errors == []


def test_tasks_paginates():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("api/v2/tasks", {"api_token": "tok", "limit": "500"}),
            _response({"data": [{"id": 1}], "additional_data": {"next_cursor": "abc"}}),
        )
        http_mocker.get(
            _request("api/v2/tasks", {"api_token": "tok", "limit": "500", "cursor": "abc"}),
            _response({"data": [{"id": 2}]}),
        )

        output = _read_stream("tasks")

    assert _ids(output) == [1, 2]
    assert output.errors == []


def test_tasks_ignores_missing_projects_suite():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("api/v2/tasks", {"api_token": "tok", "limit": "500"}),
            _response({"success": False, "error": "Required suites missing", "errorCode": 402}, status_code=402),
        )

        output = _read_stream("tasks")

    assert output.records == []
    assert output.errors == []


def test_deal_installments_batches_parent_deals_into_one_request():
    with HttpMocker() as http_mocker:
        _mock_deals(http_mocker)
        http_mocker.get(
            _request("api/v2/deals/installments", {"api_token": "tok", "deal_ids": "1,2", "limit": "500"}),
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
            _request("api/v2/deals/installments", {"api_token": "tok", "deal_ids": "1,2", "limit": "500"}),
            _response({"success": False, "error": "The company does not have access to this feature"}, status_code=403),
        )

        output = _read_stream("deal_installments")

    assert output.records == []
    assert output.errors == []


def _flow_request(deal_id, start=None):
    params = {"api_token": "tok", "limit": "500", "items": "dealChange", "all_changes": "1"}
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
        _request("v1/permissionSets", {"api_token": "tok", "limit": "50"}),
        _response({"data": [{"id": "ps-1", "name": "Admin"}]}),
    )


def test_permission_set_assignments_reads_each_permission_set():
    with HttpMocker() as http_mocker:
        _mock_permission_sets(http_mocker)
        http_mocker.get(
            _request("v1/permissionSets/ps-1/assignments", {"api_token": "tok", "limit": "500"}),
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
            _request("v1/permissionSets/ps-1/assignments", {"api_token": "tok", "limit": "500"}),
            _response({"success": False, "error": "forbidden"}, status_code=403),
        )

        output = _read_stream("permission_set_assignments")

    assert output.records == []
    assert output.errors == []


def test_discover_lists_new_streams():
    catalog = get_source(CONFIG).discover(logging.getLogger(__name__), CONFIG)
    streams = {stream.name: stream for stream in catalog.streams}

    assert len(streams) == 35
    assert streams["deals_archived"].source_defined_primary_key == [["id"]]
    assert streams["deals_archived"].default_cursor_field == ["update_time"]
    assert streams["leads"].default_cursor_field == ["update_time"]
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


def test_deals_v2_cursor_pagination_and_deleted_records():
    with HttpMocker() as http_mocker:
        first = {
            "data": [
                {"id": 1, "update_time": "2024-01-01T00:00:00Z"},
                {"id": 2, "update_time": "2024-01-02T00:00:00Z", "is_deleted": True, "status": "deleted"},
            ],
            "additional_data": {"next_cursor": "abc"},
        }
        http_mocker.get(
            _request(
                "api/v2/deals",
                {
                    "api_token": "tok",
                    "limit": "500",
                    "sort_by": "update_time",
                    "sort_direction": "asc",
                    "status": "open,won,lost,deleted",
                    "updated_since": "2017-01-25T00:00:00Z",
                },
            ),
            _response(first),
        )
        http_mocker.get(
            _request(
                "api/v2/deals",
                {
                    "api_token": "tok",
                    "limit": "500",
                    "sort_by": "update_time",
                    "sort_direction": "asc",
                    "status": "open,won,lost,deleted",
                    "updated_since": "2017-01-25T00:00:00Z",
                    "cursor": "abc",
                },
            ),
            _response(
                {
                    "data": [{"id": 3, "update_time": "2024-01-03T00:00:00Z"}],
                    "additional_data": {"next_cursor": None},
                }
            ),
        )

        output = _read_stream("deals", SyncMode.incremental)

    assert _ids(output) == [1, 2, 3]
    assert output.records[1].record.data["is_deleted"] is True
    assert output.most_recent_state.stream_state.__dict__ == {"update_time": "2024-01-03T00:00:00Z"}


def test_deals_updated_since_is_inclusive():
    state = StateBuilder().with_stream_state("deals", {"update_time": "2023-02-22T08:27:54Z"}).build()
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request(
                "api/v2/deals",
                {
                    "api_token": "tok",
                    "limit": "500",
                    "sort_by": "update_time",
                    "sort_direction": "asc",
                    "status": "open,won,lost,deleted",
                    "updated_since": "2023-02-22T08:27:54Z",
                },
            ),
            _response({"data": [{"id": 1, "update_time": "2023-02-22T08:27:54Z"}], "additional_data": {"next_cursor": None}}),
        )

        output = _read_stream("deals", SyncMode.incremental, state)

    assert _ids(output) == [1]


def test_deals_legacy_state_is_normalized_to_rfc3339():
    state = StateBuilder().with_stream_state("deals", {"update_time": "2021-06-01 10:10:10"}).build()
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request(
                "api/v2/deals",
                {
                    "api_token": "tok",
                    "limit": "500",
                    "sort_by": "update_time",
                    "sort_direction": "asc",
                    "status": "open,won,lost,deleted",
                    "updated_since": "2021-06-01T10:10:10Z",
                },
            ),
            _response({"data": [{"id": 1, "update_time": "2021-06-01T10:10:10Z"}], "additional_data": {"next_cursor": None}}),
        )

        output = _read_stream("deals", SyncMode.incremental, state)

    assert _ids(output) == [1]


def test_files_filter_records_client_side():
    state = StateBuilder().with_stream_state("files", {"update_time": "2024-01-01 00:00:00"}).build()
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("v1/files", {"api_token": "tok", "limit": "100", "sort": "update_time ASC"}),
            _response(
                {
                    "data": [
                        {"id": 1, "update_time": "2023-12-31 23:59:59"},
                        {"id": 2, "update_time": "2024-01-01 00:00:00"},
                        {"id": 3, "update_time": "2024-01-01 00:00:01"},
                    ],
                    "additional_data": {"pagination": {"more_items_in_collection": False}},
                }
            ),
        )

        output = _read_stream("files", SyncMode.incremental, state)

    assert _ids(output) == [2, 3]


def test_notes_filter_server_side_with_updated_since_and_emit_rfc3339_state():
    # `GET /v1/notes` accepts an inclusive RFC3339 `updated_since`; the legacy state format is still accepted.
    state = StateBuilder().with_stream_state("notes", {"update_time": "2024-01-01 00:00:00"}).build()
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request(
                "v1/notes",
                {"api_token": "tok", "limit": "500", "sort": "update_time ASC", "updated_since": "2024-01-01T00:00:00Z"},
            ),
            _response(
                {
                    "data": [
                        {"id": 2, "update_time": "2024-01-01 00:00:00"},
                        {"id": 3, "update_time": "2024-01-05 10:00:00"},
                    ],
                    "additional_data": {"pagination": {"more_items_in_collection": False}},
                }
            ),
        )

        output = _read_stream("notes", SyncMode.incremental, state)

    assert _ids(output) == [2, 3]
    assert output.most_recent_state.stream_state.__dict__ == {"update_time": "2024-01-05T10:00:00Z"}


def test_leads_filter_server_side_with_updated_since():
    # `GET /v1/leads` accepts `updated_since` and sorts on `update_time`; values carry fractional seconds.
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request(
                "v1/leads",
                {"api_token": "tok", "limit": "50", "sort": "update_time ASC", "updated_since": "2017-01-25T00:00:00Z"},
            ),
            _response(
                {
                    "data": [
                        {"id": "lead-1", "update_time": "2023-02-22T11:48:49.834Z"},
                        {"id": "lead-2", "update_time": "2023-02-22T11:49:24.853Z"},
                    ],
                    "additional_data": {"pagination": {"more_items_in_collection": False}},
                }
            ),
        )

        output = _read_stream("leads", SyncMode.incremental)

    assert _ids(output) == ["lead-1", "lead-2"]
    assert output.most_recent_state.stream_state.__dict__ == {"update_time": "2023-02-22T11:49:24Z"}


def test_deals_archived_reads_the_archived_collection():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("api/v2/deals/archived", _DEALS_QUERY),
            _response(
                {
                    "data": [{"id": 9, "update_time": "2024-02-01T00:00:00Z", "is_archived": True}],
                    "additional_data": {"next_cursor": None},
                }
            ),
        )

        output = _read_stream("deals_archived", SyncMode.incremental)

    assert _ids(output) == [9]
    assert output.records[0].record.data["is_archived"] is True
    assert output.most_recent_state.stream_state.__dict__ == {"update_time": "2024-02-01T00:00:00Z"}


def test_deal_products_expands_archived_deals_too():
    with HttpMocker() as http_mocker:
        _mock_deals(http_mocker, archived=[{"id": 9, "update_time": "2024-02-01T00:00:00Z", "is_archived": True}])
        for deal_id, products in ((1, [{"id": 10, "deal_id": 1}]), (2, []), (9, [{"id": 90, "deal_id": 9}])):
            http_mocker.get(
                _request(f"api/v2/deals/{deal_id}/products", {"api_token": "tok", "limit": "500"}),
                _response({"data": products, "additional_data": {"next_cursor": None}}),
            )

        output = _read_stream("deal_products")

    assert sorted(_ids(output)) == [10, 90]
    assert output.errors == []


def test_persons_page_without_additional_data_is_a_single_page():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request(
                "api/v2/persons",
                {
                    "api_token": "tok",
                    "limit": "500",
                    "sort_by": "update_time",
                    "sort_direction": "asc",
                    "updated_since": "2017-01-25T00:00:00Z",
                },
            ),
            _response({"success": True, "data": [{"id": 1, "update_time": "2024-01-01T00:00:00Z"}]}),
        )

        output = _read_stream("persons", SyncMode.incremental)

    assert _ids(output) == [1]
    assert output.errors == []


def test_no_stream_uses_the_recents_endpoint():
    from conftest import _YAML_FILE_PATH

    assert "v1/recents" not in _YAML_FILE_PATH.read_text()


@pytest.mark.parametrize(
    "stream, path, query",
    [
        ("pipelines", "api/v2/pipelines", {"api_token": "tok", "limit": "500"}),
        ("stages", "api/v2/stages", {"api_token": "tok", "limit": "500"}),
        ("filters", "v1/filters", {"api_token": "tok"}),
        ("users", "v1/users", {"api_token": "tok"}),
    ],
)
def test_full_refresh_streams_use_list_endpoints(stream, path, query):
    with HttpMocker() as http_mocker:
        http_mocker.get(_request(path, query), _response({"data": [{"id": 1}]}))

        output = _read_stream(stream)

    assert _ids(output) == [1]


@pytest.mark.parametrize(
    "stream, expected",
    [
        ("deal_fields", [["key"]]),
        ("activity_fields", [["key"]]),
        ("organization_fields", [["key"]]),
        ("person_fields", [["key"]]),
        ("product_fields", [["key"]]),
        ("lead_labels", [["id"]]),
        ("leads", [["id"]]),
        ("activity_types", [["id"]]),
        ("currencies", [["id"]]),
        ("permission_sets", [["id"]]),
        ("roles", [["id"]]),
        ("deal_products", [["id"]]),
    ],
)
def test_migrated_primary_keys(stream, expected):
    catalog = get_source(CONFIG).discover(logging.getLogger(__name__), CONFIG)
    discovered = {item.name: item for item in catalog.streams}

    assert discovered[stream].source_defined_primary_key == expected


def test_deal_products_uses_v2_nested_endpoint():
    with HttpMocker() as http_mocker:
        _mock_deals(http_mocker)
        http_mocker.get(
            _request("api/v2/deals/1/products", {"api_token": "tok", "limit": "500"}),
            _response({"data": [{"id": 10, "deal_id": 1}], "additional_data": {"next_cursor": None}}),
        )
        http_mocker.get(
            _request("api/v2/deals/2/products", {"api_token": "tok", "limit": "500"}),
            _response({"data": [], "additional_data": {"next_cursor": None}}),
        )

        output = _read_stream("deal_products")

    assert _ids(output) == [10]
    assert output.errors == []
