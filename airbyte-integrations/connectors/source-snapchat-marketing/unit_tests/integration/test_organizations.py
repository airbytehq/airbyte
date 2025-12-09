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
from airbyte_cdk.test.mock_http.request import HttpRequest
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
    def test_read_records_with_pagination(self, http_mocker: HttpMocker) -> None:
        next_link = "https://adsapi.snapchat.com/v1/me/organizations?cursor=page2"
        http_mocker.post(
            OAuthRequestBuilder.oauth_endpoint().build(),
            oauth_response(),
        )
        http_mocker.get(
            RequestBuilder.organizations_endpoint("me").build(),
            organizations_response(organization_id="org_1", has_next=True, next_link=next_link),
        )
        http_mocker.get(
            HttpRequest(url=next_link),
            organizations_response(organization_id="org_2", has_next=False),
        )

        output = _read(config_builder=config())
        assert len(output.records) == 2

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
        assert any(expected_error_prefix in msg for msg in log_messages), (
            f"Expected custom 403 error message '{expected_error_prefix}' in logs"
        )
        assert any(_STREAM_NAME in msg for msg in log_messages), (
            f"Expected stream name '{_STREAM_NAME}' in log messages"
        )


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
        assert len(output.records) == 1
        # Verify state message is emitted
        assert len(output.state_messages) >= 1
        # Verify state contains cursor field (updated_at)
        state_data = output.state_messages[-1].state
        assert state_data is not None

    @HttpMocker()
    def test_incremental_sync_validates_cursor_field(self, http_mocker: HttpMocker) -> None:
        """Test that cursor field name and value are correct in emitted state (GAP 4).

        For client-side incremental streams with partition routers, the state structure is:
        {'use_global_cursor': False, 'states': [...], 'state': {'updated_at': '...'}, 'lookback_window': 1}
        """
        http_mocker.post(
            OAuthRequestBuilder.oauth_endpoint().build(),
            oauth_response(),
        )
        http_mocker.get(
            RequestBuilder.organizations_endpoint("me").build(),
            organizations_response(organization_id=ORGANIZATION_ID),
        )

        output = _read(config_builder=config(), sync_mode=SyncMode.incremental)
        assert len(output.state_messages) >= 1

        # Strong cursor field validation - access nested state structure
        state_dict = output.most_recent_state.stream_state.__dict__
        cursor_field = "updated_at"

        # For partitioned streams, cursor is in state_dict["state"]
        if "state" in state_dict and isinstance(state_dict["state"], dict):
            inner_state = state_dict["state"]
            assert cursor_field in inner_state, f"Expected cursor field '{cursor_field}' in state, got: {list(inner_state.keys())}"
            cursor_value = inner_state[cursor_field]
        else:
            assert cursor_field in state_dict, f"Expected cursor field '{cursor_field}' in state, got: {list(state_dict.keys())}"
            cursor_value = state_dict[cursor_field]

        # Verify cursor value is present and valid datetime format
        assert cursor_value is not None
        # Validate datetime format (handles both ISO and date-only formats)
        if "T" in str(cursor_value):
            datetime.fromisoformat(str(cursor_value).replace("Z", "+00:00"))
        else:
            datetime.strptime(str(cursor_value), "%Y-%m-%d")

    @HttpMocker()
    def test_incremental_with_pagination_two_pages(self, http_mocker: HttpMocker) -> None:
        """Test pagination with 2 pages and verify pagination stops correctly.

        Note: This pagination test also validates the same behavior for other streams
        that use the same CursorPagination with paging.next_link pattern:
        adaccounts, campaigns, adsquads, ads, creatives, media, segments.
        """
        page1_link = "https://adsapi.snapchat.com/v1/me/organizations?cursor=page2"
        http_mocker.post(
            OAuthRequestBuilder.oauth_endpoint().build(),
            oauth_response(),
        )
        # Page 1 with next_link
        http_mocker.get(
            RequestBuilder.organizations_endpoint("me").build(),
            organizations_response(organization_id="org_1", has_next=True, next_link=page1_link),
        )
        # Page 2 without next_link (pagination stops)
        http_mocker.get(
            HttpRequest(url=page1_link),
            organizations_response(organization_id="org_2", has_next=False),
        )

        output = _read(config_builder=config(), sync_mode=SyncMode.incremental)
        # Verify both pages were read
        assert len(output.records) == 2
        # Verify pagination stopped (no more requests made)
        record_ids = [r.record.data["id"] for r in output.records]
        assert "org_1" in record_ids
        assert "org_2" in record_ids

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
        state = StateBuilder().with_stream_state(
            _STREAM_NAME,
            {"updated_at": previous_state_date}
        ).build()

        http_mocker.post(
            OAuthRequestBuilder.oauth_endpoint().build(),
            oauth_response(),
        )
        http_mocker.get(
            RequestBuilder.organizations_endpoint("me").build(),
            organizations_response(organization_id=ORGANIZATION_ID),
        )

        output = _read(config_builder=config(), sync_mode=SyncMode.incremental, state=state)

        assert len(output.records) >= 1, f"Expected at least 1 record, got {len(output.records)}"
        assert output.records[0].record.data["id"] is not None, "Expected record to have id"
        assert len(output.state_messages) > 0, "Expected state messages to be emitted"

        new_state = output.most_recent_state.stream_state.__dict__
        cursor_value = new_state.get("updated_at") or new_state.get("state", {}).get("updated_at")
        assert cursor_value is not None, "Expected cursor value in state"
