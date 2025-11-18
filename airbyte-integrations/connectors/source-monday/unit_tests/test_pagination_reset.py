# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import pytest
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from source_declarative_manifest import SourceDeclarativeManifest


def test_pagination_reset_on_cursor_expired_error():
    """Test that pagination resets when CursorExpiredError is encountered."""
    
    config = {
        "credentials": {
            "auth_type": "api_token",
            "api_token": "test_token"
        },
        "num_workers": 1
    }
    
    catalog = CatalogBuilder().with_stream("items", sync_mode="full_refresh").build()
    
    source = SourceDeclarativeManifest()
    
    with HttpMocker() as http_mocker:
        http_mocker.post(
            HttpRequest(url="https://api.monday.com/v2"),
            HttpResponse(
                body={
                    "error_code": "CursorException",
                    "error_message": "CursorExpiredError: The cursor provided for pagination has expired. Please refresh your query and obtain a new cursor to continue fetching items",
                    "status_code": 200,
                    "extensions": {
                        "request_id": "test-request-id-1"
                    }
                },
                status_code=200
            )
        )
        
        http_mocker.post(
            HttpRequest(url="https://api.monday.com/v2"),
            HttpResponse(
                body={
                    "data": {
                        "boards": [
                            {
                                "items_page": {
                                    "cursor": None,
                                    "items": [
                                        {
                                            "id": "item1",
                                            "name": "Test Item 1",
                                            "updated_at": "2025-11-18T00:00:00Z"
                                        },
                                        {
                                            "id": "item2",
                                            "name": "Test Item 2",
                                            "updated_at": "2025-11-18T00:00:00Z"
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                },
                status_code=200
            )
        )
        
        output = read(source, config, catalog)
        
        records = [message.record for message in output if message.record]
        
        assert len(records) == 2
        assert records[0].data["id"] == "item1"
        assert records[1].data["id"] == "item2"


def test_other_cursor_exceptions_still_fail():
    """Test that other CursorException errors (not CursorExpiredError) still fail."""
    
    config = {
        "credentials": {
            "auth_type": "api_token",
            "api_token": "test_token"
        },
        "num_workers": 1
    }
    
    catalog = CatalogBuilder().with_stream("items", sync_mode="full_refresh").build()
    source = SourceDeclarativeManifest()
    
    with HttpMocker() as http_mocker:
        http_mocker.post(
            HttpRequest(url="https://api.monday.com/v2"),
            HttpResponse(
                body={
                    "error_code": "CursorException",
                    "error_message": "SomeOtherCursorError: A different cursor error occurred",
                    "status_code": 200,
                    "extensions": {
                        "request_id": "test-request-id-2"
                    }
                },
                status_code=200
            )
        )
        
        with pytest.raises(Exception) as exc_info:
            output = list(read(source, config, catalog))
        
        assert "CursorException" in str(exc_info.value) or "SomeOtherCursorError" in str(exc_info.value)
