#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
from copy import deepcopy
from unittest.mock import ANY

import pytest

from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteErrorTraceMessage,
    AirbyteMessage,
    AirbyteTraceMessage,
    FailureType,
    Status,
    TraceType,
    Type,
)
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template

from .conftest import AUTH_BODY, AuthBuilder, GoogleSheetsBaseTest, oauth_credentials, service_account_credentials, service_account_info


_SPREADSHEET_ID = "a_spreadsheet_id"

_STREAM_NAME = "a_stream_name"
_B_STREAM_NAME = "b_stream_name"
_C_STREAM_NAME = "c_stream_name"


_CONFIG = {"spreadsheet_id": _SPREADSHEET_ID, "credentials": oauth_credentials, "batch_size": 200}

_SERVICE_CONFIG = {"spreadsheet_id": _SPREADSHEET_ID, "credentials": service_account_credentials}

GET_SPREADSHEET_INFO = "get_spreadsheet_info"
GET_SHEETS_FIRST_ROW = "get_sheet_first_row"
GET_STREAM_DATA = "get_stream_data"


class TestCredentials(GoogleSheetsBaseTest):
    def test_given_authentication_error_when_check_then_status_is_failed(self) -> None:
        del self._config["credentials"]["client_secret"]

        output = self._check(self._config, expecting_exception=False)
        msg = AirbyteConnectionStatus(status=Status.FAILED, message="Config validation error: 'Service' was expected")
        expected_message = AirbyteMessage(type=Type.CONNECTION_STATUS, connectionStatus=msg)
        assert output._messages[-1] == expected_message

    @pytest.mark.skip("Need service credentials to test this behavior")
    def test_given_service_authentication_error_when_check_then_status_is_failed(self) -> None:
        # todo, test this with service credentials
        wrong_service_account_info = deepcopy(service_account_info)
        del wrong_service_account_info["client_email"]
        wrong_service_account_info_encoded = json.dumps(service_account_info)  # .encode("utf-8")
        wrong_service_account_credentials = {
            "auth_type": "Service",
            "service_account_info": wrong_service_account_info_encoded,
        }
        wrong_config = {"spreadsheet_id": _SPREADSHEET_ID, "credentials": wrong_service_account_credentials}
        # connection_status = self._source.check(Mock(), wrong_service_account_credentials)
        output = self._check(wrong_config, expecting_exception=True)

        msg = AirbyteConnectionStatus(status=Status.FAILED, message="")
        expected_message = AirbyteMessage(type=Type.CONNECTION_STATUS, connectionStatus=msg)
        assert output._messages[-1] == expected_message

    @HttpMocker()
    def test_invalid_credentials_error_message_when_check(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(
            AuthBuilder.get_token_endpoint().with_body(AUTH_BODY).build(),
            HttpResponse(json.dumps(find_template("auth_invalid_client", __file__)), 401),
        )
        output = self._check(self._config, expecting_exception=True)
        trace_message = AirbyteTraceMessage(
            type=TraceType.ERROR,
            emitted_at=ANY,
            error=AirbyteErrorTraceMessage(
                message="Something went wrong in the connector. See the logs for more details.",
                internal_message="401 Client Error: None for url: https://www.googleapis.com/oauth2/v4/token",
                failure_type=FailureType.system_error,
                stack_trace=ANY,
            ),
        )
        expected_message = AirbyteMessage(type=Type.TRACE, trace=trace_message)
        assert output.errors[-1] == expected_message

    def test_check_invalid_creds_json_file(self) -> None:
        invalid_creds_json_file = {}
        output = self._check(invalid_creds_json_file, expecting_exception=True)
        msg = AirbyteConnectionStatus(status=Status.FAILED, message="Config validation error: 'spreadsheet_id' is a required property")
        expected_message = AirbyteMessage(type=Type.CONNECTION_STATUS, connectionStatus=msg)
        assert output._messages[-1] == expected_message

    @HttpMocker()
    def test_discover_invalid_credentials_error_message(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(
            AuthBuilder.get_token_endpoint().with_body(AUTH_BODY).build(),
            HttpResponse(json.dumps(find_template("auth_invalid_client", __file__)), 401),
        )

        trace_message = AirbyteTraceMessage(
            type=TraceType.ERROR,
            emitted_at=ANY,
            error=AirbyteErrorTraceMessage(
                message="Something went wrong in the connector. See the logs for more details.",
                internal_message="401 Client Error: None for url: https://www.googleapis.com/oauth2/v4/token",
                failure_type=FailureType.system_error,
                stack_trace=ANY,
            ),
        )
        expected_message = AirbyteMessage(type=Type.TRACE, trace=trace_message)
        output = self._discover(self._config, expecting_exception=True)
        assert output.errors[-1] == expected_message
