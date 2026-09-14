#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Tests for the `flows` stream (HubSpot Automation v4 Flows API).

The stream lists flow summaries from `GET /automation/v4/flows` and enriches each record with the
full workflow definition from `GET /automation/v4/flows/{flowId}`.
"""

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.state_builder import StateBuilder

from .conftest import find_stream, get_source, read_from_stream


FLOWS_LIST_URL = "https://api.hubapi.com/automation/v4/flows"
SCHEMAS_URL = "https://api.hubapi.com/crm/v3/schemas"


def _listing(flow_id: str, updated_at: str = "2023-05-01T10:00:00.000Z") -> dict:
    """A summary record as returned by the list endpoint (HubSpot `ApiFlowListing`)."""
    return {
        "id": flow_id,
        "name": f"Flow {flow_id}",
        "flowType": "WORKFLOW",
        "isEnabled": True,
        "objectTypeId": "0-1",
        "revisionId": "3",
        "createdAt": "2023-01-01T00:00:00.000Z",
        "updatedAt": updated_at,
        "uuid": f"uuid-{flow_id}",
    }


def _details(flow_id: str, updated_at: str = "2023-05-01T10:00:00.000Z") -> dict:
    """A full definition as returned by the detail endpoint (HubSpot `ApiContactFlow`)."""
    return {
        **_listing(flow_id, updated_at),
        "type": "CONTACT_FLOW",
        "startActionId": "1",
        "nextAvailableActionId": "4",
        "actions": [
            {"actionId": "1", "type": "SINGLE_CONNECTION", "actionTypeId": "0-1", "connection": {"nextActionId": "2"}},
            {
                "actionId": "2",
                "type": "STATIC_BRANCH",
                "branches": [{"branchName": "Yes", "connection": {"nextActionId": "3"}}],
            },
        ],
        "enrollmentCriteria": {
            "type": "LIST_BASED",
            "listFilterBranch": {"filterBranchType": "OR", "filters": [{"property": "email", "operation": {"operator": "IS_KNOWN"}}]},
        },
        "dataSources": [{"type": "STATIC_PROPERTY", "propertyName": "email"}],
        "timeWindows": [],
        "blockedDates": [],
        "customProperties": {},
        "crmObjectCreationStatus": "COMPLETE",
        "suppressionListIds": [42],
        "canEnrollFromSalesforce": False,
    }


@pytest.fixture
def mock_schemas(requests_mock):
    """The source resolves custom-object dynamic streams before any stream is read."""
    requests_mock.get(SCHEMAS_URL, json={}, status_code=200)


def test_flows_stream_is_gated_behind_enable_experimental_streams(config, config_experimental, mock_schemas):
    default_streams = {stream.name for stream in get_source(config).streams(config=config)}
    experimental_streams = {stream.name for stream in get_source(config_experimental).streams(config=config_experimental)}

    assert "flows" not in default_streams
    assert "flows" in experimental_streams

    # The legacy v3 stream is unaffected by the new stream in both configurations.
    assert "workflows" in default_streams
    assert "workflows" in experimental_streams


def test_read_enriches_each_listing_with_the_full_definition(config_experimental, mock_schemas, requests_mock):
    requests_mock.get(FLOWS_LIST_URL, json={"results": [_listing("111")]}, status_code=200)
    details_mock = requests_mock.get(f"{FLOWS_LIST_URL}/111", json=_details("111"), status_code=200)

    output = read_from_stream(config_experimental, "flows", SyncMode.full_refresh)

    assert details_mock.call_count == 1
    assert len(output.records) == 1

    record = output.records[0].record.data
    # Summary fields survive the merge...
    assert record["id"] == "111"
    assert record["name"] == "Flow 111"
    # ...and the detail-only fields are present.
    assert record["startActionId"] == "1"
    assert [action["actionId"] for action in record["actions"]] == ["1", "2"]
    assert record["enrollmentCriteria"]["type"] == "LIST_BASED"
    assert record["dataSources"] == [{"type": "STATIC_PROPERTY", "propertyName": "email"}]
    assert record["suppressionListIds"] == [42]


def test_read_follows_the_paging_next_after_cursor(config_experimental, mock_schemas, requests_mock):
    requests_mock.get(
        FLOWS_LIST_URL,
        [
            {
                "json": {"results": [_listing("111")], "paging": {"next": {"after": "cursor-2"}}},
                "status_code": 200,
            },
            {"json": {"results": [_listing("222")]}, "status_code": 200},
        ],
    )
    requests_mock.get(f"{FLOWS_LIST_URL}/111", json=_details("111"), status_code=200)
    requests_mock.get(f"{FLOWS_LIST_URL}/222", json=_details("222"), status_code=200)

    output = read_from_stream(config_experimental, "flows", SyncMode.full_refresh)

    assert [record.record.data["id"] for record in output.records] == ["111", "222"]

    list_requests = [request for request in requests_mock.request_history if request.path == "/automation/v4/flows"]
    assert len(list_requests) == 2
    assert "after" not in list_requests[0].qs
    assert list_requests[1].qs["after"] == ["cursor-2"]
    # Page size is requested explicitly so the page count is predictable.
    assert list_requests[0].qs["limit"] == ["100"]


def test_detail_request_failure_degrades_to_the_summary_record(config_experimental, mock_schemas, requests_mock, caplog):
    """A flow needing sensitive-data scopes must not fail the whole stream."""
    requests_mock.get(FLOWS_LIST_URL, json={"results": [_listing("111"), _listing("222")]}, status_code=200)
    requests_mock.get(
        f"{FLOWS_LIST_URL}/111",
        json={"status": "error", "message": "This app hasn't been granted all required scopes"},
        status_code=403,
    )
    requests_mock.get(f"{FLOWS_LIST_URL}/222", json=_details("222"), status_code=200)

    output = read_from_stream(config_experimental, "flows", SyncMode.full_refresh)

    assert len(output.records) == 2
    degraded, complete = (record.record.data for record in output.records)

    # The inaccessible flow still yields its summary fields, without the detail-only fields.
    assert degraded["id"] == "111"
    assert degraded["name"] == "Flow 111"
    assert "actions" not in degraded
    # The readable flow is unaffected.
    assert complete["id"] == "222"
    assert complete["enrollmentCriteria"]["type"] == "LIST_BASED"

    assert "Failed to fetch the full definition for flow 111" in caplog.text


def test_detail_request_is_retried_on_rate_limit(config_experimental, mock_schemas, requests_mock):
    requests_mock.get(FLOWS_LIST_URL, json={"results": [_listing("111")]}, status_code=200)
    rate_limited = requests_mock.get(f"{FLOWS_LIST_URL}/111", json={"message": "rate limited"}, status_code=429)

    read_from_stream(config_experimental, "flows", SyncMode.full_refresh)

    # 5 default retries plus the initial call, matching the shared HubSpot error handler.
    assert rate_limited.call_count == 6


def test_incremental_filters_unchanged_flows_before_paying_for_details(config_experimental, mock_schemas, requests_mock):
    """Client-side filtering runs ahead of the enrichment, so unchanged flows cost no detail request."""
    requests_mock.get(
        FLOWS_LIST_URL,
        json={
            "results": [
                _listing("111", updated_at="2023-01-01T00:00:00.000Z"),  # older than state -> filtered out
                _listing("222", updated_at="2023-09-01T00:00:00.000Z"),  # newer than state -> synced
            ]
        },
        status_code=200,
    )
    stale_details = requests_mock.get(f"{FLOWS_LIST_URL}/111", json=_details("111"), status_code=200)
    fresh_details = requests_mock.get(f"{FLOWS_LIST_URL}/222", json=_details("222", updated_at="2023-09-01T00:00:00.000Z"), status_code=200)

    state = StateBuilder().with_stream_state("flows", {"updatedAt": "2023-06-01T00:00:00.000Z"}).build()
    output = read_from_stream(config_experimental, "flows", SyncMode.incremental, state=state)

    assert [record.record.data["id"] for record in output.records] == ["222"]
    assert fresh_details.call_count == 1
    assert stale_details.call_count == 0


def test_stream_metadata_matches_the_v4_contract(config_experimental, mock_schemas):
    stream = find_stream("flows", config_experimental)
    airbyte_stream = stream.as_airbyte_stream()

    assert airbyte_stream.source_defined_primary_key == [["id"]]
    assert airbyte_stream.default_cursor_field == ["updatedAt"]
    assert SyncMode.incremental in airbyte_stream.supported_sync_modes

    schema = stream.get_json_schema()["properties"]
    # v4 identifies flows with a string id, unlike the integer id of the legacy `workflows` stream.
    assert schema["id"]["type"] == ["null", "string"]
    assert schema["actions"]["type"] == ["null", "array"]
    assert schema["enrollmentCriteria"]["type"] == ["null", "object"]
