#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder

from .config import BUSINESS_ACCOUNT_ID, PAGE_ID, ConfigBuilder
from .request_builder import RequestBuilder, get_account_request
from .response_builder import SECOND_BUSINESS_ACCOUNT_ID, SECOND_PAGE_ID, get_account_response, get_multiple_accounts_response
from .utils import read_output


_STREAM_NAME = "user_insights"

_FROZEN_TIME = "2024-01-15T12:00:00Z"


def _get_user_insights_request_any_params(business_account_id: str) -> RequestBuilder:
    """Create a request builder for user_insights with any query params.

    The user_insights stream uses DatetimeBasedCursor with step P1D and QueryProperties
    with 4 chunks (day/follower_count,reach; week/reach; days_28/reach; lifetime/online_followers).
    This creates multiple time slices and query property combinations.
    Using with_any_query_params() allows matching all these requests when the exact
    parameters are not predictable or when testing behavior that doesn't depend on
    specific request parameters.
    """
    return RequestBuilder.get_user_lifetime_insights_endpoint(item_id=business_account_id).with_any_query_params()


def _get_user_insights_request_with_params(business_account_id: str, since: str, until: str, period: str, metric: str) -> RequestBuilder:
    """Create a request builder for user_insights with specific query params."""
    return (
        RequestBuilder.get_user_lifetime_insights_endpoint(item_id=business_account_id)
        .with_custom_param("since", since)
        .with_custom_param("until", until)
        .with_custom_param("period", period)
        .with_custom_param("metric", metric)
    )


def _build_user_insights_response() -> HttpResponse:
    """Build a successful user_insights response inline."""
    body = {
        "data": [
            {
                "name": "follower_count",
                "period": "day",
                "values": [{"value": 1000, "end_time": "2024-01-15T07:00:00+0000"}],
                "title": "Follower Count",
                "description": "Total number of followers",
                "id": f"{BUSINESS_ACCOUNT_ID}/insights/follower_count/day",
            },
            {
                "name": "reach",
                "period": "day",
                "values": [{"value": 500, "end_time": "2024-01-15T07:00:00+0000"}],
                "title": "Reach",
                "description": "Total reach",
                "id": f"{BUSINESS_ACCOUNT_ID}/insights/reach/day",
            },
        ]
    }
    return HttpResponse(json.dumps(body), 200)


def _build_error_response(code: int, message: str, error_subcode: int = None) -> HttpResponse:
    """Build an error response inline.

    Args:
        code: The error code (e.g., 100, 10)
        message: The error message
        error_subcode: Optional error subcode (e.g., 2108006, 33)
    """
    error = {
        "message": message,
        "type": "OAuthException",
        "code": code,
        "fbtrace_id": "ABC123",
    }
    if error_subcode is not None:
        error["error_subcode"] = error_subcode
    return HttpResponse(json.dumps({"error": error}), 400)


class TestFullRefresh(TestCase):
    @staticmethod
    def _read(config_: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
            expecting_exception=expecting_exception,
        )

    @HttpMocker()
    @freezegun.freeze_time(_FROZEN_TIME)
    def test_read_records_full_refresh(self, http_mocker: HttpMocker) -> None:
        """Test full refresh sync for user_insights stream.

        The user_insights stream uses DatetimeBasedCursor with step P1D and QueryProperties
        with multiple chunks. We set start_date close to frozen time to minimize time slices.
        Using with_any_query_params() because the stream makes multiple requests with different
        period/metric combinations that are determined by the QueryProperties configuration.
        """
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )

        http_mocker.get(
            _get_user_insights_request_any_params(BUSINESS_ACCOUNT_ID).build(),
            _build_user_insights_response(),
        )

        test_config = ConfigBuilder().with_start_date("2024-01-15T00:00:00Z")
        output = self._read(config_=test_config)
        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record.get("page_id") == PAGE_ID
        assert record.get("business_account_id") == BUSINESS_ACCOUNT_ID

    @HttpMocker()
    @freezegun.freeze_time(_FROZEN_TIME)
    def test_substream_with_multiple_parent_accounts(self, http_mocker: HttpMocker) -> None:
        """Test user_insights stream against 2+ parent accounts per playbook requirements.

        This test verifies that the stream correctly processes data from multiple parent accounts
        and applies transformations (page_id, business_account_id) to records from each account.
        """
        http_mocker.get(
            get_account_request().build(),
            get_multiple_accounts_response(),
        )

        # Mock user_insights requests for both accounts
        http_mocker.get(
            _get_user_insights_request_any_params(BUSINESS_ACCOUNT_ID).build(),
            _build_user_insights_response(),
        )
        http_mocker.get(
            _get_user_insights_request_any_params(SECOND_BUSINESS_ACCOUNT_ID).build(),
            _build_user_insights_response(),
        )

        test_config = ConfigBuilder().with_start_date("2024-01-15T00:00:00Z")
        output = self._read(config_=test_config)

        # Verify we get records from both accounts
        assert len(output.records) == 2

        # Verify transformations on all records
        business_account_ids = {record.record.data.get("business_account_id") for record in output.records}
        assert BUSINESS_ACCOUNT_ID in business_account_ids
        assert SECOND_BUSINESS_ACCOUNT_ID in business_account_ids

        for record in output.records:
            assert "page_id" in record.record.data
            assert record.record.data["page_id"] is not None
            assert "business_account_id" in record.record.data
            assert record.record.data["business_account_id"] is not None


class TestIncremental(TestCase):
    @staticmethod
    def _read(
        config_: ConfigBuilder,
        state: list = None,
        expecting_exception: bool = False,
    ) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.incremental,
            state=state,
            expecting_exception=expecting_exception,
        )

    @HttpMocker()
    @freezegun.freeze_time(_FROZEN_TIME)
    def test_incremental_sync_first_sync_no_state(self, http_mocker: HttpMocker) -> None:
        """Test incremental sync with no prior state (first sync).

        Using with_any_query_params() because without prior state, the stream starts from
        start_date and creates multiple time slices with different period/metric combinations.
        """
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )

        http_mocker.get(
            _get_user_insights_request_any_params(BUSINESS_ACCOUNT_ID).build(),
            _build_user_insights_response(),
        )

        test_config = ConfigBuilder().with_start_date("2024-01-15T00:00:00Z")
        output = self._read(config_=test_config)
        assert len(output.records) == 1
        assert len(output.state_messages) >= 1

    @HttpMocker()
    @freezegun.freeze_time(_FROZEN_TIME)
    def test_incremental_sync_with_prior_state(self, http_mocker: HttpMocker) -> None:
        """Test incremental sync with prior state (subsequent sync).

        With prior state at 2024-01-15T00:00:00+00:00 and frozen time at 2024-01-15T12:00:00Z,
        the stream should request data with since=2024-01-15T00:00:00Z.
        We verify the outbound request includes the expected since parameter derived from state
        by mocking specific query params for each QueryProperties chunk.

        The DatetimeBasedCursor uses the state value as the starting point, and the frozen time
        determines the end datetime. With step P1D, there's only one time slice from state to now.
        """
        prior_state_value = "2024-01-15T00:00:00+00:00"
        # Expected since value derived from state - the API uses the state value format directly
        expected_since = "2024-01-15T00:00:00+00:00"
        # Expected until value is the frozen time (in the same format as the API expects)
        expected_until = "2024-01-15T12:00:00+00:00"

        state = (
            StateBuilder()
            .with_stream_state(
                _STREAM_NAME,
                {
                    "states": [
                        {
                            "partition": {"business_account_id": BUSINESS_ACCOUNT_ID},
                            "cursor": {"date": prior_state_value},
                        }
                    ]
                },
            )
            .build()
        )

        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )

        # Mock each QueryProperties chunk with specific params to validate the since parameter
        # Chunk 1: period=day, metric=follower_count,reach
        http_mocker.get(
            _get_user_insights_request_with_params(
                BUSINESS_ACCOUNT_ID, since=expected_since, until=expected_until, period="day", metric="follower_count,reach"
            ).build(),
            _build_user_insights_response(),
        )
        # Chunk 2: period=week, metric=reach
        http_mocker.get(
            _get_user_insights_request_with_params(
                BUSINESS_ACCOUNT_ID, since=expected_since, until=expected_until, period="week", metric="reach"
            ).build(),
            _build_user_insights_response(),
        )
        # Chunk 3: period=days_28, metric=reach
        http_mocker.get(
            _get_user_insights_request_with_params(
                BUSINESS_ACCOUNT_ID, since=expected_since, until=expected_until, period="days_28", metric="reach"
            ).build(),
            _build_user_insights_response(),
        )
        # Chunk 4: period=lifetime, metric=online_followers
        http_mocker.get(
            _get_user_insights_request_with_params(
                BUSINESS_ACCOUNT_ID, since=expected_since, until=expected_until, period="lifetime", metric="online_followers"
            ).build(),
            _build_user_insights_response(),
        )

        test_config = ConfigBuilder().with_start_date("2024-01-14T00:00:00Z")
        output = self._read(config_=test_config, state=state)

        # With specific mocks for each chunk, we can now assert exact record count
        # The merge strategy groups by date, and all chunks return the same date (2024-01-15T07:00:00+0000)
        # so records should be merged into 1 record
        assert len(output.records) == 1
        assert len(output.state_messages) >= 1

        # Verify the record has the expected business_account_id
        record = output.records[0].record.data
        assert record.get("business_account_id") == BUSINESS_ACCOUNT_ID

        # Verify the record date matches the expected date from our response
        # Note: The date is normalized to RFC 3339 format (+00:00) by the schema normalization
        assert record.get("date") == "2024-01-15T07:00:00+00:00"


class TestErrorHandling(TestCase):
    """Test error handling for user_insights stream.

    The user_insights stream has IGNORE error handlers for:
    - error_subcode 2108006: "Insights error for business_account_id: {message}"
    - code 100 with error_subcode 33: "Check provided permissions for: {message}"
    - code 10 with specific permission message: "Check provided permissions for: {message}"

    For IGNORE handlers, we verify:
    1. No ERROR logs are produced
    2. The configured error_message appears in logs (proving the handler was triggered)
    3. Zero records are returned (graceful handling)
    """

    @staticmethod
    def _read(config_: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
            expecting_exception=expecting_exception,
        )

    @HttpMocker()
    @freezegun.freeze_time(_FROZEN_TIME)
    def test_error_subcode_2108006_is_ignored(self, http_mocker: HttpMocker) -> None:
        """Test that error_subcode 2108006 is gracefully ignored.

        Verifies both error code and error message assertion per playbook requirements.
        """
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )

        error_message = "Invalid parameter"
        http_mocker.get(
            _get_user_insights_request_any_params(BUSINESS_ACCOUNT_ID).build(),
            _build_error_response(code=100, message=error_message, error_subcode=2108006),
        )

        test_config = ConfigBuilder().with_start_date("2024-01-15T00:00:00Z")
        output = self._read(config_=test_config)
        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
        log_messages = [log.log.message for log in output.logs]
        assert any(
            "Insights error for business_account_id" in msg for msg in log_messages
        ), f"Expected 'Insights error for business_account_id' in logs but got: {log_messages}"

    @HttpMocker()
    @freezegun.freeze_time(_FROZEN_TIME)
    def test_error_code_100_subcode_33_is_ignored(self, http_mocker: HttpMocker) -> None:
        """Test that error code 100 with subcode 33 is gracefully ignored.

        Verifies both error code and error message assertion per playbook requirements.
        """
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )

        error_message = "Unsupported get request"
        http_mocker.get(
            _get_user_insights_request_any_params(BUSINESS_ACCOUNT_ID).build(),
            _build_error_response(code=100, message=error_message, error_subcode=33),
        )

        test_config = ConfigBuilder().with_start_date("2024-01-15T00:00:00Z")
        output = self._read(config_=test_config)
        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
        log_messages = [log.log.message for log in output.logs]
        assert any(
            "Check provided permissions for" in msg for msg in log_messages
        ), f"Expected 'Check provided permissions for' in logs but got: {log_messages}"

    @HttpMocker()
    @freezegun.freeze_time(_FROZEN_TIME)
    def test_error_code_10_permission_denied_is_ignored(self, http_mocker: HttpMocker) -> None:
        """Test that error code 10 with permission denied message is gracefully ignored.

        Verifies both error code and error message assertion per playbook requirements.
        """
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )

        error_message = "(#10) Application does not have permission for this action"
        http_mocker.get(
            _get_user_insights_request_any_params(BUSINESS_ACCOUNT_ID).build(),
            _build_error_response(code=10, message=error_message),
        )

        test_config = ConfigBuilder().with_start_date("2024-01-15T00:00:00Z")
        output = self._read(config_=test_config)
        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
        log_messages = [log.log.message for log in output.logs]
        assert any(
            "Check provided permissions for" in msg for msg in log_messages
        ), f"Expected 'Check provided permissions for' in logs but got: {log_messages}"
