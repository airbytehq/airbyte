# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from http import HTTPStatus
from typing import List, Optional
from unittest import TestCase

import freezegun

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder

from .config import ConfigBuilder
from .request_builder import RequestBuilder
from .response_builder import bounces_response, empty_response, error_response
from .utils import config, read_output


_STREAM_NAME = "bounces"


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
class TestBouncesStream(TestCase):
    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Basic read test for bounces stream"""
        http_mocker.get(
            RequestBuilder.bounces_endpoint().with_any_query_params().build(),
            bounces_response(),
        )

        output = _read(config_builder=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["email"] == "test@example.com"
        assert output.records[0].record.data["reason"] == "550 5.1.1 The email account does not exist"

    @HttpMocker()
    def test_read_empty_response(self, http_mocker: HttpMocker) -> None:
        """Test handling of empty response"""
        http_mocker.get(
            RequestBuilder.bounces_endpoint().with_any_query_params().build(),
            empty_response(),
        )

        output = _read(config_builder=config())
        assert len(output.records) == 0


@freezegun.freeze_time("2024-01-31T00:00:00Z")
class TestBouncesPagination(TestCase):
    @HttpMocker()
    def test_pagination_two_pages(self, http_mocker: HttpMocker) -> None:
        """Test pagination with 2 pages using offset-based pagination"""
        page1_records = [
            {"created": 1704067200, "email": f"bounce{i}@example.com", "reason": "Bounce", "status": "5.1.1"} for i in range(500)
        ]
        page2_records = [{"created": 1704067200, "email": "bounce500@example.com", "reason": "Bounce", "status": "5.1.1"}]

        http_mocker.get(
            RequestBuilder.bounces_endpoint().with_any_query_params().build(),
            [
                bounces_response(records=page1_records),
                bounces_response(records=page2_records),
            ],
        )

        output = _read(config_builder=config())
        assert len(output.records) == 501


@freezegun.freeze_time("2024-01-31T00:00:00Z")
class TestBouncesIncremental(TestCase):
    @HttpMocker()
    def test_incremental_first_sync_emits_state(self, http_mocker: HttpMocker) -> None:
        """Test that first sync (no state) emits state message"""
        http_mocker.get(
            RequestBuilder.bounces_endpoint().with_any_query_params().build(),
            bounces_response(),
        )

        output = _read(config_builder=config(), sync_mode=SyncMode.incremental)
        assert len(output.records) >= 1
        assert len(output.state_messages) >= 1

    @HttpMocker()
    def test_incremental_with_state(self, http_mocker: HttpMocker) -> None:
        """Test incremental sync with existing state"""
        http_mocker.get(
            RequestBuilder.bounces_endpoint().with_any_query_params().build(),
            bounces_response(),
        )

        state = StateBuilder().with_stream_state(_STREAM_NAME, {"created": 1704067200}).build()
        output = _read(config_builder=config(), sync_mode=SyncMode.incremental, state=state)
        assert len(output.state_messages) >= 1


@freezegun.freeze_time("2024-01-31T00:00:00Z")
class TestBouncesErrors(TestCase):
    @HttpMocker()
    def test_error_401_unauthorized(self, http_mocker: HttpMocker) -> None:
        """Test 401 error handling"""
        http_mocker.get(
            RequestBuilder.bounces_endpoint().with_any_query_params().build(),
            error_response(HTTPStatus.UNAUTHORIZED),
        )

        output = _read(config_builder=config(), expecting_exception=True)
        assert len(output.records) == 0

    @HttpMocker()
    def test_error_403_forbidden(self, http_mocker: HttpMocker) -> None:
        """Test 403 error handling"""
        http_mocker.get(
            RequestBuilder.bounces_endpoint().with_any_query_params().build(),
            error_response(HTTPStatus.FORBIDDEN),
        )

        output = _read(config_builder=config(), expecting_exception=True)
        assert len(output.records) == 0
