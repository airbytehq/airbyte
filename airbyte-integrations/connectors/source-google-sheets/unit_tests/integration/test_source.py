#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
from copy import deepcopy
from unittest.mock import ANY

import pytest
from requests.status_codes import codes as status_codes

from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteErrorTraceMessage,
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    AirbyteStreamStatusTraceMessage,
    AirbyteTraceMessage,
    ConfiguredAirbyteCatalog,
    FailureType,
    Level,
    Status,
    StreamDescriptor,
    SyncMode,
    TraceType,
    Type,
)
from airbyte_cdk.models.airbyte_protocol import AirbyteStateBlob, AirbyteStreamStatus
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template

from .conftest import GoogleSheetsBaseTest, oauth_credentials, service_account_credentials


_SPREADSHEET_ID = "a_spreadsheet_id"

_STREAM_NAME = "a_stream_name"
_B_STREAM_NAME = "b_stream_name"
_C_STREAM_NAME = "c_stream_name"


_CONFIG = {"spreadsheet_id": _SPREADSHEET_ID, "credentials": oauth_credentials, "batch_size": 200}

_SERVICE_CONFIG = {"spreadsheet_id": _SPREADSHEET_ID, "credentials": service_account_credentials}

GET_SPREADSHEET_INFO = "get_spreadsheet_info"
GET_SHEETS_FIRST_ROW = "get_sheet_first_row"
GET_STREAM_DATA = "get_stream_data"


class TestSourceCheck(GoogleSheetsBaseTest):
    @HttpMocker()
    def test_given_spreadsheet_when_check_then_status_is_succeeded(self, http_mocker: HttpMocker) -> None:
        TestSourceCheck.get_spreadsheet_info_and_sheets(http_mocker, "check_succeeded_meta")
        TestSourceCheck.get_sheet_first_row(http_mocker, "check_succeeded_range")

        output = self._check(self._config, expecting_exception=False)
        expected_message = AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="Check succeeded"))
        assert output.logs[-1] == expected_message

    @HttpMocker()
    def test_check_expected_to_read_data_from_1_sheet(self, http_mocker: HttpMocker) -> None:
        TestSourceCheck.get_spreadsheet_info_and_sheets(http_mocker, "check_succeeded_meta", 200)
        TestSourceCheck.get_sheet_first_row(http_mocker, "check_wrong_range", 200)
        error_message = (
            f"Unable to read the schema of sheet. Error: Unexpected return result: Sheet was expected to contain data on exactly 1 sheet."
        )
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
    def test_check_duplicated_headers(self, http_mocker: HttpMocker) -> None:
        # With headers, we refer to properties that will be used for schema
        TestSourceCheck.get_spreadsheet_info_and_sheets(http_mocker, "check_succeeded_meta", 200)
        TestSourceCheck.get_sheet_first_row(http_mocker, "check_duplicate_headers", 200)

        error_message = f"The following duplicate headers were found in the sheet. Please fix them to continue: ['header1']"
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
        assert output.is_in_logs("Duplicate headers")

    @HttpMocker()
    def test_given_grid_sheet_type_with_at_least_one_row_when_discover_then_return_stream(self, http_mocker: HttpMocker) -> None:
        TestSourceCheck.get_spreadsheet_info_and_sheets(http_mocker, "only_headers_meta", 200)
        TestSourceCheck.get_sheet_first_row(http_mocker, "only_headers_range", 200)

        expected_schema = {
            "$schema": "https://json-schema.org/draft-07/schema#",
            "additionalProperties": True,
            "properties": {"header1": {"type": ["null", "string"]}, "header2": {"type": ["null", "string"]}},
            "type": "object",
        }
        expected_catalog = AirbyteCatalog(
            streams=[
                AirbyteStream(
                    name="a_stream_name", json_schema=expected_schema, supported_sync_modes=[SyncMode.full_refresh], is_resumable=False
                )
            ]
        )
        expected_message = AirbyteMessage(type=Type.CATALOG, catalog=expected_catalog)

        output = self._discover(self._config, expecting_exception=False)
        assert output.catalog == expected_message


class TestSourceDiscovery(GoogleSheetsBaseTest):
    @HttpMocker()
    def test_discover_return_expected_schema(self, http_mocker: HttpMocker) -> None:
        expected_schemas_properties = {
            _STREAM_NAME: {"age": {"type": ["null", "string"]}, "name": {"type": ["null", "string"]}},
            _B_STREAM_NAME: {"email": {"type": ["null", "string"]}, "name": {"type": ["null", "string"]}},
            _C_STREAM_NAME: {"address": {"type": ["null", "string"]}},
        }
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, "multiple_streams_schemas_meta", 200)
        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, f"multiple_streams_schemas_{_STREAM_NAME}_range", 200)
        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, f"multiple_streams_schemas_{_B_STREAM_NAME}_range", 200, _B_STREAM_NAME)
        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, f"multiple_streams_schemas_{_C_STREAM_NAME}_range", 200, _C_STREAM_NAME)

        expected_streams = []
        for expected_stream_name, expected_stream_properties in expected_schemas_properties.items():
            expected_schema = {
                "$schema": "https://json-schema.org/draft-07/schema#",
                "additionalProperties": True,
                "properties": expected_stream_properties,
                "type": "object",
            }
            expected_stream = AirbyteStream(
                name=expected_stream_name, json_schema=expected_schema, supported_sync_modes=[SyncMode.full_refresh], is_resumable=False
            )
            expected_streams.append(expected_stream)
        expected_catalog = AirbyteCatalog(streams=expected_streams)
        expected_message = AirbyteMessage(type=Type.CATALOG, catalog=expected_catalog)

        output = self._discover(self._config, expecting_exception=False)
        assert output.catalog == expected_message

    @HttpMocker()
    def test_discover_empty_column_return_expected_schema(self, http_mocker: HttpMocker) -> None:
        """
        The response from headers (first row) has columns "name | age | | address | address2"  so everything after empty cell will be
        discarded, in this case address and address2 shouldn't be part of the schema.
        """
        expected_schemas_properties = {
            _STREAM_NAME: {"name": {"type": ["null", "string"]}, "age": {"type": ["null", "string"]}},
        }
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, "discover_with_empty_column_spreadsheet_info_and_sheets", 200)
        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, f"discover_with_empty_column_get_sheet_first_row", 200)

        expected_streams = []
        for expected_stream_name, expected_stream_properties in expected_schemas_properties.items():
            expected_schema = {
                "$schema": "https://json-schema.org/draft-07/schema#",
                "additionalProperties": True,
                "properties": expected_stream_properties,
                "type": "object",
            }
            expected_stream = AirbyteStream(
                name=expected_stream_name, json_schema=expected_schema, supported_sync_modes=[SyncMode.full_refresh], is_resumable=False
            )
            expected_streams.append(expected_stream)
        expected_catalog = AirbyteCatalog(streams=expected_streams)
        expected_message = AirbyteMessage(type=Type.CATALOG, catalog=expected_catalog)

        output = self._discover(self._config, expecting_exception=False)
        assert output.catalog == expected_message

    @HttpMocker()
    def test_discover_with_duplicated_return_expected_schema(self, http_mocker: HttpMocker):
        """
        The response from headers (first row) has columns "header_1 | header_2 | header_2 | address | address2"  so header_2 will
        be ignored from schema.
        """
        expected_schema_properties = {
            "header_1": {"type": ["null", "string"]},
            "address": {"type": ["null", "string"]},
            "address2": {"type": ["null", "string"]},
        }
        test_file_base_name = "discover_duplicated_headers"
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, f"{test_file_base_name}_{GET_SPREADSHEET_INFO}")
        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, f"{test_file_base_name}_{GET_SHEETS_FIRST_ROW}")

        expected_schema = {
            "$schema": "https://json-schema.org/draft-07/schema#",
            "additionalProperties": True,
            "properties": expected_schema_properties,
            "type": "object",
        }
        expected_stream = AirbyteStream(
            name=_STREAM_NAME, json_schema=expected_schema, supported_sync_modes=[SyncMode.full_refresh], is_resumable=False
        )

        expected_catalog = AirbyteCatalog(streams=[expected_stream])
        expected_message = AirbyteMessage(type=Type.CATALOG, catalog=expected_catalog)
        expected_log_message = AirbyteMessage(
            type=Type.LOG,
            log=AirbyteLogMessage(level=Level.INFO, message="Duplicate headers found in sheet a_stream_name. Ignoring them: ['header_2']"),
        )

        output = self._discover(self._config, expecting_exception=False)

        assert output.catalog == expected_message
        assert output.logs[-1] == expected_log_message

    @HttpMocker()
    def test_discover_with_names_conversion(self, http_mocker: HttpMocker) -> None:
        # will convert '1 тест' to '_1_test and 'header2' to 'header_2'
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, "only_headers_meta", 200)
        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, "names_conversion_range", 200)
        expected_schema = {
            "$schema": "https://json-schema.org/draft-07/schema#",
            "additionalProperties": True,
            "properties": {"_1_test": {"type": ["null", "string"]}, "header_2": {"type": ["null", "string"]}},
            "type": "object",
        }
        expected_catalog = AirbyteCatalog(
            streams=[
                AirbyteStream(
                    name="a_stream_name", json_schema=expected_schema, supported_sync_modes=[SyncMode.full_refresh], is_resumable=False
                )
            ]
        )
        expected_message = AirbyteMessage(type=Type.CATALOG, catalog=expected_catalog)

        self._config["names_conversion"] = True
        output = self._discover(self._config, expecting_exception=False)
        assert output.catalog == expected_message

    @HttpMocker()
    def test_given_grid_sheet_type_without_rows_when_discover_then_ignore_stream(self, http_mocker: HttpMocker) -> None:
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, "no_rows_meta", 200)
        output = self._discover(self._config, expecting_exception=False)
        assert len(output.catalog.catalog.streams) == 0

    @HttpMocker()
    def test_given_not_grid_sheet_type_when_discover_then_ignore_stream(self, http_mocker: HttpMocker) -> None:
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, "non_grid_sheet_meta", 200)
        output = self._discover(self._config, expecting_exception=False)
        assert len(output.catalog.catalog.streams) == 0


class TestSourceRead(GoogleSheetsBaseTest):
    @HttpMocker()
    def test_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, "read_records_meta")
        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, "read_records_range")
        GoogleSheetsBaseTest.get_stream_data(http_mocker, "read_records_range_with_dimensions")
        first_property = "header_1"
        second_property = "header_2"
        configured_catalog = (
            CatalogBuilder()
            .with_stream(
                ConfiguredAirbyteStreamBuilder()
                .with_name(_STREAM_NAME)
                .with_json_schema(
                    {"properties": {first_property: {"type": ["null", "string"]}, second_property: {"type": ["null", "string"]}}}
                )
            )
            .build()
        )

        output = self._read(self._config, catalog=configured_catalog, expecting_exception=False)
        expected_records = [
            AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    emitted_at=ANY, stream=_STREAM_NAME, data={first_property: "value_11", second_property: "value_12"}
                ),
            ),
            AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    emitted_at=ANY, stream=_STREAM_NAME, data={first_property: "value_21", second_property: "value_22"}
                ),
            ),
        ]
        assert len(output.records) == 2
        assert output.records == expected_records

    @HttpMocker()
    def test_when_read_empty_column_then_return_records(self, http_mocker: HttpMocker) -> None:
        """
        The response from headers (first row) has columns "header_1 | header_2 | | address | address2"  so everything after empty cell will be
        discarded, in this case address and address2 shouldn't be part of the schema in records.
        """
        test_file_base_name = "read_with_empty_column"
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, f"{test_file_base_name}_{GET_SPREADSHEET_INFO}")
        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, f"{test_file_base_name}_{GET_SHEETS_FIRST_ROW}")
        GoogleSheetsBaseTest.get_stream_data(http_mocker, f"{test_file_base_name}_{GET_STREAM_DATA}")
        first_property = "header_1"
        second_property = "header_2"
        configured_catalog = (
            CatalogBuilder()
            .with_stream(
                ConfiguredAirbyteStreamBuilder()
                .with_name(_STREAM_NAME)
                .with_json_schema(
                    {"properties": {first_property: {"type": ["null", "string"]}, second_property: {"type": ["null", "string"]}}}
                )
            )
            .build()
        )

        output = self._read(self._config, catalog=configured_catalog, expecting_exception=False)
        expected_records = [
            AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    emitted_at=ANY, stream=_STREAM_NAME, data={first_property: "value_11", second_property: "value_12"}
                ),
            ),
            AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    emitted_at=ANY, stream=_STREAM_NAME, data={first_property: "value_21", second_property: "value_22"}
                ),
            ),
        ]
        assert len(output.records) == 2
        assert output.records == expected_records

    @HttpMocker()
    def test_when_read_with_duplicated_headers_then_return_records(self, http_mocker: HttpMocker):
        """ "
        header_2 will be ignored from records as column is duplicated.

        header_1	header_2	header_2	address	        address2
        value_11	value_12	value_13	main	        main st
        value_21	value_22	value_23	washington 3	colonial

        It will correctly match row values and field/column names in read records.
        """
        test_file_base_name = "read_duplicated_headers"
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, f"{test_file_base_name}_{GET_SPREADSHEET_INFO}")
        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, f"{test_file_base_name}_{GET_SHEETS_FIRST_ROW}")
        GoogleSheetsBaseTest.get_stream_data(http_mocker, f"{test_file_base_name}_{GET_STREAM_DATA}")
        first_property = "header_1"
        second_property = "address"
        third_property = "address2"
        configured_catalog = (
            CatalogBuilder()
            .with_stream(
                ConfiguredAirbyteStreamBuilder()
                .with_name(_STREAM_NAME)
                .with_json_schema(
                    {
                        "properties": {
                            first_property: {"type": ["null", "string"]},
                            second_property: {"type": ["null", "string"]},
                            third_property: {"type": ["null", "string"]},
                        }
                    }
                )
            )
            .build()
        )

        output = self._read(self._config, catalog=configured_catalog, expecting_exception=False)
        expected_records = [
            AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    emitted_at=ANY,
                    stream=_STREAM_NAME,
                    data={first_property: "value_11", second_property: "main", third_property: "main st"},
                ),
            ),
            AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    emitted_at=ANY,
                    stream=_STREAM_NAME,
                    data={first_property: "value_21", second_property: "washington 3", third_property: "colonial"},
                ),
            ),
        ]
        assert len(output.records) == 2
        assert output.records == expected_records

    @HttpMocker()
    def test_when_empty_rows_then_return_records(self, http_mocker: HttpMocker):
        """ "
        There are a few empty rows in the response that we shuld ignore

        e.g.
        id	name	            normalized_name
        7	Children	        children
        12	Mechanical Santa	mechanical santa
        13	Tattoo Man	        tattoo man
        16	DOCTOR ZITSOFSKY	doctor zitsofsky


        20	Students	        students

        There are two empty rows between id 16 and 20 that we will not be present in read records
        """
        test_file_base_name = "read_empty_rows"
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, f"{test_file_base_name}_{GET_SPREADSHEET_INFO}")
        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, f"{test_file_base_name}_{GET_SHEETS_FIRST_ROW}")
        GoogleSheetsBaseTest.get_stream_data(http_mocker, f"{test_file_base_name}_{GET_STREAM_DATA}")
        expected_properties = ["id", "name", "normalized_name"]
        catalog_properties = {}
        for property in expected_properties:
            catalog_properties[property] = {"type": ["null", "string"]}
        configured_catalog = (
            CatalogBuilder()
            .with_stream(ConfiguredAirbyteStreamBuilder().with_name(_STREAM_NAME).with_json_schema({"properties": catalog_properties}))
            .build()
        )

        records_in_response = find_template(f"{test_file_base_name}_{GET_STREAM_DATA}", __file__)
        empty_row_count = 0
        expected_rows_found = 23
        expected_empty_rows = 7
        expected_records = []

        for row in records_in_response["valueRanges"][0]["values"]:
            if row:
                expected_records += [
                    AirbyteMessage(
                        type=Type.RECORD,
                        record=AirbyteRecordMessage(
                            emitted_at=ANY,
                            stream=_STREAM_NAME,
                            data={expected_property: row_value for expected_property, row_value in zip(expected_properties, row)},
                        ),
                    )
                ]
            else:
                empty_row_count += 1
        assert empty_row_count == expected_empty_rows
        assert len(expected_records) == expected_rows_found
        output = self._read(self._config, catalog=configured_catalog, expecting_exception=False)
        assert len(output.records) == expected_rows_found
        assert output.records == expected_records

    @HttpMocker()
    def test_when_read_by_batches_make_expected_requests(self, http_mocker: HttpMocker):
        test_file_base_name = "read_by_batches"
        batch_size = 10
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, f"{test_file_base_name}_{GET_SPREADSHEET_INFO}")
        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, f"{test_file_base_name}_{GET_SHEETS_FIRST_ROW}")
        start_range = 2
        for range_file_postfix in ("first_batch", "second_batch", "third_batch", "fourth_batch", "fifth_batch"):
            end_range = start_range + batch_size
            request_range = (start_range, end_range)
            GoogleSheetsBaseTest.get_stream_data(
                http_mocker, data_response_file=f"{test_file_base_name}_{GET_STREAM_DATA}_{range_file_postfix}", request_range=request_range
            )
            start_range += batch_size + 1
        catalog_properties = {}
        for expected_property in ["id", "name", "normalized_name"]:
            catalog_properties[expected_property] = {"type": ["null", "string"]}
        configured_catalog = (
            CatalogBuilder()
            .with_stream(ConfiguredAirbyteStreamBuilder().with_name(_STREAM_NAME).with_json_schema({"properties": catalog_properties}))
            .build()
        )
        self._config["batch_size"] = batch_size
        output = self._read(self._config, catalog=configured_catalog, expecting_exception=False)
        assert len(output.records) > 0

    @HttpMocker()
    def test_when_read_then_return_records_with_name_conversion(self, http_mocker: HttpMocker) -> None:
        # will convert '1 тест' to '_1_test and 'header2' to 'header_2'
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, "read_records_meta")
        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, "names_conversion_range")
        GoogleSheetsBaseTest.get_stream_data(http_mocker, "read_records_range_with_dimensions")

        first_expected_converted_property = "_1_test"
        second_expected_converted_property = "header_2"
        configured_catalog = (
            CatalogBuilder()
            .with_stream(
                ConfiguredAirbyteStreamBuilder()
                .with_name(_STREAM_NAME)
                .with_json_schema(
                    {
                        "properties": {
                            first_expected_converted_property: {"type": ["null", "string"]},
                            second_expected_converted_property: {"type": ["null", "string"]},
                        }
                    }
                )
            )
            .build()
        )

        self._config["names_conversion"] = True
        output = self._read(self._config, catalog=configured_catalog, expecting_exception=False)
        expected_records = [
            AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    emitted_at=ANY,
                    stream=_STREAM_NAME,
                    data={first_expected_converted_property: "value_11", second_expected_converted_property: "value_12"},
                ),
            ),
            AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    emitted_at=ANY,
                    stream=_STREAM_NAME,
                    data={first_expected_converted_property: "value_21", second_expected_converted_property: "value_22"},
                ),
            ),
        ]
        assert len(output.records) == 2
        assert output.records == expected_records

    @HttpMocker()
    def test_when_read_multiple_streams_return_records(self, http_mocker: HttpMocker) -> None:
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, "multiple_streams_schemas_meta", 200)

        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, f"multiple_streams_schemas_{_STREAM_NAME}_range", 200)
        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, f"multiple_streams_schemas_{_B_STREAM_NAME}_range", 200, _B_STREAM_NAME)
        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, f"multiple_streams_schemas_{_C_STREAM_NAME}_range", 200, _C_STREAM_NAME)

        GoogleSheetsBaseTest.get_stream_data(http_mocker, f"multiple_streams_schemas_{_STREAM_NAME}_range_2")
        GoogleSheetsBaseTest.get_stream_data(http_mocker, f"multiple_streams_schemas_{_B_STREAM_NAME}_range_2", stream_name=_B_STREAM_NAME)
        GoogleSheetsBaseTest.get_stream_data(http_mocker, f"multiple_streams_schemas_{_C_STREAM_NAME}_range_2", stream_name=_C_STREAM_NAME)

        configured_catalog = (
            CatalogBuilder()
            .with_stream(
                ConfiguredAirbyteStreamBuilder()
                .with_name(_STREAM_NAME)
                .with_json_schema({"properties": {"age": {"type": "string"}, "name": {"type": "string"}}})
            )
            .with_stream(
                ConfiguredAirbyteStreamBuilder()
                .with_name(_B_STREAM_NAME)
                .with_json_schema({"properties": {"email": {"type": "string"}, "name": {"type": "string"}}})
            )
            .with_stream(
                ConfiguredAirbyteStreamBuilder().with_name(_C_STREAM_NAME).with_json_schema({"properties": {"address": {"type": "string"}}})
            )
            .build()
        )

        output = self._read(self._config, catalog=configured_catalog, expecting_exception=False)
        assert len(output.records) == 9

        assert len(output.state_messages) == 3
        state_messages_streams = []
        for state_message in output.state_messages:
            state_messages_streams.append(state_message.state.stream.stream_descriptor.name)

        assert _STREAM_NAME in state_messages_streams
        assert _B_STREAM_NAME in state_messages_streams
        assert _C_STREAM_NAME in state_messages_streams

        expected_messages = []
        for current_stream in [_STREAM_NAME, _B_STREAM_NAME, _C_STREAM_NAME]:
            for current_status in [AirbyteStreamStatus.COMPLETE, AirbyteStreamStatus.RUNNING, AirbyteStreamStatus.STARTED]:
                stream_descriptor = StreamDescriptor(name=current_stream, namespace=None)
                stream_status = AirbyteStreamStatusTraceMessage(status=current_status, stream_descriptor=stream_descriptor)
                airbyte_trace_message = AirbyteTraceMessage(type=TraceType.STREAM_STATUS, emitted_at=ANY, stream_status=stream_status)
                airbyte_message = AirbyteMessage(type=Type.TRACE, trace=airbyte_trace_message)
                expected_messages.append(airbyte_message)
        assert len(output.trace_messages) == len(expected_messages)
        for message in expected_messages:
            assert message in output.trace_messages

    @HttpMocker()
    def test_when_read_single_stream_with_multiple_streams_available_return_records_of_requested_stream(
        self, http_mocker: HttpMocker
    ) -> None:
        """ "
        Source has multiple sheets/stream but configured catalog will just request data for one sheet/stream
        then we just get records for that stream.
        """
        file_name_base = "multiple_streams_schemas"
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, f"{file_name_base}_meta", 200)

        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, f"{file_name_base}_{_STREAM_NAME}_range", 200)
        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, f"{file_name_base}_{_B_STREAM_NAME}_range", 200, _B_STREAM_NAME)
        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, f"{file_name_base}_{_C_STREAM_NAME}_range", 200, _C_STREAM_NAME)

        GoogleSheetsBaseTest.get_stream_data(http_mocker, f"{file_name_base}_{_B_STREAM_NAME}_range_2", stream_name=_B_STREAM_NAME)

        configured_catalog = (
            CatalogBuilder()
            .with_stream(
                ConfiguredAirbyteStreamBuilder()
                .with_name(_B_STREAM_NAME)
                .with_json_schema({"properties": {"email": {"type": "string"}, "name": {"type": "string"}}})
            )
            .build()
        )

        output = self._read(self._config, catalog=configured_catalog, expecting_exception=False)
        assert len(output.records) == 2

        assert len(output.state_messages) == 1
        state_messages_streams = []
        for state_message in output.state_messages:
            state_messages_streams.append(state_message.state.stream.stream_descriptor.name)

        assert _STREAM_NAME not in state_messages_streams
        assert _B_STREAM_NAME in state_messages_streams
        assert _C_STREAM_NAME not in state_messages_streams

        expected_messages = []
        for current_stream in [_B_STREAM_NAME]:
            for current_status in [AirbyteStreamStatus.COMPLETE, AirbyteStreamStatus.RUNNING, AirbyteStreamStatus.STARTED]:
                stream_descriptor = StreamDescriptor(name=current_stream, namespace=None)
                stream_status = AirbyteStreamStatusTraceMessage(status=current_status, stream_descriptor=stream_descriptor)
                airbyte_trace_message = AirbyteTraceMessage(type=TraceType.STREAM_STATUS, emitted_at=ANY, stream_status=stream_status)
                airbyte_message = AirbyteMessage(type=Type.TRACE, trace=airbyte_trace_message)
                expected_messages.append(airbyte_message)
        assert len(output.trace_messages) == len(expected_messages)
        for message in expected_messages:
            assert message in output.trace_messages

    @HttpMocker()
    def test_when_read_stream_is_not_available_then_is_marked_incomplete(self, http_mocker: HttpMocker) -> None:
        """
        Configured catalog will include a streams that is not available in first row response, so it will be marked as incomplete.
        """
        base_file_name = "multiple_streams_schemas"
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, f"{base_file_name}_meta", 200)

        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, f"{base_file_name}_{_STREAM_NAME}_range", 200)
        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, f"{base_file_name}_{_B_STREAM_NAME}_range", 200, _B_STREAM_NAME)
        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, f"{base_file_name}_{_C_STREAM_NAME}_range", 200, _C_STREAM_NAME)

        GoogleSheetsBaseTest.get_stream_data(http_mocker, f"{base_file_name}_{_STREAM_NAME}_range_2")
        GoogleSheetsBaseTest.get_stream_data(http_mocker, f"{base_file_name}_{_B_STREAM_NAME}_range_2", stream_name=_B_STREAM_NAME)

        unavailable_stream = "unavailable_stream"
        configured_catalog = (
            CatalogBuilder()
            .with_stream(
                ConfiguredAirbyteStreamBuilder()
                .with_name(_STREAM_NAME)
                .with_json_schema({"properties": {"age": {"type": "string"}, "name": {"type": "string"}}})
            )
            .with_stream(
                ConfiguredAirbyteStreamBuilder()
                .with_name(_B_STREAM_NAME)
                .with_json_schema({"properties": {"email": {"type": "string"}, "name": {"type": "string"}}})
            )
            .with_stream(
                ConfiguredAirbyteStreamBuilder()
                .with_name(unavailable_stream)
                .with_json_schema({"properties": {"address": {"type": "string"}}})
            )
            .build()
        )

        output = self._read(self._config, catalog=configured_catalog, expecting_exception=False)
        a_and_b_stream_records_count = 5
        assert len(output.records) == a_and_b_stream_records_count

        catalog_available_streams = [_STREAM_NAME, _B_STREAM_NAME]
        assert len(output.state_messages) == len(catalog_available_streams)
        state_messages_streams = []
        for state_message in output.state_messages:
            state_messages_streams.append(state_message.state.stream.stream_descriptor.name)

        assert _STREAM_NAME in state_messages_streams
        assert _B_STREAM_NAME in state_messages_streams

        expected_messages = []
        for current_stream in catalog_available_streams:
            for current_status in [AirbyteStreamStatus.COMPLETE, AirbyteStreamStatus.RUNNING, AirbyteStreamStatus.STARTED]:
                stream_descriptor = StreamDescriptor(name=current_stream, namespace=None)
                stream_status = AirbyteStreamStatusTraceMessage(status=current_status, stream_descriptor=stream_descriptor)
                airbyte_trace_message = AirbyteTraceMessage(type=TraceType.STREAM_STATUS, emitted_at=ANY, stream_status=stream_status)
                airbyte_message = AirbyteMessage(type=Type.TRACE, trace=airbyte_trace_message)
                expected_messages.append(airbyte_message)

        stream_descriptor = StreamDescriptor(name=unavailable_stream, namespace=None)
        stream_status = AirbyteStreamStatusTraceMessage(status=AirbyteStreamStatus.INCOMPLETE, stream_descriptor=stream_descriptor)
        airbyte_trace_message = AirbyteTraceMessage(type=TraceType.STREAM_STATUS, emitted_at=ANY, stream_status=stream_status)
        airbyte_message_incomplete_stream = AirbyteMessage(type=Type.TRACE, trace=airbyte_trace_message)
        expected_messages.append(airbyte_message_incomplete_stream)
        assert len(output.trace_messages) == len(expected_messages)
        for message in expected_messages:
            assert message in output.trace_messages

    @HttpMocker()
    def test_when_read_then_status_and_state_messages_emitted(self, http_mocker: HttpMocker) -> None:
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, "read_records_meta_2", 200)
        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, "read_records_range_2", 200)
        GoogleSheetsBaseTest.get_stream_data(http_mocker, "read_records_range_with_dimensions_2")

        configured_catalog = (
            CatalogBuilder()
            .with_stream(
                ConfiguredAirbyteStreamBuilder()
                .with_name(_STREAM_NAME)
                .with_json_schema({"properties": {"header_1": {"type": ["null", "string"]}, "header_2": {"type": ["null", "string"]}}})
            )
            .build()
        )

        output = self._read(self._config, catalog=configured_catalog, expecting_exception=False)
        assert len(output.records) == 5
        assert output.state_messages[0].state.stream.stream_state == AirbyteStateBlob(__ab_no_cursor_state_message=True)
        assert output.state_messages[0].state.stream.stream_descriptor.name == _STREAM_NAME

        assert output.trace_messages[0].trace.stream_status.status == AirbyteStreamStatus.STARTED
        assert output.trace_messages[1].trace.stream_status.status == AirbyteStreamStatus.RUNNING
        assert output.trace_messages[2].trace.stream_status.status == AirbyteStreamStatus.COMPLETE

    @HttpMocker()
    def test_read_empty_sheet(self, http_mocker: HttpMocker) -> None:
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, "read_records_meta", 200)
        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, "read_records_range_empty", 200)

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
            f"Unable to read the schema of sheet. Error: Unexpected return result: Sheet was expected to contain data on exactly 1 sheet."
        )
        assert output.errors[0].trace.error.message == expected_message

    @HttpMocker()
    def test_read_expected_data_on_1_sheet(self, http_mocker: HttpMocker) -> None:
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, "read_records_meta", 200)
        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, "read_records_range_with_unexpected_extra_sheet", 200)

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
            f"Unable to read the schema of sheet. Error: Unexpected return result: Sheet was expected to contain data on exactly 1 sheet."
        )
        assert output.errors[0].trace.error.message == expected_message

    def _make_read_with_spreadsheet(self, http_mocker: HttpMocker, spreadsheet_id_to_mock: str, spreadsheet_id_for_config: str):
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, "read_records_meta", spreadsheet_id=spreadsheet_id_to_mock)
        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, "read_records_range", spreadsheet_id=spreadsheet_id_to_mock)
        GoogleSheetsBaseTest.get_stream_data(http_mocker, "read_records_range_with_dimensions", spreadsheet_id=spreadsheet_id_to_mock)
        first_property = "header_1"
        second_property = "header_2"
        configured_catalog = (
            CatalogBuilder()
            .with_stream(
                ConfiguredAirbyteStreamBuilder()
                .with_name(_STREAM_NAME)
                .with_json_schema(
                    {"properties": {first_property: {"type": ["null", "string"]}, second_property: {"type": ["null", "string"]}}}
                )
            )
            .build()
        )

        config_with_other_spreadsheet_format = deepcopy(self._config)
        config_with_other_spreadsheet_format["spreadsheet_id"] = spreadsheet_id_for_config
        output = self._read(config_with_other_spreadsheet_format, catalog=configured_catalog, expecting_exception=False)
        expected_records = [
            AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    emitted_at=ANY, stream=_STREAM_NAME, data={first_property: "value_11", second_property: "value_12"}
                ),
            ),
            AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    emitted_at=ANY, stream=_STREAM_NAME, data={first_property: "value_21", second_property: "value_22"}
                ),
            ),
        ]
        assert len(output.records) == 2
        assert output.records == expected_records

    @HttpMocker()
    def test_spreadsheet_url_with_edit_and_gid_in_path(self, http_mocker: HttpMocker) -> None:
        spreadsheet_id_to_mock = "18vWlVH8BfjGegwY_GdV1B_cPP9re66xI8uJK25dtY9Q"
        spreadsheet_id_for_config = (
            "https://docs.google.com/spreadsheets/d/18vWlVH8BfjGegwY_GdV1B_cPP9re66xI8uJK25dtY9Q/edit#gid=1820065035"
        )
        self._make_read_with_spreadsheet(
            http_mocker=http_mocker, spreadsheet_id_to_mock=spreadsheet_id_to_mock, spreadsheet_id_for_config=spreadsheet_id_for_config
        )

    @HttpMocker()
    def test_spreadsheet_url_with_edit_in_path(self, http_mocker: HttpMocker) -> None:
        spreadsheet_id_to_mock = "18vWlVH8BfjGa-gwYGdV1BjcPP9re66xI8uJK25dtY9Q"
        spreadsheet_id_for_config = "https://docs.google.com/spreadsheets/d/18vWlVH8BfjGa-gwYGdV1BjcPP9re66xI8uJK25dtY9Q/edit"
        self._make_read_with_spreadsheet(
            http_mocker=http_mocker, spreadsheet_id_to_mock=spreadsheet_id_to_mock, spreadsheet_id_for_config=spreadsheet_id_for_config
        )

    @HttpMocker()
    def test_spreadsheet_path(self, http_mocker: HttpMocker) -> None:
        spreadsheet_id_to_mock = "18vWlVH8BfjGegwY_GdV1BjcPP9re_6xI8uJ-25dtY9Q"
        spreadsheet_id_for_config = "https://docs.google.com/spreadsheets/d/18vWlVH8BfjGegwY_GdV1BjcPP9re_6xI8uJ-25dtY9Q/"
        self._make_read_with_spreadsheet(
            http_mocker=http_mocker, spreadsheet_id_to_mock=spreadsheet_id_to_mock, spreadsheet_id_for_config=spreadsheet_id_for_config
        )

    @HttpMocker()
    def test_spreadsheet_url_with_pound_in_path(self, http_mocker: HttpMocker) -> None:
        spreadsheet_id_to_mock = "18vWlVH8BfjGegwY_GdV1BjcPP9re_6xI8uJ-25dtY9Q"
        spreadsheet_id_for_config = "https://docs.google.com/spreadsheets/d/18vWlVH8BfjGegwY_GdV1BjcPP9re_6xI8uJ-25dtY9Q/#"
        self._make_read_with_spreadsheet(
            http_mocker=http_mocker, spreadsheet_id_to_mock=spreadsheet_id_to_mock, spreadsheet_id_for_config=spreadsheet_id_for_config
        )

    @HttpMocker()
    def test_spreadsheet_id(self, http_mocker: HttpMocker) -> None:
        spreadsheet_id_to_mock = "18vWlVH8BfjGegwY_GdV1BjcPP9re66xI8uJK25dtY9Q"
        spreadsheet_id_for_config = "18vWlVH8BfjGegwY_GdV1BjcPP9re66xI8uJK25dtY9Q"
        self._make_read_with_spreadsheet(
            http_mocker=http_mocker, spreadsheet_id_to_mock=spreadsheet_id_to_mock, spreadsheet_id_for_config=spreadsheet_id_for_config
        )

    @pytest.mark.skip("Pending to do")
    def test_for_increase_batch_size_when_rate_limit(self):
        pass
