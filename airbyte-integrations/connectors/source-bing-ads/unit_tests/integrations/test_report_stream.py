# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, List, Optional

from base_test import BaseTest
from config_builder import ConfigBuilder
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template


SECOND_READ_FREEZE_TIME = "2024-05-08"


class TestReportStream(BaseTest):
    start_date = "2024-01-01"

    @property
    def _config(self) -> dict[str, Any]:
        return ConfigBuilder().with_reports_start_date(self.start_date).build()

    def _download_file(self, file: Optional[str] = None) -> Path:
        """
        Returns path to a temporary file of downloaded data that will be use in read.
        Base file should be named as {file_name}.csv in the resource/response folder.
        """
        if file:
            path_to_tmp_file = Path(__file__).parent.parent / f"resource/response/{file}.csv"
            return path_to_tmp_file
        return Path(__file__).parent.parent / "resource/response/non-existing-file.csv"


class TestReportDownloadErrorHandling(TestReportStream):
    stream_name = "age_gender_audience_report_hourly"

    _submit_request_body = {
        "ReportRequest": {
            "ExcludeColumnHeaders": False,
            "ExcludeReportFooter": True,
            "ExcludeReportHeader": True,
            "Format": "Csv",
            "FormatVersion": "2.0",
            "ReportName": "AgeGenderAudienceReport",
            "ReturnOnlyCompleteData": False,
            "Type": "AgeGenderAudienceReportRequest",
            "Aggregation": "Hourly",
            "Columns": [
                "AccountName",
                "AccountNumber",
                "AccountId",
                "TimePeriod",
                "CampaignName",
                "CampaignId",
                "AdGroupName",
                "AdGroupId",
                "AdDistribution",
                "AgeGroup",
                "Gender",
                "Impressions",
                "Clicks",
                "Conversions",
                "Spend",
                "Revenue",
                "ExtendedCost",
                "Assists",
                "Language",
                "AccountStatus",
                "CampaignStatus",
                "AdGroupStatus",
                "BaseCampaignId",
                "AllConversions",
                "AllRevenue",
                "ViewThroughConversions",
                "Goal",
                "GoalType",
                "AbsoluteTopImpressionRatePercent",
                "TopImpressionRatePercent",
                "ConversionsQualified",
                "AllConversionsQualified",
                "ViewThroughConversionsQualified",
                "ViewThroughRevenue",
            ],
            "Scope": {"AccountIds": [180535609]},
            "Time": {
                "CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024},
                "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024},
                "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon",
            },
        }
    }

    _expired_sas_response_body = (
        "<Error><Code>AuthenticationFailed</Code><Message>Server failed to authenticate the request.</Message>"
        "<AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [2024-01-01T00:00:00Z] "
        "- Expiry [2024-01-01T00:10:00Z] - Current [2024-01-01T00:11:00Z]</AuthenticationErrorDetail></Error>"
    )
    _permission_mismatch_response_body = (
        "<Error><Code>AuthorizationPermissionMismatch</Code><Message>This request is not authorized to perform this "
        "operation using this permission.</Message></Error>"
    )
    _expired_sas_error_message = "Bing Ads file download URL is expired."
    _default_forbidden_error_message = "Forbidden. You don't have permission to access this resource."

    def _mock_report_apis(self, download_response: HttpResponse):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        self.http_mocker.post(
            HttpRequest(
                url="https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Submit",
                body=json.dumps(self._submit_request_body),
            ),
            HttpResponse('{"ReportRequestId": "thisisthereport_requestid"}', 200),
        )
        poll_response = HttpResponse(
            json.dumps(find_template("generate_report_poll", __file__)),
            200,
        )
        self.http_mocker.post(
            RequestBuilder(resource="GenerateReport/Poll", api="reporting")
            .with_body('{"ReportRequestId": "thisisthereport_requestid"}')
            .build(),
            [poll_response, poll_response],
        )
        self.http_mocker.get(RequestBuilder(resource="").build_report_url(), download_response)

    def _read_with_download_response(self, download_response: HttpResponse):
        self._mock_report_apis(download_response)
        catalog = CatalogBuilder().with_stream(self.stream_name, SyncMode.full_refresh).build()
        return read_helper(self._config, catalog, expecting_exception=True)

    def _assert_error(self, output, failure_type: str, message: str, message_contains: bool = False):
        errors = [message.trace.error for message in output.errors]
        assert any(
            getattr(error.failure_type, "value", error.failure_type) == failure_type
            and (message in error.message if message_contains else error.message == message)
            for error in errors
        ), [(error.failure_type, error.message) for error in errors]

    @freeze_time("2024-05-06")
    def test_expired_download_url_is_transient_error(self):
        output = self._read_with_download_response(
            HttpResponse(
                self._expired_sas_response_body,
                403,
                headers={"x-ms-error-code": "AuthenticationFailed"},
            )
        )

        self._assert_error(output, "transient_error", self._expired_sas_error_message)

    @freeze_time("2024-05-06")
    def test_other_download_forbidden_error_remains_config_error(self):
        output = self._read_with_download_response(
            HttpResponse(
                self._permission_mismatch_response_body,
                403,
                headers={"x-ms-error-code": "AuthorizationPermissionMismatch"},
            )
        )

        self._assert_error(output, "config_error", self._default_forbidden_error_message, message_contains=True)


class TestSuiteReportStream(TestReportStream):
    stream_name: Optional[str] = None
    report_file: str
    report_file_with_records_further_start_date: Optional[str] = None
    records_number: int
    second_read_records_number: Optional[int] = None
    state_file: str
    state_file_after_migration: Optional[str] = None
    state_file_after_migration_with_cursor_further_config_start_date: Optional[str] = None
    state_file_legacy: Optional[str] = None
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

    def mock_report_apis(self):
        # make noop for no migrated streams to manifest (rest api).
        ...

    @freeze_time("2024-05-06")
    def test_return_records_from_given_csv_file(self):
        self.mock_report_apis()
        output = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, self.report_file)
        assert len(output.records) == self.records_number

    @freeze_time("2024-05-06")
    def test_transform_records_from_given_csv_file(self):
        self.mock_report_apis()
        output = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, self.report_file)

        assert len(output.records) == self.records_number
        for record in output.records:
            assert self.transform_field in record.record.data.keys()

    @freeze_time("2024-05-06")
    def test_incremental_read_returns_records(self):
        self.mock_report_apis()
        output = self.read_stream(self.stream_name, SyncMode.incremental, self._config, self.report_file)
        assert len(output.records) == self.records_number
        assert output.most_recent_state.stream_state.__dict__ == self.first_read_state

    @freeze_time("2024-05-06")
    def test_incremental_read_returns_records_further_config_start_date(self):
        """
        We validate the state cursor is set to the value of the latest record read.
        """
        if not self.report_file_with_records_further_start_date or not self.first_read_state_for_records_further_start_date:
            assert False, "test_incremental_read_returns_records_further_config_start_date is not correctly set"
        self.mock_report_apis()
        output = self.read_stream(self.stream_name, SyncMode.incremental, self._config, self.report_file_with_records_further_start_date)
        assert len(output.records) == self.records_number
        assert output.most_recent_state.stream_state.__dict__ == self.first_read_state_for_records_further_start_date

    @freeze_time(SECOND_READ_FREEZE_TIME)
    def test_incremental_read_with_state_and_no_start_date_returns_records_once_after_migration(self):
        """
        Test that incremental read with state and no start date in config returns records only once.
        We observed that if the start date is not provided in the config, and we don't parse correctly the account_id
        from the state, the incremental read returns records multiple times as we yield the default_time_periods
        for no start date scenario.
        """
        self.mock_report_apis()
        state = self._state(self.state_file_legacy, self.stream_name)
        config = deepcopy(self._config)
        del config["reports_start_date"]  # Simulate no start date in config
        output = self.read_stream(
            self.stream_name, SyncMode.incremental, config, self.incremental_report_file_with_records_further_cursor, state
        )
        if not self.second_read_records_number:
            assert len(output.records) == self.records_number
        else:
            assert len(output.records) == self.second_read_records_number

    @freeze_time("2024-05-06")
    def test_incremental_read_with_state_returns_records_after_migration(self):
        """
        For this test the records are all with TimePeriod behind the config start date and the state TimePeriod cursor.
        """
        self.mock_report_apis()
        state = self._state(self.state_file_after_migration, self.stream_name)
        output = self.read_stream(self.stream_name, SyncMode.incremental, self._config, self.incremental_report_file, state)
        if not self.second_read_records_number:
            assert len(output.records) == self.records_number
        else:
            assert len(output.records) == self.second_read_records_number

        actual_cursor = None
        for state in output.most_recent_state.stream_state.states:
            if state["partition"]["account_id"] == self.account_id:
                actual_cursor = state["cursor"]
        expected_state = self.second_read_state_for_records_before_start_date
        expected_cursor = None
        for state in expected_state["states"]:
            if state["partition"]["account_id"] == self.account_id:
                expected_cursor = state["cursor"]
        if not expected_cursor or not actual_cursor:
            assert False, f"Expected state is empty for account_id: {self.account_id}"
        assert actual_cursor == expected_cursor

    @freeze_time(SECOND_READ_FREEZE_TIME)
    def test_incremental_read_with_state_returns_records_after_migration_with_records_further_state_cursor(self):
        """
        For this test we get records with TimePeriod further the config start date and the state TimePeriod cursor.
        The provide state is "taken" from a previous run; with stream manifest; so, is in the new state format, and
        where the resultant cursor was further the config start date.
        So we validate that the cursor in the output.most_recent_state is moved to the value of the latest record read.
        The state format before migration IS NOT involved in this test.
        """
        self.mock_report_apis()
        provided_state = self._state(self.state_file_after_migration_with_cursor_further_config_start_date, self.stream_name)
        output = self.read_stream(
            self.stream_name, SyncMode.incremental, self._config, self.incremental_report_file_with_records_further_cursor, provided_state
        )
        if not self.second_read_records_number:
            assert len(output.records) == self.records_number
        else:
            assert len(output.records) == self.second_read_records_number

        actual_cursor = None
        actual_partition = None
        for state in output.most_recent_state.stream_state.states:
            if state["partition"]["account_id"] == self.account_id:
                actual_cursor = state["cursor"]
                actual_partition = state["partition"]
        expected_state = self.second_read_state_for_records_further_start_date
        expected_cursor = None
        expected_partition = None
        for state in expected_state["states"]:
            if state["partition"]["account_id"] == self.account_id:
                expected_cursor = state["cursor"]
                expected_partition = state["partition"]
        if not expected_cursor or not actual_cursor:
            assert False, f"Expected state is empty for account_id: {self.account_id}"
        # here the cursor moved to expected that is the latest record read
        assert actual_cursor == expected_cursor
        # this is important as we are expecting the new state format
        # to contain the parent slice as should be happening. In this case
        # migration is not needed as the state is already in the new format
        assert actual_partition == expected_partition

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

        last_successful_sync_cursor_value = provided_state[0].stream.stream_state.state[self.cursor_field]
        assert job_start_time == last_successful_sync_cursor_value
        if "hourly" in self.stream_name or (hasattr(self, "custom_report_aggregation") and self.custom_report_aggregation == "Hourly"):
            assert job_end_time == f"{SECOND_READ_FREEZE_TIME}T00:00:00+00:00"
        else:
            assert job_end_time == SECOND_READ_FREEZE_TIME

    @freeze_time(SECOND_READ_FREEZE_TIME)
    def test_incremental_read_with_legacy_state_returns_records_after_migration_with_records_further_state_cursor(self):
        """
        For this test, we get records with TimePeriod further the config start date and the state TimePeriod cursor.
        The provided state is taken from a previous run; with python stream; so, is already in legacy format, and
        where the resultant cursor was further the config start date.
        So we validate that the cursor in the output.most_recent_state is moved to the value of the latest record read.
        Also, the state is migrated to the new format, so we can validate that the partition is correctly set.
        The state format before migration (legacy) IS involved in this test.
        """
        self.mock_report_apis()
        provided_state = self._state(self.state_file_legacy, self.stream_name)
        output = self.read_stream(
            self.stream_name, SyncMode.incremental, self._config, self.incremental_report_file_with_records_further_cursor, provided_state
        )
        if not self.second_read_records_number:
            assert len(output.records) == self.records_number
        else:
            assert len(output.records) == self.second_read_records_number

        actual_cursor = None
        actual_partition = None
        for state in output.most_recent_state.stream_state.states:
            if state["partition"]["account_id"] == self.account_id:
                actual_cursor = state["cursor"]
                actual_partition = state["partition"]
        expected_state = self.second_read_state_for_records_further_start_date
        expected_cursor = None
        expected_partition = None
        for state in expected_state["states"]:
            if state["partition"]["account_id"] == self.account_id:
                expected_cursor = state["cursor"]
                expected_partition = state["partition"]
        if not expected_cursor or not actual_cursor:
            assert False, f"Expected state is empty for account_id: {self.account_id}"
        if not actual_partition or not expected_partition:
            assert False, f"Expected state is empty for account_id: {self.account_id}"
        # here the cursor moved to expect that is the latest record read
        assert actual_cursor == expected_cursor
        assert actual_partition == expected_partition

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

        last_successful_sync_cursor_value = vars(provided_state[0].stream.stream_state)[self.account_id][self.cursor_field]
        assert job_start_time == last_successful_sync_cursor_value
        if "hourly" in self.stream_name or (hasattr(self, "custom_report_aggregation") and self.custom_report_aggregation == "Hourly"):
            assert job_end_time == f"{SECOND_READ_FREEZE_TIME}T00:00:00+00:00"
        else:
            assert job_end_time == SECOND_READ_FREEZE_TIME

    @freeze_time("2024-05-06")
    def test_no_config_start_date(self):
        """
        If the field reports_start_date is blank, Airbyte will replicate all data from previous and current calendar years.
        This test is to validate that the stream will return all records from the first day of the year 2023 (CustomDateRangeStart in mocked body).
        """
        self.mock_report_apis()
        # here we mock the report start date to be the first day of the year 2023
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "AdPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "AdPerformanceReportRequest", "Aggregation": "Hourly", "Columns": ["AccountId", "CampaignId", "AdGroupId", "AdId", "TimePeriod", "AbsoluteTopImpressionRatePercent", "TopImpressionRatePercent", "CurrencyCode", "AdDistribution", "DeviceType", "Language", "Network", "DeviceOS", "TopVsOther", "BidMatchType", "DeliveredMatchType", "AccountName", "CampaignName", "CampaignType", "AdGroupName", "Impressions", "Clicks", "Ctr", "Spend", "CostPerConversion", "DestinationUrl", "Assists", "ReturnOnAdSpend", "CostPerAssist", "CustomParameters", "FinalAppUrl", "AdDescription", "AdDescription2", "ViewThroughConversions", "ViewThroughConversionsQualified", "AllCostPerConversion", "AllReturnOnAdSpend", "Conversions", "ConversionRate", "ConversionsQualified", "AverageCpc", "AveragePosition", "AverageCpm", "AllConversions", "AllConversionRate", "AllRevenue", "AllRevenuePerConversion", "Revenue", "RevenuePerConversion", "RevenuePerAssist"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2023}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        config = deepcopy(self._config)
        del config["reports_start_date"]
        output = self.read_stream(self.stream_name, SyncMode.incremental, config, self.report_file)
        assert len(output.records) == self.records_number
        first_read_state = deepcopy(self.first_read_state)
        # this corresponds to the last read record as we don't have started_date in the config
        # the self.first_read_state is set using the config start date, so it is not correct for this test
        if "hourly" in self.stream_name or (hasattr(self, "custom_report_aggregation") and self.custom_report_aggregation == "Hourly"):
            first_read_state["state"][self.cursor_field] = "2023-11-12T00:00:00+00:00"
            first_read_state["states"][0]["cursor"][self.cursor_field] = "2023-11-12T00:00:00+00:00"
            assert output.most_recent_state.stream_state.__dict__ == first_read_state
        else:
            assert output.most_recent_state.stream_state.__dict__ == first_read_state
