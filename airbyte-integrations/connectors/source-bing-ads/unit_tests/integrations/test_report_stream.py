# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from pathlib import Path
from typing import Any, Optional

import pendulum
from base_test import BaseTest
from bingads.v13.reporting.reporting_service_manager import ReportingServiceManager
from config_builder import ConfigBuilder

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker


class TestReportStream(BaseTest):
    start_date = "2024-01-01"

    @property
    def service_manager(self) -> ReportingServiceManager:
        return ReportingServiceManager

    @property
    def _config(self) -> dict[str, Any]:
        return ConfigBuilder().with_reports_start_date(self.start_date).build()

    def _download_file(self, file: Optional[str] = None) -> Path:
        """
        Returns path to temporary file of downloaded data that will be use in read.
        Base file should be named as {file_name}.csv in resource/response folder.
        """
        if file:
            path_to_tmp_file = Path(__file__).parent.parent / f"resource/response/{file}.csv"
            return path_to_tmp_file
        return Path(__file__).parent.parent / "resource/response/non-existing-file.csv"


class TestSuiteReportStream(TestReportStream):
    stream_name: Optional[str] = None
    report_file: str
    records_number: int
    second_read_records_number: Optional[int] = None
    state_file: str
    incremental_report_file: str
    first_read_state: dict
    second_read_state: dict
    transform_field: str = "AccountId"
    account_id: str = "180535609"
    cursor_field = "TimePeriod"

    def setUp(self):
        if not self.stream_name:
            self.skipTest("Skipping TestSuiteReportStream")

    @HttpMocker()
    def test_return_records_from_given_csv_file(self, http_mocker: HttpMocker):
        self.auth_client(http_mocker)
        output, _ = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, self.report_file)
        assert len(output.records) == self.records_number

    @HttpMocker()
    def test_transform_records_from_given_csv_file(self, http_mocker: HttpMocker):
        self.auth_client(http_mocker)
        output, _ = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, self.report_file)

        assert len(output.records) == self.records_number
        for record in output.records:
            assert self.transform_field in record.record.data.keys()

    @HttpMocker()
    def test_incremental_read_returns_records(self, http_mocker: HttpMocker):
        self.auth_client(http_mocker)
        output, _ = self.read_stream(self.stream_name, SyncMode.incremental, self._config, self.report_file)
        assert len(output.records) == self.records_number
        assert output.most_recent_state.stream_state.__dict__ == self.first_read_state

    @HttpMocker()
    def test_incremental_read_with_state_returns_records(self, http_mocker: HttpMocker):
        state = self._state(self.state_file, self.stream_name)
        self.auth_client(http_mocker)
        output, service_call_mock = self.read_stream(
            self.stream_name, SyncMode.incremental, self._config, self.incremental_report_file, state
        )
        if not self.second_read_records_number:
            assert len(output.records) == self.records_number
        else:
            assert len(output.records) == self.second_read_records_number

        actual_cursor = output.most_recent_state.stream_state.__dict__.get(self.account_id)
        expected_cursor = self.second_read_state.get(self.account_id)
        assert actual_cursor == expected_cursor

        provided_state = state[0].stream.stream_state.__dict__[self.account_id][self.cursor_field]
        # gets ReportDownloadParams object
        request_start_date = service_call_mock.call_args.args[0].report_request.Time.CustomDateRangeStart
        year = request_start_date.Year
        month = request_start_date.Month
        day = request_start_date.Day
        assert pendulum.DateTime(year, month, day, tzinfo=pendulum.UTC) == pendulum.parse(provided_state)
