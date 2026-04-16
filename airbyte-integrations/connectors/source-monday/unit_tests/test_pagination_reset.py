# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse

from .integrations.config import ConfigBuilder
from .integrations.monday_requests import ItemsRequestBuilder
from .integrations.monday_requests.request_authenticators import ApiTokenAuthenticator
from .integrations.utils import read_stream


@pytest.mark.skip(
    reason="Pagination reset functionality is tested in the CDK. This test is skipped due to concurrent execution making unpredictable HTTP requests."
)
def test_pagination_reset_on_cursor_expired_error():
    """Test that pagination resets when CursorExpiredError is encountered."""
    config = ConfigBuilder().with_api_token_credentials("test_token").build()
    config["num_workers"] = 2
    api_token_authenticator = ApiTokenAuthenticator(api_token=config["credentials"]["api_token"])

    with HttpMocker() as http_mocker:
        call_count = {"n": 0}

        def response_callback(request, context):
            context.status_code = 200
            context.headers["Content-Type"] = "application/json"
            call_count["n"] += 1

            if call_count["n"] == 1:
                return json.dumps(
                    {
                        "error_code": "CursorException",
                        "error_message": "CursorExpiredError: The cursor provided for pagination has expired. Please refresh your query and obtain a new cursor to continue fetching items",
                        "status_code": 200,
                        "extensions": {"request_id": "test-request-id-1"},
                    }
                ).encode("utf-8")
            else:
                return json.dumps(
                    {
                        "data": {
                            "boards": [
                                {
                                    "items_page": {
                                        "cursor": None,
                                        "items": [
                                            {
                                                "id": "item1",
                                                "name": "Test Item 1",
                                                "updated_at": "2025-11-18T00:00:00Z",
                                                "created_at": "2025-11-18T00:00:00Z",
                                                "creator_id": "123",
                                                "state": "active",
                                                "board": {"id": "1", "name": "Test Board"},
                                                "group": {"id": "group1"},
                                                "column_values": [],
                                                "assets": [],
                                                "subscribers": [],
                                                "updates": [],
                                            },
                                            {
                                                "id": "item2",
                                                "name": "Test Item 2",
                                                "updated_at": "2025-11-18T00:00:00Z",
                                                "created_at": "2025-11-18T00:00:00Z",
                                                "creator_id": "123",
                                                "state": "active",
                                                "board": {"id": "1", "name": "Test Board"},
                                                "group": {"id": "group1"},
                                                "column_values": [],
                                                "assets": [],
                                                "subscribers": [],
                                                "updates": [],
                                            },
                                        ],
                                    }
                                }
                            ]
                        }
                    }
                ).encode("utf-8")

        http_mocker.post(
            ItemsRequestBuilder.items_endpoint(api_token_authenticator).build(),
            HttpResponse(body=response_callback),
        )

        output = read_stream("items", SyncMode.full_refresh, config)

        assert len(output.records) == 2
        assert output.records[0].data["id"] == "item1"
        assert output.records[1].data["id"] == "item2"


@pytest.mark.skip(
    reason="Pagination reset functionality is tested in the CDK. This test is skipped due to concurrent execution making unpredictable HTTP requests."
)
def test_other_cursor_exceptions_still_fail():
    """Test that other CursorException errors (not CursorExpiredError) still fail."""
    config = ConfigBuilder().with_api_token_credentials("test_token").build()
    config["num_workers"] = 2
    api_token_authenticator = ApiTokenAuthenticator(api_token=config["credentials"]["api_token"])

    with HttpMocker() as http_mocker:

        def error_callback(request, context):
            context.status_code = 200
            context.headers["Content-Type"] = "application/json"
            return json.dumps(
                {
                    "error_code": "CursorException",
                    "error_message": "SomeOtherCursorError: A different cursor error occurred",
                    "status_code": 200,
                    "extensions": {"request_id": "test-request-id-2"},
                }
            ).encode("utf-8")

        http_mocker.post(
            ItemsRequestBuilder.items_endpoint(api_token_authenticator).build(),
            HttpResponse(body=error_callback),
        )

        output = read_stream("items", SyncMode.full_refresh, config)

        assert len(output.errors) > 0
        error_messages = [str(e).lower() for e in output.errors]
        assert any("cursorexception" in msg or "someothercursorerror" in msg for msg in error_messages)
