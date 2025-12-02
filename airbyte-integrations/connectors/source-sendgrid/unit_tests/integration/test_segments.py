# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from http import HTTPStatus
from typing import List, Optional
from unittest import TestCase

import freezegun

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker

from .config import ConfigBuilder
from .request_builder import RequestBuilder
from .response_builder import error_response, segments_response
from .utils import config, read_output


_STREAM_NAME = "segments"


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
class TestSegmentsStream(TestCase):
    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Basic read test for segments stream"""
        http_mocker.get(
            RequestBuilder.segments_endpoint().with_any_query_params().build(),
            segments_response(),
        )

        output = _read(config_builder=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "segment-id-123"
        assert output.records[0].record.data["name"] == "Test Segment"

    @HttpMocker()
    def test_read_empty_response(self, http_mocker: HttpMocker) -> None:
        """Test handling of empty response"""
        http_mocker.get(
            RequestBuilder.segments_endpoint().with_any_query_params().build(),
            segments_response(records=[]),
        )

        output = _read(config_builder=config())
        assert len(output.records) == 0

    @HttpMocker()
    def test_read_multiple_records(self, http_mocker: HttpMocker) -> None:
        """Test reading multiple segments"""
        records = [
            {
                "id": "segment-1",
                "name": "Segment 1",
                "contacts_count": 100,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T00:00:00Z",
                "sample_updated_at": None,
                "next_sample_update": None,
                "parent_list_ids": [],
                "query_version": "2.0",
                "status": {"query_validation": "valid"},
            },
            {
                "id": "segment-2",
                "name": "Segment 2",
                "contacts_count": 200,
                "created_at": "2024-01-02T00:00:00Z",
                "updated_at": "2024-01-16T00:00:00Z",
                "sample_updated_at": None,
                "next_sample_update": None,
                "parent_list_ids": ["list-1"],
                "query_version": "2.0",
                "status": {"query_validation": "valid"},
            },
        ]
        http_mocker.get(
            RequestBuilder.segments_endpoint().with_any_query_params().build(),
            segments_response(records=records),
        )

        output = _read(config_builder=config())
        assert len(output.records) == 2


@freezegun.freeze_time("2024-01-31T00:00:00Z")
class TestSegmentsErrors(TestCase):
    @HttpMocker()
    def test_error_401_unauthorized(self, http_mocker: HttpMocker) -> None:
        """Test 401 error handling"""
        http_mocker.get(
            RequestBuilder.segments_endpoint().with_any_query_params().build(),
            error_response(HTTPStatus.UNAUTHORIZED),
        )

        output = _read(config_builder=config(), expecting_exception=True)
        assert len(output.records) == 0
