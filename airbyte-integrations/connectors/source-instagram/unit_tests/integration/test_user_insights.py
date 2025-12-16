#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template
from airbyte_cdk.test.state_builder import StateBuilder

from .config import BUSINESS_ACCOUNT_ID, PAGE_ID, ConfigBuilder
from .request_builder import RequestBuilder, get_account_request
from .response_builder import get_account_response
from .utils import config, read_output


_STREAM_NAME = "user_insights"

_FROZEN_TIME = "2024-01-15T12:00:00Z"


def _get_user_insights_request_any_params(business_account_id: str) -> RequestBuilder:
    """Create a request builder for user_insights with any query params.

    The user_insights stream uses DatetimeBasedCursor with step P1D which creates
    multiple time slices. Using with_any_query_params() allows matching all these requests.
    """
    return RequestBuilder.get_user_lifetime_insights_endpoint(item_id=business_account_id).with_any_query_params()


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

        The user_insights stream uses DatetimeBasedCursor with step P1D, creating
        multiple time slices. We use with_any_query_params() to match all requests since
        the datetime parameters are dynamic.
        """
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )

        # Mock all user_insights requests with any query params since datetime params are dynamic
        http_mocker.get(
            _get_user_insights_request_any_params(BUSINESS_ACCOUNT_ID).build(),
            HttpResponse(json.dumps(find_template("user_insights", __file__)), 200),
        )

        output = self._read(config_=config())
        # Verify records are returned and contain expected fields
        assert len(output.records) >= 1
        record = output.records[0].record.data
        assert record.get("page_id") == PAGE_ID
        assert record.get("business_account_id") == BUSINESS_ACCOUNT_ID


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
        """Test incremental sync with no prior state (first sync)."""
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )

        http_mocker.get(
            _get_user_insights_request_any_params(BUSINESS_ACCOUNT_ID).build(),
            HttpResponse(json.dumps(find_template("user_insights", __file__)), 200),
        )

        output = self._read(config_=config())
        assert len(output.records) >= 1
        # Verify state messages are emitted for incremental sync
        assert len(output.state_messages) >= 1

    @HttpMocker()
    @freezegun.freeze_time(_FROZEN_TIME)
    def test_incremental_sync_with_prior_state(self, http_mocker: HttpMocker) -> None:
        """Test incremental sync with prior state (subsequent sync)."""
        prior_state_value = "2024-01-14T07:00:00+00:00"
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

        http_mocker.get(
            _get_user_insights_request_any_params(BUSINESS_ACCOUNT_ID).build(),
            HttpResponse(json.dumps(find_template("user_insights", __file__)), 200),
        )

        output = self._read(config_=config(), state=state)
        assert len(output.records) >= 1
        assert len(output.state_messages) >= 1


class TestErrorHandling(TestCase):
    """Test error handling for user_insights stream.

    The user_insights stream has IGNORE error handlers for:
    - error_subcode 2108006
    - code 100 with error_subcode 33
    - code 10 with specific permission message

    For IGNORE handlers, we verify no ERROR logs are produced.
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
        """Test that error_subcode 2108006 is gracefully ignored."""
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )

        http_mocker.get(
            _get_user_insights_request_any_params(BUSINESS_ACCOUNT_ID).build(),
            HttpResponse(json.dumps(find_template("user_insights_for_error_subcode_2108006", __file__)), 400),
        )

        output = self._read(config_=config())
        # For IGNORE handlers, verify no ERROR logs are produced
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    @freezegun.freeze_time(_FROZEN_TIME)
    def test_error_code_100_subcode_33_is_ignored(self, http_mocker: HttpMocker) -> None:
        """Test that error code 100 with subcode 33 is gracefully ignored."""
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )

        http_mocker.get(
            _get_user_insights_request_any_params(BUSINESS_ACCOUNT_ID).build(),
            HttpResponse(json.dumps(find_template("user_insights_for_error_code_100_subcode_33", __file__)), 400),
        )

        output = self._read(config_=config())
        # For IGNORE handlers, verify no ERROR logs are produced
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    @freezegun.freeze_time(_FROZEN_TIME)
    def test_error_code_10_permission_denied_is_ignored(self, http_mocker: HttpMocker) -> None:
        """Test that error code 10 with permission denied message is gracefully ignored."""
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )

        http_mocker.get(
            _get_user_insights_request_any_params(BUSINESS_ACCOUNT_ID).build(),
            HttpResponse(json.dumps(find_template("user_insights_for_error_code_10", __file__)), 400),
        )

        output = self._read(config_=config())
        # For IGNORE handlers, verify no ERROR logs are produced
        assert not any(log.log.level == "ERROR" for log in output.logs)
