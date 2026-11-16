# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any
from unittest import TestCase
from urllib.parse import urlencode

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest
from airbyte_cdk.test.state_builder import StateBuilder

from .request_builder import BASE_URL, START_CURSOR
from .response_builder import error_response, page_response
from .utils import given_token, read_stream, record_ids, stream_state


_STREAM = "audit_logs"
_PATH = "/auditLogs"


def _query(since: str) -> dict[str, str]:
    # `/auditLogs` rejects `sort=updatedAt` with 400; the stream sorts and filters on `timestamp` instead.
    return {
        "count": "false",
        "sort": "timestamp",
        "page[size]": "1000",
        "newFilterSyntax": "true",
        "filter[timestamp][gte]": since,
    }


def _request(since: str = START_CURSOR) -> HttpRequest:
    return HttpRequest(f"{BASE_URL}{_PATH}", query_params=_query(since))


def _audit_log(log_id: str, timestamp: str) -> dict[str, Any]:
    return {
        "type": "auditLog",
        "id": log_id,
        "attributes": {
            "action": "update",
            "additionalInfo": [{"field": "resource_id", "value": "1"}],
            "agent": {
                "callerServiceId": None,
                "email": "admin@example.com",
                "impersonatedBy": None,
                "ipAddress": "192.0.2.1",
                "userId": "1",
            },
            "changes": [{"field": "last_name", "preValue": "Byron", "postValue": "Lovelace"}],
            "eventName": "user_updated",
            "globalId": log_id,
            "orgId": "2706687d-dc8d-406a-9162-3962faa4b665",
            "requestId": "20369948-2b6b-424a-affa-ef9aab106ff9",
            "result": "completed",
            "timestamp": timestamp,
        },
        "links": {"self": f"{BASE_URL}{_PATH}/{log_id}"},
    }


_LOG_1 = "edabeba1-3d82-439a-9f77-c1f69bf23c03"
_LOG_2 = "5c1d0b5e-8f0a-4c4e-9a59-2f8b6f2b9d11"
_LOG_3 = "9a7e3c2d-1b4f-4e6a-8c5d-3f2e1d0c9b8a"


class TestAuditLogsStream(TestCase):
    @HttpMocker()
    def test_full_refresh_keeps_the_uuid_id_and_nested_objects(self, http_mocker: HttpMocker) -> None:
        given_token(http_mocker)
        http_mocker.get(_request(), page_response([_audit_log(_LOG_1, "2026-09-17T20:40:11Z")]))

        output = read_stream(_STREAM, SyncMode.full_refresh)

        assert not output.errors
        assert [record.record.data for record in output.records] == [
            {
                "id": _LOG_1,
                "action": "update",
                "additionalInfo": [{"field": "resource_id", "value": "1"}],
                "agent": {
                    "callerServiceId": None,
                    "email": "admin@example.com",
                    "impersonatedBy": None,
                    "ipAddress": "192.0.2.1",
                    "userId": "1",
                },
                "changes": [{"field": "last_name", "preValue": "Byron", "postValue": "Lovelace"}],
                "eventName": "user_updated",
                "globalId": _LOG_1,
                "orgId": "2706687d-dc8d-406a-9162-3962faa4b665",
                "requestId": "20369948-2b6b-424a-affa-ef9aab106ff9",
                "result": "completed",
                "timestamp": "2026-09-17T20:40:11Z",
            }
        ]

    @HttpMocker()
    def test_pagination_follows_links_next_until_it_is_absent(self, http_mocker: HttpMocker) -> None:
        given_token(http_mocker)
        next_url = f"{BASE_URL}{_PATH}?{urlencode({**_query(START_CURSOR), 'page[after]': 'W3siYnkiOiJ0aW1lc3RhbXAifV0='})}"
        http_mocker.get(_request(), page_response([_audit_log(_LOG_1, "2026-09-17T20:40:11Z")], next_url=next_url))
        http_mocker.get(HttpRequest(next_url), page_response([_audit_log(_LOG_2, "2026-09-17T20:45:53Z")]))

        output = read_stream(_STREAM, SyncMode.full_refresh)

        assert not output.errors
        assert record_ids(output) == [_LOG_1, _LOG_2]

    @HttpMocker()
    def test_incremental_first_sync_starts_at_start_date_and_emits_state(self, http_mocker: HttpMocker) -> None:
        given_token(http_mocker)
        http_mocker.get(
            _request(),
            page_response([_audit_log(_LOG_1, "2026-09-17T20:40:11Z"), _audit_log(_LOG_2, "2026-09-17T20:45:53Z")]),
        )

        output = read_stream(_STREAM, SyncMode.incremental)

        assert not output.errors
        assert record_ids(output) == [_LOG_1, _LOG_2]
        assert stream_state(output) == {"timestamp": "2026-09-17T20:45:53.000Z"}

    @HttpMocker()
    def test_incremental_with_state_requests_from_the_saved_cursor(self, http_mocker: HttpMocker) -> None:
        state = StateBuilder().with_stream_state(_STREAM, {"timestamp": "2026-09-17T20:45:53.000Z"}).build()
        given_token(http_mocker)
        http_mocker.get(
            _request("2026-09-17T20:45:53.000Z"),
            page_response([_audit_log(_LOG_2, "2026-09-17T20:45:53Z"), _audit_log(_LOG_3, "2026-11-11T20:07:52Z")]),
        )

        output = read_stream(_STREAM, SyncMode.incremental, state=state)

        assert not output.errors
        # The filter includes the cursor value, so the last record of the previous sync is read again.
        assert record_ids(output) == [_LOG_2, _LOG_3]
        assert stream_state(output) == {"timestamp": "2026-11-11T20:07:52.000Z"}

    @HttpMocker()
    def test_403_without_admin_scope_fails_as_config_error(self, http_mocker: HttpMocker) -> None:
        given_token(http_mocker)
        http_mocker.get(
            _request(),
            error_response(403, "unauthorizedOauthScope", "Unauthorized OAuth Scope", "Your token lacks the auditLogs.read scope."),
        )

        output = read_stream(_STREAM, SyncMode.full_refresh, expecting_exception=True)

        assert output.records == []
        assert output.errors[-1].trace.error.failure_type == FailureType.config_error
        assert "Your token lacks the auditLogs.read scope." in output.errors[-1].trace.error.message
        assert len(http_mocker._mocker.request_history) == 2
