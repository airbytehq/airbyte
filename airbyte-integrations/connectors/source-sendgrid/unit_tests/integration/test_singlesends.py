# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from http import HTTPStatus
from typing import List, Optional
from unittest import TestCase

import freezegun

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.request import HttpRequest

from .config import ConfigBuilder
from .request_builder import API_BASE_URL, RequestBuilder
from .response_builder import error_response, singlesends_response
from .utils import config, read_output


_STREAM_NAME = "singlesends"


def _read(
    config_builder: ConfigBuilder,
    sync_mode: SyncMode = SyncMode.full_refresh,
    state: Optional[List[AirbyteStateMessage]] = None,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    return read_output(
        config_builder=config_builder,
        stream_name=_STREAM_NAME,
        sync_mode=sync_mode,
        state=state,
        expecting_exception=expecting_exception,
    )


@freezegun.freeze_time("2024-01-31T00:00:00Z")
class TestSinglesendsStream(TestCase):
    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Basic read test for singlesends stream"""
        http_mocker.get(
            RequestBuilder.singlesends_endpoint().with_any_query_params().build(),
            singlesends_response(),
        )

        output = _read(config_builder=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "550e8400-e29b-41d4-a716-446655440001"
        assert output.records[0].record.data["name"] == "Test Single Send"

    @HttpMocker()
    def test_read_empty_response(self, http_mocker: HttpMocker) -> None:
        """Test handling of empty response"""
        http_mocker.get(
            RequestBuilder.singlesends_endpoint().with_any_query_params().build(),
            singlesends_response(records=[]),
        )

        output = _read(config_builder=config())
        assert len(output.records) == 0


@freezegun.freeze_time("2024-01-31T00:00:00Z")
class TestSinglesendsPagination(TestCase):
    @HttpMocker()
    def test_pagination_two_pages(self, http_mocker: HttpMocker) -> None:
        """Test cursor-based pagination with 2 pages"""
        next_page_url = f"{API_BASE_URL}/v3/marketing/singlesends?page_token=next_page"
        page1_records = [
            {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "name": "Single Send 1",
                "status": "draft",
                "categories": [],
                "is_abtest": False,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T00:00:00Z",
                "send_at": None,
            }
        ]
        page2_records = [
            {
                "id": "550e8400-e29b-41d4-a716-446655440002",
                "name": "Single Send 2",
                "status": "sent",
                "categories": ["marketing"],
                "is_abtest": False,
                "created_at": "2024-01-02T00:00:00Z",
                "updated_at": "2024-01-16T00:00:00Z",
                "send_at": "2024-01-16T12:00:00Z",
            }
        ]

        http_mocker.get(
            RequestBuilder.singlesends_endpoint().with_any_query_params().build(),
            singlesends_response(records=page1_records, next_page_url=next_page_url),
        )
        http_mocker.get(
            HttpRequest(url=next_page_url),
            singlesends_response(records=page2_records, next_page_url=None),
        )

        output = _read(config_builder=config())
        assert len(output.records) == 2


@freezegun.freeze_time("2024-01-31T00:00:00Z")
class TestSinglesendsErrors(TestCase):
    @HttpMocker()
    def test_error_401_unauthorized(self, http_mocker: HttpMocker) -> None:
        """Test 401 error handling"""
        http_mocker.get(
            RequestBuilder.singlesends_endpoint().with_any_query_params().build(),
            error_response(HTTPStatus.UNAUTHORIZED),
        )

        output = _read(config_builder=config(), expecting_exception=True)
        assert len(output.records) == 0
