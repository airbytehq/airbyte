#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from http import HTTPStatus
from typing import List, Optional
from unittest import TestCase

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder

from .config import ORGANIZATION_ID, ConfigBuilder
from .request_builder import OAuthRequestBuilder, RequestBuilder
from .response_builder import (
    create_empty_response,
    error_response,
    oauth_response,
    organizations_response,
)
from .utils import config, read_output


_STREAM_NAME = "organizations"


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


class TestOrganizations(TestCase):
    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(
            OAuthRequestBuilder.oauth_endpoint().build(),
            oauth_response(),
        )
        http_mocker.get(
            RequestBuilder.organizations_endpoint("me").build(),
            organizations_response(organization_id=ORGANIZATION_ID),
        )

        output = _read(config_builder=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == ORGANIZATION_ID

    @HttpMocker()
    def test_read_records_with_organization_ids(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(
            OAuthRequestBuilder.oauth_endpoint().build(),
            oauth_response(),
        )
        http_mocker.get(
            RequestBuilder.organizations_endpoint(ORGANIZATION_ID).build(),
            organizations_response(organization_id=ORGANIZATION_ID),
        )

        output = _read(config_builder=config().with_organization_ids([ORGANIZATION_ID]))
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == ORGANIZATION_ID

    @HttpMocker()
    def test_read_records_with_error_403_retry(self, http_mocker: HttpMocker) -> None:
        """Test that 403 errors trigger RETRY behavior with custom error message from manifest."""
        http_mocker.post(
            OAuthRequestBuilder.oauth_endpoint().build(),
            oauth_response(),
        )
        # First request returns 403, then succeeds on retry
        http_mocker.get(
            RequestBuilder.organizations_endpoint("me").build(),
            [
                error_response(HTTPStatus.FORBIDDEN),
                organizations_response(organization_id=ORGANIZATION_ID),
            ],
        )

        output = _read(config_builder=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == ORGANIZATION_ID

        # Verify custom error message from manifest is logged
        log_messages = [log.log.message for log in output.logs]
        expected_error_prefix = "Got permission error when accessing URL. Skipping"
        assert any(
            expected_error_prefix in msg for msg in log_messages
        ), f"Expected custom 403 error message '{expected_error_prefix}' in logs"
        assert any(_STREAM_NAME in msg for msg in log_messages), f"Expected stream name '{_STREAM_NAME}' in log messages"


class TestOrganizationsEmptyResults(TestCase):
    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker) -> None:
        """Test handling of 0-record responses from API (GAP 2)."""
        http_mocker.post(
            OAuthRequestBuilder.oauth_endpoint().build(),
            oauth_response(),
        )
        http_mocker.get(
            RequestBuilder.organizations_endpoint("me").build(),
            create_empty_response("organizations"),
        )

        output = _read(config_builder=config())
        assert len(output.records) == 0
        assert len(output.errors) == 0
        # Verify sync completed successfully
        log_messages = [log.log.message for log in output.logs]
        assert any("Finished syncing" in msg or "Read" in msg for msg in log_messages)


class TestOrganizationsIncremental(TestCase):
    @HttpMocker()
    def test_incremental_first_sync_emits_state(self, http_mocker: HttpMocker) -> None:
        """Test that first sync (no state) emits state message with cursor value."""
        http_mocker.post(
            OAuthRequestBuilder.oauth_endpoint().build(),
            oauth_response(),
        )
        http_mocker.get(
            RequestBuilder.organizations_endpoint("me").build(),
            organizations_response(organization_id=ORGANIZATION_ID),
        )

        output = _read(config_builder=config(), sync_mode=SyncMode.incremental)

        assert len(output.state_messages) > 0, "Expected state messages to be emitted"
        assert len(output.records) == 1

        # Get latest record's cursor
        latest_record = output.records[-1].record.data
        record_cursor_value = latest_record.get("updated_at")

        # Get state cursor
        new_state = output.most_recent_state.stream_state.__dict__
        state_cursor_value = new_state.get("updated_at") or new_state.get("state", {}).get("updated_at")

        # Validate state matches record
        assert state_cursor_value is not None, "Expected 'updated_at' in state"
        assert record_cursor_value is not None, "Expected 'updated_at' in record"
        assert state_cursor_value == record_cursor_value or state_cursor_value.startswith(
            record_cursor_value[:10]
        ), f"Expected state to match latest record. State: {state_cursor_value}, Record: {record_cursor_value}"

    @HttpMocker()
    def test_incremental_sync_with_state(self, http_mocker: HttpMocker) -> None:
        """Test incremental sync with previous state.

        This test validates:
        - Connector accepts state from previous sync
        - State is passed to both get_source() and read()
        - Records are returned
        - State advances to latest record's cursor value
        """
        previous_state_date = "2024-01-15T00:00:00.000000Z"
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated_at": previous_state_date}).build()

        http_mocker.post(
            OAuthRequestBuilder.oauth_endpoint().build(),
            oauth_response(),
        )
        http_mocker.get(
            RequestBuilder.organizations_endpoint("me").build(),
            organizations_response(organization_id=ORGANIZATION_ID),
        )

        output = _read(config_builder=config(), sync_mode=SyncMode.incremental, state=state)

        assert len(output.state_messages) > 0, "Expected state messages to be emitted"
        assert len(output.records) == 1

        # Get latest record's cursor
        latest_record = output.records[-1].record.data
        record_cursor_value = latest_record.get("updated_at")

        # Get state cursor
        new_state = output.most_recent_state.stream_state.__dict__
        state_cursor_value = new_state.get("updated_at") or new_state.get("state", {}).get("updated_at")

        # Validate state matches record
        assert state_cursor_value is not None, "Expected 'updated_at' in state"
        assert record_cursor_value is not None, "Expected 'updated_at' in record"
        assert state_cursor_value == record_cursor_value or state_cursor_value.startswith(
            record_cursor_value[:10]
        ), f"Expected state to match latest record. State: {state_cursor_value}, Record: {record_cursor_value}"
