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
from .response_builder import empty_response, error_response, suppression_groups_response
from .utils import config, read_output


_STREAM_NAME = "suppression_groups"


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
class TestSuppressionGroupsStream(TestCase):
    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Basic read test for suppression_groups stream"""
        http_mocker.get(
            RequestBuilder.suppression_groups_endpoint().with_any_query_params().build(),
            suppression_groups_response(),
        )

        output = _read(config_builder=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 123
        assert output.records[0].record.data["name"] == "Test Group"

    @HttpMocker()
    def test_read_empty_response(self, http_mocker: HttpMocker) -> None:
        """Test handling of empty response"""
        http_mocker.get(
            RequestBuilder.suppression_groups_endpoint().with_any_query_params().build(),
            empty_response(),
        )

        output = _read(config_builder=config())
        assert len(output.records) == 0

    @HttpMocker()
    def test_read_multiple_records(self, http_mocker: HttpMocker) -> None:
        """Test reading multiple suppression groups"""
        records = [
            {"id": 1, "name": "Group 1", "description": "First group", "is_default": False, "unsubscribes": 5},
            {"id": 2, "name": "Group 2", "description": "Second group", "is_default": True, "unsubscribes": 10},
        ]
        http_mocker.get(
            RequestBuilder.suppression_groups_endpoint().with_any_query_params().build(),
            suppression_groups_response(records=records),
        )

        output = _read(config_builder=config())
        assert len(output.records) == 2


@freezegun.freeze_time("2024-01-31T00:00:00Z")
class TestSuppressionGroupsErrors(TestCase):
    @HttpMocker()
    def test_error_401_unauthorized(self, http_mocker: HttpMocker) -> None:
        """Test 401 error handling"""
        http_mocker.get(
            RequestBuilder.suppression_groups_endpoint().with_any_query_params().build(),
            error_response(HTTPStatus.UNAUTHORIZED),
        )

        output = _read(config_builder=config(), expecting_exception=True)
        assert len(output.records) == 0
