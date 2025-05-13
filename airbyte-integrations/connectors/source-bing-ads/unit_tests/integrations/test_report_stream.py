# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
import re
from pathlib import Path
from typing import Any, Optional

import pendulum
from base_test import BaseTest
from bingads.v13.reporting.reporting_service_manager import ReportingServiceManager
from config_builder import ConfigBuilder
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode


# TODO: Remove this list when all streams are migrated to the manifest
MIGRATED_STREAMS = [
    "ad_performance_report_hourly",
    "ad_performance_report_daily",
    "ad_performance_report_weekly",
    "ad_performance_report_monthly",
]


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
    report_file_with_records_further_start_date: Optional[str] = None
    records_number: int
    second_read_records_number: Optional[int] = None
    state_file: str
    state_file_after_migration: Optional[str] = None
    state_file_after_migration_with_cursor_further_config_start_date: Optional[str] = None
    incremental_report_file: str
    incremental_report_file_with_records_further_cursor: Optional[str] = None
    first_read_state: dict
    first_read_state_for_records_further_start_date: Optional[dict] = None
    second_read_state: dict
    second_read_state_for_records_before_start_date: Optional[dict] = None
    second_read_state_for_records_further_start_date: Optional[dict] = None
    transform_field: str = "AccountId"
    account_id: str = "180535609"
    cursor_field = "TimePeriod"

    def setUp(self):
        super().setUp()
        if not self.stream_name:
            self.skipTest("Skipping TestSuiteReportStream")

    @freeze_time("2024-05-06")
    def test_return_records_from_given_csv_file(self):
        output, _ = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, self.report_file)
        assert len(output.records) == self.records_number

    @freeze_time("2024-05-06")
    def test_transform_records_from_given_csv_file(self):
        output, _ = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, self.report_file)

        assert len(output.records) == self.records_number
        for record in output.records:
            assert self.transform_field in record.record.data.keys()

    @freeze_time("2024-05-06")
    def test_incremental_read_returns_records(self):
        output, _ = self.read_stream(self.stream_name, SyncMode.incremental, self._config, self.report_file)
        assert len(output.records) == self.records_number
        assert output.most_recent_state.stream_state.__dict__ == self.first_read_state

    @freeze_time("2024-05-06")
    def test_incremental_read_returns_records_further_config_start_date(self):
        if self.stream_name not in MIGRATED_STREAMS:
            self.skipTest("Skipping test_incremental_read_returns_records for NOT migrated to manifest streams")
        if not self.report_file_with_records_further_start_date or not self.first_read_state_for_records_further_start_date:
            assert False, "test_incremental_read_returns_records_further_config_start_date is not correctly set"
        output, _ = self.read_stream(self.stream_name, SyncMode.incremental, self._config, self.report_file_with_records_further_start_date)
        assert len(output.records) == self.records_number
        assert output.most_recent_state.stream_state.__dict__ == self.first_read_state_for_records_further_start_date

    @freeze_time("2024-05-06")
    def test_incremental_read_with_state_returns_records(self):
        if self.stream_name in MIGRATED_STREAMS:
            self.skipTest("Skipping for migrated to manifest streams")
        state = self._state(self.state_file, self.stream_name)
        output, service_call_mock = self.read_stream(
            self.stream_name, SyncMode.incremental, self._config, self.incremental_report_file, state
        )
        if not self.second_read_records_number:
            assert len(output.records) == self.records_number
        else:
            assert len(output.records) == self.second_read_records_number

        most_recent_state = output.most_recent_state.stream_state.__dict__
        actual_cursor = most_recent_state.get(self.account_id)
        expected_cursor = self.second_read_state.get(self.account_id)
        assert actual_cursor == expected_cursor

        provided_state = state[0].stream.stream_state.__dict__[self.account_id][self.cursor_field]
        # gets ReportDownloadParams object
        request_start_date = service_call_mock.call_args.args[0].report_request.Time.CustomDateRangeStart
        year = request_start_date.Year
        month = request_start_date.Month
        day = request_start_date.Day
        assert pendulum.DateTime(year, month, day, tzinfo=pendulum.UTC) == pendulum.parse(provided_state)

    @freeze_time("2024-05-06")
    def test_incremental_read_with_state_returns_records_after_migration(self):
        """
        For this test the records are all with TimePeriod behind the config start date and the state TimePeriod cursor.
        """
        if self.stream_name not in MIGRATED_STREAMS:
            self.skipTest("Skipping for NOT migrated to manifest streams")
        state = self._state(self.state_file_after_migration, self.stream_name)
        output, service_call_mock = self.read_stream(
            self.stream_name, SyncMode.incremental, self._config, self.incremental_report_file, state
        )
        if not self.second_read_records_number:
            assert len(output.records) == self.records_number
        else:
            assert len(output.records) == self.second_read_records_number

        actual_cursor = None
        for state in output.most_recent_state.stream_state.states:
            if state["partition"]["account_id"] == int(self.account_id):
                actual_cursor = state["cursor"]
        expected_state = self.second_read_state_for_records_before_start_date
        expected_cursor = None
        for state in expected_state["states"]:
            if state["partition"]["account_id"] == int(self.account_id):
                expected_cursor = state["cursor"]
        if not expected_cursor or not actual_cursor:
            assert False, f"Expected state is empty for account_id: {self.account_id}"
        assert actual_cursor == expected_cursor

    @freeze_time("2024-05-08")
    def test_incremental_read_with_state_returns_records_after_migration_with_records_further_state_cursor(self):
        """
        For this test we get records with TimePeriod further the config start date and the state TimePeriod cursor.
        The provide state is taken from a previous run; with stream manifest; so, is in the new state format, and
        where the resultant cursor was further the config start date.
        So we validate that the cursor in the output.most_recent_state is moved to the value of the latest record read.
        The state format before migration IS NOT involved in this test.
        """
        if self.stream_name not in MIGRATED_STREAMS:
            self.skipTest("Skipping for NOT migrated to manifest streams")
        provided_state = self._state(self.state_file_after_migration_with_cursor_further_config_start_date, self.stream_name)
        output, service_call_mock = self.read_stream(
            self.stream_name, SyncMode.incremental, self._config, self.incremental_report_file_with_records_further_cursor, provided_state
        )
        if not self.second_read_records_number:
            assert len(output.records) == self.records_number
        else:
            assert len(output.records) == self.second_read_records_number

        actual_cursor = None
        for state in output.most_recent_state.stream_state.states:
            if state["partition"]["account_id"] == int(self.account_id):
                actual_cursor = state["cursor"]
        expected_state = self.second_read_state_for_records_further_start_date
        expected_cursor = None
        for state in expected_state["states"]:
            if state["partition"]["account_id"] == int(self.account_id):
                expected_cursor = state["cursor"]
        if not expected_cursor or not actual_cursor:
            assert False, f"Expected state is empty for account_id: {self.account_id}"
        assert actual_cursor == expected_cursor

        # Let's check in the logs what was the start_time and end_time values of the Job
        job_completed_log = ""
        for current_log in output.logs:
            if "The following jobs for stream slice" in current_log.log.message:
                job_completed_log = current_log.log.message
                break

        if not job_completed_log:
            assert False, "Job completed log is empty"

        # Regex patterns to match start_time and end_time values
        start_time_pattern = re.compile(r"'start_time': '([^']+)'")
        end_time_pattern = re.compile(r"'end_time': '([^']+)'")

        # Extract values
        start_time_match = start_time_pattern.search(job_completed_log)
        end_time_match = end_time_pattern.search(job_completed_log)

        job_start_time = start_time_match.group(1) if start_time_match else None
        job_end_time = end_time_match.group(1) if end_time_match else None

        # here the provided state cursor is further the config start date
        assert provided_state[0].stream.stream_state.state[self.cursor_field] == "2024-05-06T07:00:00+0000"
        # here the cursor in the output.most_recent_state moved to the value of the latest record read
        assert actual_cursor[self.cursor_field] == "2024-05-07T01:00:00+0000"
        # todo: FIXME, start_time of the job is the config start date rather the cursor state start date in the provided state
        # I am not sure if it is a bug or not
        assert job_start_time == "2024-01-01T00:00:00+0000"
        assert job_end_time == "2024-05-08T00:00:00+0000"
        # todo: remove hardcoded asserts after figure out the issue with job start_time

    # todo: We need to add a test to validate that the previous state format can be reused during first sync after migration and that
    # consequently we can create jobs with new state format, but need to figure out if above test statement is correct or not
