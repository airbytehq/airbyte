# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from pathlib import Path
from typing import Any, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from base_test import BaseTest
from bingads.v13.reporting.reporting_service_manager import ReportingServiceManager
from config_builder import ConfigBuilder


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
        Base file should be named as {file_name}.cvs in resource/response folder.
        """
        if file:
            path_to_tmp_file = Path(__file__).parent.parent / f"resource/response/{file}.csv"
            return path_to_tmp_file
        return Path(__file__).parent.parent / "resource/response/non-existing-file.csv"


class TestSuiteReportStream(TestReportStream):
    stream_name: str = None
    report_file: str
    records_number: int
    state_file: str
    incremental_report_file: str
    first_read_state: dict
    second_read_state: dict
    transform_field: str = "AccountId"

    @HttpMocker()
    def test_return_records_from_given_csv_file(self, http_mocker: HttpMocker):
        if self.stream_name:
            self.auth_client(http_mocker)
            output = self.read_stream(
                self.stream_name,
                SyncMode.full_refresh, self._config, [],
                self.report_file)
            assert len(output.records) == self.records_number

    @HttpMocker()
    def test_transform_records_from_given_csv_file(self, http_mocker: HttpMocker):
        if self.stream_name:
            self.auth_client(http_mocker)
            output = self.read_stream(
                self.stream_name,
                SyncMode.full_refresh, self._config, [],
                self.report_file)

            assert len(output.records) == self.records_number
            for record in output.records:
                assert self.transform_field in record.record.data.keys()

    @HttpMocker()
    def test_incremental_read_returns_records(self, http_mocker: HttpMocker):
        if self.stream_name:
            self.auth_client(http_mocker)
            output = self.read_stream(
                self.stream_name,
                SyncMode.incremental, self._config, [],
                self.report_file)
            assert len(output.records) == self.records_number
            assert output.most_recent_state == self.first_read_state

    @HttpMocker()
    def test_incremental_read_with_state_returns_records(self, http_mocker: HttpMocker):
        if self.stream_name:
            state = self._state(self.state_file)
            self.auth_client(http_mocker)
            output = self.read_stream(self.stream_name,
                                      SyncMode.incremental, self._config, [],
                                      self.incremental_report_file,
                                      state)
            assert len(output.records) == self.records_number
            assert output.most_recent_state == self.second_read_state


