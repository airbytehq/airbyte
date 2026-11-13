# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from airbyte_cdk.models import Level, SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse

from .config import ConfigBuilder
from .monday_requests import ActivityLogsRequestBuilder
from .monday_requests.request_authenticators import ApiTokenAuthenticator
from .utils import get_log_messages_by_log_level, read_stream


_API_TOKEN = "api-token"
_GRAPHQL_ERRORS = [{"message": "Internal server error", "path": ["boards", 0, "activity_logs", 1]}]


def _activity_log(log_id: str, entity: str, data) -> dict:
    return {
        "id": log_id,
        "event": "update_column_value",
        "data": data,
        "entity": entity,
        "created_at": "17626752000000000",
        "user_id": "42",
    }


class TestActivityLogsStream(TestCase):
    @HttpMocker()
    def test_null_activity_log_entries_are_skipped_with_graphql_errors_logged(self, http_mocker: HttpMocker) -> None:
        config = ConfigBuilder().with_api_token_credentials(_API_TOKEN).build()
        authenticator = ApiTokenAuthenticator(api_token=_API_TOKEN)
        body = {
            "data": {
                "boards": [
                    {
                        "activity_logs": [
                            _activity_log("log-1", "pulse", json.dumps({"pulse_id": 111, "board_id": 222})),
                            None,
                            _activity_log("log-3", "board", None),
                            _activity_log("log-4", "board", json.dumps({"board_id": 222})),
                        ]
                    }
                ]
            },
            "errors": _GRAPHQL_ERRORS,
        }
        http_mocker.post(
            ActivityLogsRequestBuilder.activity_logs_endpoint(authenticator).build(),
            HttpResponse(json.dumps(body), 200),
        )
        http_mocker.post(
            ActivityLogsRequestBuilder.activity_logs_endpoint(authenticator).with_page(page=2, sub_page=1).build(),
            HttpResponse(json.dumps({"data": {"boards": []}}), 200),
        )

        output = read_stream("activity_logs", SyncMode.full_refresh, config)

        assert [(r.record.data["id"], r.record.data.get("pulse_id"), r.record.data.get("board_id")) for r in output.records] == [
            ("log-1", 111, None),
            ("log-3", None, None),
            ("log-4", None, 222),
        ]
        assert all(r.record.data["created_at_int"] == 1762675200 for r in output.records)
        assert not output.errors
        warnings = list(get_log_messages_by_log_level(output.logs, Level.WARN))
        assert f"Skipped 1 null entries in a board's activity_logs list; GraphQL errors: {_GRAPHQL_ERRORS}" in warnings
