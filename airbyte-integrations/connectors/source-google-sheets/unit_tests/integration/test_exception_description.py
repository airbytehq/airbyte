#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from unittest.mock import ANY, patch

from requests.status_codes import codes as status_codes

from airbyte_cdk.models import (
    AirbyteErrorTraceMessage,
    AirbyteMessage,
    AirbyteTraceMessage,
    FailureType,
    TraceType,
    Type,
)
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.mock_http import HttpMocker

from .conftest import GoogleSheetsBaseTest

_SPREADSHEET_ID = "a_spreadsheet_id"

_STREAM_NAME = "a_stream_name"


def exception_description_by_status_code(code: int, spreadsheet_id) -> str:
    if code in [status_codes.INTERNAL_SERVER_ERROR, status_codes.BAD_GATEWAY, status_codes.SERVICE_UNAVAILABLE]:
        return (
            "There was an issue with the Google Sheets API. This is usually a temporary issue from Google's side."
            " Please try again. If this issue persists, contact support"
        )
    if code == status_codes.FORBIDDEN:
        return (
            f"The authenticated Google Sheets user does not have permissions to view the spreadsheet with id {spreadsheet_id}. "
            "Please ensure the authenticated user has access to the Spreadsheet and reauthenticate. If the issue persists, contact support"
        )
    if code == status_codes.NOT_FOUND:
        return (
            f"The requested Google Sheets spreadsheet with id {spreadsheet_id} does not exist. "
            f"Please ensure the Spreadsheet Link you have set is valid and the spreadsheet exists. If the issue persists, contact support"
        )

    if code == status_codes.TOO_MANY_REQUESTS:
        return "Rate limit has been reached. Please try later or request a higher quota for your account."

    return ""


class TestExceptionDescriptionByStatusCode(GoogleSheetsBaseTest):
    @HttpMocker()
    def test_invalid_link_error_message_when_check(self, http_mocker: HttpMocker) -> None:
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, "invalid_link", status_codes.NOT_FOUND)
        error_message = exception_description_by_status_code(status_codes.NOT_FOUND, _SPREADSHEET_ID)
        output = self._check(self._config, expecting_exception=True)
        trace_message = AirbyteTraceMessage(
            type=TraceType.ERROR,
            emitted_at=ANY,
            error=AirbyteErrorTraceMessage(
                message=error_message,
                internal_message=ANY,
                failure_type=FailureType.system_error,
                stack_trace=ANY,
            ),
        )
        expected_message = AirbyteMessage(type=Type.TRACE, trace=trace_message)
        assert output.errors[-1] == expected_message

    @HttpMocker()
    def test_check_access_expired(self, http_mocker: HttpMocker) -> None:
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, "invalid_permissions", status_codes.FORBIDDEN)
        expected_message = (
            f"{exception_description_by_status_code(status_codes.FORBIDDEN, _SPREADSHEET_ID)}. The caller does not have right permissions."
        )

        output = self._check(self._config, expecting_exception=True)
        trace_message = AirbyteTraceMessage(
            type=TraceType.ERROR,
            emitted_at=ANY,
            error=AirbyteErrorTraceMessage(
                message=expected_message,
                internal_message=ANY,
                failure_type=FailureType.config_error,
                stack_trace=ANY,
            ),
        )
        expected_airbyte_message = AirbyteMessage(type=Type.TRACE, trace=trace_message)
        assert output.errors[-1] == expected_airbyte_message

    @HttpMocker()
    def test_discover_could_not_run_discover(self, http_mocker: HttpMocker) -> None:
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, "internal_server_error", status_codes.INTERNAL_SERVER_ERROR)

        with patch("time.sleep"):
            output = self._discover(self._config, expecting_exception=True)
            expected_message = exception_description_by_status_code(status_codes.INTERNAL_SERVER_ERROR, _SPREADSHEET_ID)

            trace_message = AirbyteTraceMessage(
                type=TraceType.ERROR,
                emitted_at=ANY,
                error=AirbyteErrorTraceMessage(
                    message="Something went wrong in the connector. See the logs for more details.",
                    internal_message=expected_message,
                    failure_type=FailureType.system_error,
                    stack_trace=ANY,
                ),
            )
            expected_message = AirbyteMessage(type=Type.TRACE, trace=trace_message)
            assert output.errors[-1] == expected_message

    @HttpMocker()
    def test_discover_404_error(self, http_mocker: HttpMocker) -> None:
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, "invalid_link", status_codes.NOT_FOUND)
        output = self._discover(self._config, expecting_exception=True)
        error_message = exception_description_by_status_code(status_codes.NOT_FOUND, _SPREADSHEET_ID)
        trace_message = AirbyteTraceMessage(
            type=TraceType.ERROR,
            emitted_at=ANY,
            error=AirbyteErrorTraceMessage(
                message=error_message,
                internal_message=ANY,
                failure_type=FailureType.system_error,
                stack_trace=ANY,
            ),
        )
        expected_message = AirbyteMessage(type=Type.TRACE, trace=trace_message)
        assert output.errors[-1] == expected_message

    @HttpMocker()
    def test_discover_403_error(self, http_mocker: HttpMocker) -> None:
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, "invalid_permissions", status_codes.FORBIDDEN)
        output = self._discover(self._config, expecting_exception=True)

        expected_message = (
            f"{exception_description_by_status_code(status_codes.FORBIDDEN, _SPREADSHEET_ID)}. The caller does not have right permissions."
        )

        trace_message = AirbyteTraceMessage(
            type=TraceType.ERROR,
            emitted_at=ANY,
            error=AirbyteErrorTraceMessage(
                message=expected_message,
                internal_message=ANY,
                failure_type=FailureType.config_error,
                stack_trace=ANY,
            ),
        )
        expected_airbyte_message = AirbyteMessage(type=Type.TRACE, trace=trace_message)
        assert output.errors[-1] == expected_airbyte_message

    @HttpMocker()
    def test_read_429_error(self, http_mocker: HttpMocker) -> None:
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, "read_records_meta", 200)
        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, "read_records_range", 200)
        GoogleSheetsBaseTest.get_stream_data(http_mocker, "rate_limit_error", status_codes.TOO_MANY_REQUESTS)

        configured_catalog = (
            CatalogBuilder()
            .with_stream(
                ConfiguredAirbyteStreamBuilder()
                .with_name(_STREAM_NAME)
                .with_json_schema({"properties": {"header_1": {"type": ["null", "string"]}, "header_2": {"type": ["null", "string"]}}})
            )
            .build()
        )

        with patch("time.sleep"):
            output = self._read(self._config, catalog=configured_catalog, expecting_exception=True)

        expected_message = f"{exception_description_by_status_code(status_codes.TOO_MANY_REQUESTS, _STREAM_NAME)}"

        assert output.errors[0].trace.error.internal_message == expected_message

    @HttpMocker()
    def test_read_403_error(self, http_mocker: HttpMocker) -> None:
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, "read_records_meta", 200)
        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, "read_records_range", 200)
        GoogleSheetsBaseTest.get_stream_data(http_mocker, "invalid_permissions", status_codes.FORBIDDEN)

        configured_catalog = (
            CatalogBuilder()
            .with_stream(
                ConfiguredAirbyteStreamBuilder()
                .with_name(_STREAM_NAME)
                .with_json_schema({"properties": {"header_1": {"type": ["null", "string"]}, "header_2": {"type": ["null", "string"]}}})
            )
            .build()
        )

        output = self._read(self._config, catalog=configured_catalog, expecting_exception=True)
        expected_message = (
            f"{exception_description_by_status_code(status_codes.FORBIDDEN, _SPREADSHEET_ID)}. The caller does not have right permissions."
        )
        assert output.errors[0].trace.error.message == expected_message

    @HttpMocker()
    def test_read_500_error(self, http_mocker: HttpMocker) -> None:
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, "read_records_meta", 200)
        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, "read_records_range", 200)
        GoogleSheetsBaseTest.get_stream_data(http_mocker, "internal_server_error", status_codes.INTERNAL_SERVER_ERROR)

        configured_catalog = (
            CatalogBuilder()
            .with_stream(
                ConfiguredAirbyteStreamBuilder()
                .with_name(_STREAM_NAME)
                .with_json_schema({"properties": {"header_1": {"type": ["null", "string"]}, "header_2": {"type": ["null", "string"]}}})
            )
            .build()
        )

        with patch("time.sleep"):
            output = self._read(self._config, catalog=configured_catalog, expecting_exception=True)

        expected_message = f"{exception_description_by_status_code(status_codes.INTERNAL_SERVER_ERROR, _SPREADSHEET_ID)}"
        assert output.errors[0].trace.error.internal_message == expected_message
