# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `application_history` stream on `source-ashby`.

`POST /application.listHistory` is called once per application from an
`application.list` parent. In incremental mode the parent is read with its
`updatedAt` state, so a later sync only requests history for applications
updated at most 1 day before the saved cursor.
"""

import json
from typing import Any, Dict, List
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from mock_server.config import ConfigBuilder
from mock_server.request_builder import AshbyRequestBuilder


_STREAM_NAME = "application_history"
_CREATED_AFTER_MS = 1704067200000  # timestamp("2024-01-01T00:00:00Z") * 1000


def _application_record(application_id: str, updated_at: str) -> Dict[str, Any]:
    return {
        "id": application_id,
        "status": "Active",
        "createdAt": "2024-02-01T00:00:00.000Z",
        "updatedAt": updated_at,
    }


def _history_record(record_id: str, entered_stage_at: str) -> Dict[str, Any]:
    """A history entry, shaped like the success example in Ashby's `application.listHistory` reference."""
    return {
        "id": record_id,
        "stageId": "stage-1",
        "title": "Application Review",
        "enteredStageAt": entered_stage_at,
        "leftStageAt": None,
        "stageNumber": 0,
        "allowedActions": ["delete", "set_entered_at"],
        "actorId": None,
    }


def _page(records: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"success": True, "results": records, "moreDataAvailable": False}), status_code=200)


def _applications_request() -> HttpRequest:
    return (
        AshbyRequestBuilder.endpoint("/application.list")
        .with_api_key("test-api-key")
        .with_body_field("createdAfter", _CREATED_AFTER_MS)
        .with_limit(100)
        .build()
    )


def _history_request(application_id: str) -> HttpRequest:
    return (
        AshbyRequestBuilder.endpoint("/application.listHistory")
        .with_api_key("test-api-key")
        .with_body_field("applicationId", application_id)
        .with_limit(100)
        .build()
    )


def _read(sync_mode: SyncMode, state: List[AirbyteStateMessage] = None) -> EntrypointOutput:
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()
    return read(get_source(config=config, state=state), config=config, catalog=catalog, state=state or [])


def _history_state(output: EntrypointOutput) -> Dict[str, Any]:
    """The last emitted state without `lookback_window`, which is the sync's duration in seconds."""
    state = dict(output.most_recent_state.stream_state.__dict__)
    state.pop("lookback_window")
    return state


def _expected_history_state(updated_at: str) -> Dict[str, Any]:
    return {
        "use_global_cursor": True,
        "state": {"application_updated_at": updated_at},
        "parent_state": {"applications_for_history": {"updatedAt": updated_at}},
    }


class TestApplicationHistory(TestCase):
    def test_full_refresh_reads_history_for_every_application(self):
        with HttpMocker() as http_mocker:
            http_mocker.post(
                _applications_request(),
                _page(
                    [
                        _application_record("app-1", "2024-03-01T00:00:00.000Z"),
                        _application_record("app-2", "2024-04-01T00:00:00.000Z"),
                    ]
                ),
            )
            http_mocker.post(_history_request("app-1"), _page([_history_record("h-1", "2024-03-01T00:00:00.000Z")]))
            http_mocker.post(_history_request("app-2"), _page([_history_record("h-2", "2024-04-01T00:00:00.000Z")]))

            output = _read(SyncMode.full_refresh)

        assert output.errors == []
        assert {(r.record.data["id"], r.record.data["application_updated_at"]) for r in output.records} == {
            ("h-1", "2024-03-01T00:00:00.000Z"),
            ("h-2", "2024-04-01T00:00:00.000Z"),
        }

    def test_incremental_sync_only_requests_history_for_applications_updated_since_last_sync(self):
        with HttpMocker() as http_mocker:
            http_mocker.post(
                _applications_request(),
                _page(
                    [
                        _application_record("app-1", "2024-03-01T00:00:00.000Z"),
                        _application_record("app-2", "2024-04-01T00:00:00.000Z"),
                    ]
                ),
            )
            http_mocker.post(_history_request("app-1"), _page([_history_record("h-1", "2024-03-01T00:00:00.000Z")]))
            http_mocker.post(_history_request("app-2"), _page([_history_record("h-2", "2024-04-01T00:00:00.000Z")]))

            first_sync = _read(SyncMode.incremental)

        assert first_sync.errors == []
        assert {r.record.data["id"] for r in first_sync.records} == {"h-1", "h-2"}
        assert _history_state(first_sync) == _expected_history_state("2024-04-01T00:00:00.000000Z")
        saved_state = first_sync.state_messages[-1].state

        # app-1 is unchanged, app-2 moved to a new stage, app-3 is new. Any
        # request for app-1's history raises NoMockAddress.
        with HttpMocker() as http_mocker:
            http_mocker.post(
                _applications_request(),
                _page(
                    [
                        _application_record("app-1", "2024-03-01T00:00:00.000Z"),
                        _application_record("app-2", "2024-05-01T00:00:00.000Z"),
                        _application_record("app-3", "2024-05-02T00:00:00.000Z"),
                    ]
                ),
            )
            app2_history = _history_request("app-2")
            app3_history = _history_request("app-3")
            http_mocker.post(
                app2_history,
                _page(
                    [
                        _history_record("h-2", "2024-04-01T00:00:00.000Z"),
                        _history_record("h-3", "2024-05-01T00:00:00.000Z"),
                    ]
                ),
            )
            http_mocker.post(app3_history, _page([_history_record("h-4", "2024-05-02T00:00:00.000Z")]))

            second_sync = _read(SyncMode.incremental, state=[saved_state])

            http_mocker.assert_number_of_calls(app2_history, 1)
            http_mocker.assert_number_of_calls(app3_history, 1)

        assert second_sync.errors == []
        assert {r.record.data["id"] for r in second_sync.records} == {"h-2", "h-3", "h-4"}
        assert _history_state(second_sync) == _expected_history_state("2024-05-02T00:00:00.000000Z")

    def test_incremental_sync_requests_history_for_application_updated_during_previous_sync(self):
        with HttpMocker() as http_mocker:
            http_mocker.post(
                _applications_request(),
                _page(
                    [
                        _application_record("app-0", "2024-05-01T00:00:00.000Z"),
                        _application_record("app-1", "2024-03-01T00:00:00.000Z"),
                        _application_record("app-2", "2024-06-01T00:10:00.000Z"),
                    ]
                ),
            )
            http_mocker.post(_history_request("app-0"), _page([_history_record("h-0", "2024-05-01T00:00:00.000Z")]))
            http_mocker.post(_history_request("app-1"), _page([_history_record("h-1", "2024-03-01T00:00:00.000Z")]))
            http_mocker.post(_history_request("app-2"), _page([_history_record("h-2", "2024-06-01T00:10:00.000Z")]))

            first_sync = _read(SyncMode.incremental)

        assert first_sync.errors == []
        saved_state = first_sync.state_messages[-1].state

        # app-1 was hired at 00:05, after its page was read but before the sync saw
        # app-2's 00:10, so its updatedAt is below the saved cursor. app-0 is more
        # than 1 day older than the cursor, and any request for its history raises
        # NoMockAddress.
        with HttpMocker() as http_mocker:
            http_mocker.post(
                _applications_request(),
                _page(
                    [
                        _application_record("app-0", "2024-05-01T00:00:00.000Z"),
                        _application_record("app-1", "2024-06-01T00:05:00.000Z"),
                        _application_record("app-2", "2024-06-01T00:10:00.000Z"),
                    ]
                ),
            )
            app1_history = _history_request("app-1")
            http_mocker.post(
                app1_history,
                _page(
                    [
                        _history_record("h-1", "2024-03-01T00:00:00.000Z"),
                        _history_record("h-1-hired", "2024-06-01T00:05:00.000Z"),
                    ]
                ),
            )
            http_mocker.post(_history_request("app-2"), _page([_history_record("h-2", "2024-06-01T00:10:00.000Z")]))

            second_sync = _read(SyncMode.incremental, state=[saved_state])

            http_mocker.assert_number_of_calls(app1_history, 1)

        assert second_sync.errors == []
        assert "h-1-hired" in {r.record.data["id"] for r in second_sync.records}
