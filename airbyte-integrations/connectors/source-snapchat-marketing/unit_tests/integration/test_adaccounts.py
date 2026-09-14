#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from typing import List, Optional
from unittest import TestCase

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.request import HttpRequest
from airbyte_cdk.test.state_builder import StateBuilder

from .config import AD_ACCOUNT_ID, ORGANIZATION_ID, ConfigBuilder
from .request_builder import OAuthRequestBuilder, RequestBuilder
from .response_builder import (
    adaccounts_response,
    error_response,
    oauth_response,
    organizations_response,
    organizations_response_multiple,
)
from .utils import config, read_output


_STREAM_NAME = "adaccounts"


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


class TestAdaccounts(TestCase):
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
        http_mocker.get(
            RequestBuilder.adaccounts_endpoint(ORGANIZATION_ID).build(),
            adaccounts_response(ad_account_id=AD_ACCOUNT_ID, organization_id=ORGANIZATION_ID),
        )

        output = _read(config_builder=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == AD_ACCOUNT_ID

    @HttpMocker()
    def test_read_records_with_pagination(self, http_mocker: HttpMocker) -> None:
        """Test pagination for adaccounts stream.

        NOTE: This test covers pagination for ALL streams in this connector
        because they all use the same DefaultPaginator with identical
        CursorPagination strategy (cursor_value from response.paging.next_link,
        stop_condition when next_link is empty). Writing separate pagination
        tests for each stream would be redundant.
        """
        next_link = "https://adsapi.snapchat.com/v1/organizations/test_org_123/adaccounts?cursor=page2"
        http_mocker.post(
            OAuthRequestBuilder.oauth_endpoint().build(),
            oauth_response(),
        )
        http_mocker.get(
            RequestBuilder.organizations_endpoint("me").build(),
            organizations_response(organization_id=ORGANIZATION_ID),
        )
        http_mocker.get(
            RequestBuilder.adaccounts_endpoint(ORGANIZATION_ID).build(),
            adaccounts_response(ad_account_id="adaccount_1", has_next=True, next_link=next_link),
        )
        http_mocker.get(
            HttpRequest(url=next_link),
            adaccounts_response(ad_account_id="adaccount_2", has_next=False),
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
        http_mocker.get(
            RequestBuilder.organizations_endpoint("me").build(),
            organizations_response(organization_id=ORGANIZATION_ID),
        )
        # First request returns 403, then succeeds on retry
        http_mocker.get(
            RequestBuilder.adaccounts_endpoint(ORGANIZATION_ID).build(),
            [
                error_response(HTTPStatus.FORBIDDEN),
                adaccounts_response(ad_account_id=AD_ACCOUNT_ID, organization_id=ORGANIZATION_ID),
            ],
        )

        output = _read(config_builder=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == AD_ACCOUNT_ID

        # Verify custom error message from manifest is logged
        log_messages = [log.log.message for log in output.logs]
        expected_error_prefix = "Got permission error when accessing URL. Skipping"
        assert any(
            expected_error_prefix in msg for msg in log_messages
        ), f"Expected custom 403 error message '{expected_error_prefix}' in logs"
        assert any(_STREAM_NAME in msg for msg in log_messages), f"Expected stream name '{_STREAM_NAME}' in log messages"


class TestAdaccountsSubstreamMultipleParents(TestCase):
    @HttpMocker()
    def test_substream_with_two_parent_records(self, http_mocker: HttpMocker) -> None:
        """Test that substream correctly processes multiple parent records.

        The adaccounts stream uses SubstreamPartitionRouter with organizations as parent.
        This test verifies that adaccounts are fetched for each parent organization.
        """
        org_1 = "org_001"
        org_2 = "org_002"

        http_mocker.post(
            OAuthRequestBuilder.oauth_endpoint().build(),
            oauth_response(),
        )
        http_mocker.get(
            RequestBuilder.organizations_endpoint("me").build(),
            organizations_response_multiple([org_1, org_2]),
        )
        # Mock adaccounts endpoint for each parent organization
        http_mocker.get(
            RequestBuilder.adaccounts_endpoint(org_1).build(),
            adaccounts_response(ad_account_id="adaccount_from_org_1", organization_id=org_1),
        )
        http_mocker.get(
            RequestBuilder.adaccounts_endpoint(org_2).build(),
            adaccounts_response(ad_account_id="adaccount_from_org_2", organization_id=org_2),
        )

        output = _read(config_builder=config())

        # Verify records from both parent organizations are returned
        assert len(output.records) == 2
        record_ids = [r.record.data.get("id") for r in output.records]
        assert "adaccount_from_org_1" in record_ids
        assert "adaccount_from_org_2" in record_ids


class TestAdaccountsIncremental(TestCase):
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
        http_mocker.get(
            RequestBuilder.adaccounts_endpoint(ORGANIZATION_ID).build(),
            adaccounts_response(ad_account_id=AD_ACCOUNT_ID, organization_id=ORGANIZATION_ID),
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
        http_mocker.get(
            RequestBuilder.adaccounts_endpoint(ORGANIZATION_ID).build(),
            adaccounts_response(ad_account_id=AD_ACCOUNT_ID, organization_id=ORGANIZATION_ID),
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
