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

        test_config = ConfigBuilder().with_start_date("2024-01-15T12:00:00Z")
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

        test_config = ConfigBuilder().with_start_date("2024-01-15T12:00:00Z")
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

        test_config = ConfigBuilder().with_start_date("2024-01-15T12:00:00Z")
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

        The DatetimeBasedCursor uses the state value as the starting point, and day_delta(1)
        determines the end datetime. With step P1D, there are two time slices from state to
        end_datetime (frozen_time + 1 day).
        """
        prior_state_value = "2024-01-15T00:00:00+00:00"
        # Expected since value derived from state - the API uses the state value format directly
        expected_since_slice1 = "2024-01-15T00:00:00+00:00"
        expected_until_slice1 = "2024-01-16T00:00:00+00:00"
        # Second slice covers the remainder up to day_delta(1) from frozen time
        expected_since_slice2 = "2024-01-16T00:00:00+00:00"
        expected_until_slice2 = "2024-01-16T12:00:00+00:00"

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

        # Mock each QueryProperties chunk for slice 1 to validate the since parameter from state
        for period, metric in [("day", "follower_count,reach"), ("week", "reach"), ("days_28", "reach"), ("lifetime", "online_followers")]:
            http_mocker.get(
                _get_user_insights_request_with_params(
                    BUSINESS_ACCOUNT_ID, since=expected_since_slice1, until=expected_until_slice1, period=period, metric=metric
                ).build(),
                _build_user_insights_response(),
            )

        # Mock each QueryProperties chunk for slice 2
        for period, metric in [("day", "follower_count,reach"), ("week", "reach"), ("days_28", "reach"), ("lifetime", "online_followers")]:
            http_mocker.get(
                _get_user_insights_request_with_params(
                    BUSINESS_ACCOUNT_ID, since=expected_since_slice2, until=expected_until_slice2, period=period, metric=metric
                ).build(),
                _build_user_insights_response(),
            )

        test_config = ConfigBuilder().with_start_date("2024-01-14T00:00:00Z")
        output = self._read(config_=test_config, state=state)

        # With day_delta(1), two P1D slices are generated from state to end_datetime.
        # Each slice returns records merged by date, producing 1 record per slice.
        # Both slices return mock data with the same date, yielding 2 records total.
        assert len(output.records) == 2
        assert len(output.state_messages) >= 1

        # Verify the records have the expected business_account_id
        for record_msg in output.records:
            record = record_msg.record.data
            assert record.get("business_account_id") == BUSINESS_ACCOUNT_ID
            # Note: The date is normalized to RFC 3339 format (+00:00) by the schema normalization
            assert record.get("date") == "2024-01-15T07:00:00+00:00"


class TestFutureStateRegression(TestCase):
    """Regression tests for future-dated cursor state.

    When the Meta API returns an end_time ahead of current UTC (e.g. for
    UTC-negative accounts), the cursor can advance to a future timestamp.
    On the next sync, sending that future value as ``since`` causes Meta to
    reject the request (HTTP 400).

    The fix has two parts:
    1. ``lookback_window: P1D`` in the manifest pulls the effective start
       back by one day, so even a slightly-future cursor produces a non-future
       ``since`` parameter.
    2. ``UserInsightsExtractor`` filters out records whose ``date`` is more
       than 1 day ahead of current UTC (matching the ``day_delta(1)``
       boundary), preventing the cursor from advancing further into the
       future while still allowing legitimate UTC+ account records that are
       only hours ahead.

    These tests verify that:
    - A future state does not produce a future ``since`` parameter.
    - Records from UTC+ accounts (hours ahead of UTC) pass through.
    - Records more than 1 day ahead are filtered out.
    """

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
    def test_future_state_does_not_produce_future_since(self, http_mocker: HttpMocker) -> None:
        """A saved cursor 1 day in the future must not produce a future ``since``.

        Frozen time: 2024-01-15T12:00:00Z
        Saved state date: 2024-01-16T07:00:00+00:00 (future)

        With lookback_window P1D the effective start is pulled back by one day:
            2024-01-16T07:00:00 - P1D = 2024-01-15T07:00:00+00:00

        end_datetime = day_delta(1) = 2024-01-16T12:00:00Z

        So we expect two P1D slices:
            slice 1: since=2024-01-15T07:00:00+00:00  until=2024-01-16T07:00:00+00:00
            slice 2: since=2024-01-16T07:00:00+00:00  until=2024-01-16T12:00:00+00:00

        The crucial assertion: slice 1 ``since`` is 2024-01-15T07:00:00+00:00
        (before frozen time), NOT 2024-01-16T07:00:00+00:00 (the raw state).

        For slice 2 the ``since`` equals the original state; that slice is in
        the future but will return no data (or the future-record filter in
        ``UserInsightsExtractor`` will drop any records), so the cursor will
        not advance further.
        """
        future_state_value = "2024-01-16T07:00:00+00:00"

        # After lookback: effective start = state - P1D
        expected_since_slice1 = "2024-01-15T07:00:00+00:00"
        expected_until_slice1 = "2024-01-16T07:00:00+00:00"
        # Second slice covers remainder up to end_datetime
        expected_since_slice2 = "2024-01-16T07:00:00+00:00"
        expected_until_slice2 = "2024-01-16T12:00:00+00:00"

        state = (
            StateBuilder()
            .with_stream_state(
                _STREAM_NAME,
                {
                    "states": [
                        {
                            "partition": {"business_account_id": BUSINESS_ACCOUNT_ID},
                            "cursor": {"date": future_state_value},
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

        # Slice 1: since is the lookback-adjusted value (NOT the future state)
        for period, metric in [("day", "follower_count,reach"), ("week", "reach"), ("days_28", "reach"), ("lifetime", "online_followers")]:
            http_mocker.get(
                _get_user_insights_request_with_params(
                    BUSINESS_ACCOUNT_ID, since=expected_since_slice1, until=expected_until_slice1, period=period, metric=metric
                ).build(),
                _build_user_insights_response(),
            )

        # Slice 2: future range - return a future-dated record to prove filter drops it
        future_body = {
            "data": [
                {
                    "name": "follower_count",
                    "period": "day",
                    "values": [{"value": 999, "end_time": "2024-01-17T07:00:00+0000"}],
                    "title": "Follower Count",
                    "description": "Total number of followers",
                    "id": f"{BUSINESS_ACCOUNT_ID}/insights/follower_count/day",
                },
            ]
        }
        future_response = HttpResponse(json.dumps(future_body), 200)
        for period, metric in [("day", "follower_count,reach"), ("week", "reach"), ("days_28", "reach"), ("lifetime", "online_followers")]:
            http_mocker.get(
                _get_user_insights_request_with_params(
                    BUSINESS_ACCOUNT_ID, since=expected_since_slice2, until=expected_until_slice2, period=period, metric=metric
                ).build(),
                future_response,
            )

        test_config = ConfigBuilder().with_start_date("2024-01-14T00:00:00Z")
        output = self._read(config_=test_config, state=state)

        # Slice 1 returns records with date 2024-01-15T07:00:00+00:00 (not future) → emitted.
        # Slice 2 returns records with date 2024-01-17T07:00:00+00:00 (>1 day ahead) → filtered out.
        # So we should get exactly 1 record from slice 1.
        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record.get("business_account_id") == BUSINESS_ACCOUNT_ID
        # The emitted record date should be from slice 1, not the future slice 2
        assert record.get("date") == "2024-01-15T07:00:00+00:00"

        # Verify state was emitted (cursor should not advance to the future date)
        assert len(output.state_messages) >= 1

    @HttpMocker()
    @freezegun.freeze_time(_FROZEN_TIME)
    def test_utc_plus_record_not_filtered(self, http_mocker: HttpMocker) -> None:
        """A record ~8 h ahead of UTC (simulating UTC+8) must NOT be filtered.

        Frozen time: 2024-01-15T12:00:00Z
        Record end_time: 2024-01-15T20:00:00+0000 (8 h ahead — UTC+8 day boundary)

        The filter threshold is ``now_utc + timedelta(days=1)`` =
        2024-01-16T12:00:00Z.  Since 2024-01-15T20:00:00 < 2024-01-16T12:00:00,
        this record should pass through and be emitted.
        """
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )

        # Build a response with end_time 8 hours ahead of frozen time (UTC+8 account)
        utc_plus_body = {
            "data": [
                {
                    "name": "follower_count",
                    "period": "day",
                    "values": [{"value": 42, "end_time": "2024-01-15T20:00:00+0000"}],
                    "title": "Follower Count",
                    "description": "Total number of followers",
                    "id": f"{BUSINESS_ACCOUNT_ID}/insights/follower_count/day",
                },
            ]
        }
        utc_plus_response = HttpResponse(json.dumps(utc_plus_body), 200)

        http_mocker.get(
            _get_user_insights_request_any_params(BUSINESS_ACCOUNT_ID).build(),
            utc_plus_response,
        )

        test_config = ConfigBuilder().with_start_date("2024-01-15T00:00:00Z")
        output = self._read(config_=test_config)

        # The record is 8 h ahead of UTC but within the 1-day filter threshold → emitted
        assert len(output.records) >= 1
        record = output.records[0].record.data
        assert record.get("business_account_id") == BUSINESS_ACCOUNT_ID
        assert record.get("date") == "2024-01-15T20:00:00+00:00"


class TestFutureSinceParamErrorHandling(TestCase):
    """Regression test for oncall issue #11701: 'since param is not valid'.

    Reproduces the exact user error scenario:

    1. A UTC+ account syncs user_insights. Meta returns end_time at the
       account's day boundary expressed in UTC (e.g. 07:00 UTC for UTC+7),
       which is ahead of now_utc().
    2. The cursor advances to that future-offset date.
    3. On the *next* sync, DatetimeBasedCursor generates a time slice whose
       ``since`` parameter is in the future.
    4. Instagram API rejects the request with HTTP 400, error code 100,
       message "(#100) since param is not valid".

    Without the HttpResponseFilter fix, step 4 would cause a sync failure.
    With the fix, the error is gracefully ignored (IGNORE action) and the
    sync completes — the skipped window will be picked up on the next sync
    once the date is no longer in the future.
    """

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
    def test_future_since_param_is_ignored(self, http_mocker: HttpMocker) -> None:
        """Simulate the exact error from oncall #11701.

        Frozen time: 2024-01-15T12:00:00Z
        Saved cursor: 2024-01-16T07:00:00+00:00 (future — from a UTC+7 account)

        With lookback_window P1D, the effective start is pulled back:
            2024-01-16T07:00:00 - P1D = 2024-01-15T07:00:00+00:00

        end_datetime = day_delta(1) = 2024-01-16T12:00:00Z

        Slice 1: since=2024-01-15T07:00:00  until=2024-01-16T07:00:00  → 200 OK
        Slice 2: since=2024-01-16T07:00:00  until=2024-01-16T12:00:00  → 400 error

        Slice 2's ``since`` is in the future (> frozen time). The Instagram
        API returns HTTP 400 with:
            {"error": {"code": 100, "message": "(#100) since param is not valid. ..."}}

        Without the fix this would fail the sync. With the fix (HttpResponseFilter
        IGNORE action), the error is silently skipped and we still get records
        from slice 1.
        """
        future_state_value = "2024-01-16T07:00:00+00:00"

        # After lookback P1D: effective start = state - P1D
        expected_since_slice1 = "2024-01-15T07:00:00+00:00"
        expected_until_slice1 = "2024-01-16T07:00:00+00:00"
        # Slice 2: the future window that triggers the API error
        expected_since_slice2 = "2024-01-16T07:00:00+00:00"
        expected_until_slice2 = "2024-01-16T12:00:00+00:00"

        state = (
            StateBuilder()
            .with_stream_state(
                _STREAM_NAME,
                {
                    "states": [
                        {
                            "partition": {"business_account_id": BUSINESS_ACCOUNT_ID},
                            "cursor": {"date": future_state_value},
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

        # Slice 1: non-future window returns data normally
        for period, metric in [("day", "follower_count,reach"), ("week", "reach"), ("days_28", "reach"), ("lifetime", "online_followers")]:
            http_mocker.get(
                _get_user_insights_request_with_params(
                    BUSINESS_ACCOUNT_ID, since=expected_since_slice1, until=expected_until_slice1, period=period, metric=metric
                ).build(),
                _build_user_insights_response(),
            )

        # Slice 2: future window — Instagram API returns the exact error from oncall #11701
        since_invalid_error = _build_error_response(
            code=100,
            message="(#100) since param is not valid. Metrics data is available for the last 2 years",
        )
        for period, metric in [("day", "follower_count,reach"), ("week", "reach"), ("days_28", "reach"), ("lifetime", "online_followers")]:
            http_mocker.get(
                _get_user_insights_request_with_params(
                    BUSINESS_ACCOUNT_ID, since=expected_since_slice2, until=expected_until_slice2, period=period, metric=metric
                ).build(),
                since_invalid_error,
            )

        test_config = ConfigBuilder().with_start_date("2024-01-14T00:00:00Z")
        output = self._read(config_=test_config, state=state)

        # The sync should succeed despite the HTTP 400 on slice 2.
        # Slice 1 returns valid data → at least 1 record emitted.
        assert len(output.records) >= 1
        record = output.records[0].record.data
        assert record.get("business_account_id") == BUSINESS_ACCOUNT_ID

        # No ERROR-level logs — the error handler converted 400 → IGNORE
        assert not any(log.log.level == "ERROR" for log in output.logs)

        # The handler's error_message should appear in logs, proving it fired
        log_messages = [log.log.message for log in output.logs]
        assert any(
            "Skipping time window with future 'since' date" in msg for msg in log_messages
        ), f"Expected 'Skipping time window with future 'since' date' in logs but got: {log_messages}"

        # State should still be emitted (sync completes normally)
        assert len(output.state_messages) >= 1


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
