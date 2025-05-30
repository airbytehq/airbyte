# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from copy import deepcopy
from pathlib import Path
from typing import Any, Optional

import pendulum
from base_test import BaseTest
from bingads.v13.reporting.reporting_service_manager import ReportingServiceManager
from config_builder import ConfigBuilder

from airbyte_cdk.models import SyncMode


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
        super().setUp()
        if not self.stream_name:
            self.skipTest("Skipping TestSuiteReportStream")

    def test_return_records_from_given_csv_file(self):
        output, _ = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, self.report_file)
        assert len(output.records) == self.records_number

    def test_transform_records_from_given_csv_file(self):
        output, _ = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, self.report_file)

        assert len(output.records) == self.records_number
        for record in output.records:
            assert self.transform_field in record.record.data.keys()

    def test_incremental_read_returns_records(self):
        output, _ = self.read_stream(self.stream_name, SyncMode.incremental, self._config, self.report_file)
        assert len(output.records) == self.records_number
        assert output.most_recent_state.stream_state.__dict__ == self.first_read_state

    def test_incremental_read_with_state_returns_records(self):
        state = self._state(self.state_file, self.stream_name)
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

    def test_incremental_read_with_state_and_no_start_date_returns_records_once(self):
        """
        Test that incremental read with state and no start date in config returns records only once.
        We observed that if the start date is not provided in the config, and we don't parse correctly the account_id
        from the state, the incremental read returns records multiple times as we yield the default_time_periods
        for no start date scenario.
        """
        state = self._state(self.state_file, self.stream_name)
        config = deepcopy(self._config)
        del config["reports_start_date"]  # Simulate no start date in config
        output, service_call_mock = self.read_stream(self.stream_name, SyncMode.incremental, config, self.incremental_report_file, state)
        if not self.second_read_records_number:
            assert len(output.records) == self.records_number
        else:
            assert len(output.records) == self.second_read_records_number
