# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `applications` stream on `source-ashby`.

`application.list` ignores `updatedAfter` and is ordered by `createdAt`, so an
incremental sync pages the full list and keeps applications updated at most
1 day before the saved cursor.
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


_STREAM_NAME = "applications"
_CREATED_AFTER_MS = 1704067200000  # timestamp("2024-01-01T00:00:00Z") * 1000


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


def _read(sync_mode: SyncMode, state: List[AirbyteStateMessage] = None) -> EntrypointOutput:
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()
    return read(get_source(config=config, state=state), config=config, catalog=catalog, state=state or [])


class TestApplications(TestCase):
    def test_incremental_sync_emits_applications_updated_within_lookback_of_saved_cursor(self):
        with HttpMocker() as http_mocker:
            http_mocker.post(
                _applications_request(),
                _page(
                    [
                        {"id": "app-0", "updatedAt": "2024-03-01T00:00:00.000Z"},
                        {"id": "app-1", "updatedAt": "2024-03-01T00:00:00.000Z"},
                        {"id": "app-2", "updatedAt": "2024-04-01T00:10:00.000Z"},
                    ]
                ),
            )
            first_sync = _read(SyncMode.incremental)

        assert first_sync.errors == []
        assert {r.record.data["id"] for r in first_sync.records} == {"app-0", "app-1", "app-2"}
        assert first_sync.most_recent_state.stream_state.__dict__ == {"updatedAt": "2024-04-01T00:10:00.000000Z"}

        # app-0 is more than 1 day older than the cursor and dropped. app-1 was
        # updated at 00:05, during the previous sync, and is still emitted.
        with HttpMocker() as http_mocker:
            http_mocker.post(
                _applications_request(),
                _page(
                    [
                        {"id": "app-0", "updatedAt": "2024-03-01T00:00:00.000Z"},
                        {"id": "app-1", "updatedAt": "2024-04-01T00:05:00.000Z"},
                        {"id": "app-2", "updatedAt": "2024-04-01T00:10:00.000Z"},
                        # No milliseconds: only the manifest's second cursor format parses this.
                        {"id": "app-3", "updatedAt": "2024-05-02T00:00:00Z"},
                    ]
                ),
            )
            second_sync = _read(SyncMode.incremental, state=[first_sync.state_messages[-1].state])

        assert second_sync.errors == []
        assert {r.record.data["id"] for r in second_sync.records} == {"app-1", "app-2", "app-3"}
        assert second_sync.most_recent_state.stream_state.__dict__ == {"updatedAt": "2024-05-02T00:00:00.000000Z"}

    def test_full_refresh_emits_applications_without_updated_at(self):
        with HttpMocker() as http_mocker:
            http_mocker.post(_applications_request(), _page([{"id": "app-1", "updatedAt": None}, {"id": "app-2"}]))

            output = _read(SyncMode.full_refresh)

        assert output.errors == []
        assert {r.record.data["id"] for r in output.records} == {"app-1", "app-2"}
