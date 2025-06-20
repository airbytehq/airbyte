# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from test_report_stream import TestSuiteReportStream


FIRST_STATE = {"180535609": {"TimePeriod": "2023-12-17"}}


def get_state_after_migration(time_period: str, account_id: str) -> dict:
    """
    Returns state format for daily reports after migration.
    Uses daily datetime format (without timezone/time component).
    """
    return {
        "lookback_window": 0,
        "parent_state": {},
        "state": {"TimePeriod": f"{time_period}"},
        "states": [
            {
                "cursor": {"TimePeriod": f"{time_period}"},
                "partition": {
                    "account_id": account_id,
                },
            }
        ],
        "use_global_cursor": False,
    }


SECOND_STATE = {"180535609": {"TimePeriod": "2024-05-07"}}


class ReportsTestWithStateChangesAfterMigration(TestSuiteReportStream):
    """
    Base class for daily, weekly, and monthly report streams that have been migrated to the low-code framework.
    Provides state handling for migrated streams with the correct datetime format for non-hourly reports.
    Migration test cases are skipped since they are already tested in hourly reports and all non-hourly streams
    use the same manifest template.
    """

    first_read_state = get_state_after_migration(
        time_period=f"{TestSuiteReportStream.start_date}", account_id=TestSuiteReportStream.account_id
    )
    first_read_state_for_records_further_start_date = get_state_after_migration(
        time_period="2024-05-06", account_id=TestSuiteReportStream.account_id
    )
    second_read_state = {"180535609": {"TimePeriod": "2024-05-07"}}
    second_read_state_for_records_before_start_date = get_state_after_migration(
        time_period=f"{TestSuiteReportStream.start_date}", account_id=TestSuiteReportStream.account_id
    )
    second_read_state_for_records_further_start_date = get_state_after_migration(
        time_period="2024-05-07", account_id=TestSuiteReportStream.account_id
    )

    @property
    def report_file_with_records_further_start_date(self):
        return f"{self.stream_name}_with_records_further_config_start_date"

    state_file_legacy = "reports_state_legacy"
    state_file_after_migration = "reports_state_after_migration"
    state_file_after_migration_with_cursor_further_config_start_date = "reports_state_after_migration_with_cursor_further_config_start_date"

    @property
    def incremental_report_file_with_records_further_cursor(self):
        return f"{self.stream_name}_incremental_with_records_further_cursor"

    @property
    def expected_no_config_start_date_cursor_value(self) -> str:
        """Non-hourly reports use date format without timezone/time component."""
        return "2023-12-17"

    @property
    def expected_job_end_time_format(self) -> str:
        """Non-hourly reports use date format without timezone/time component."""
        return "2024-05-08"

    def test_incremental_read_with_state_and_no_start_date_returns_records_once_after_migration(self):
        """
        Skip migration tests for non-hourly streams since we have thoroughly tested them in hourly reports.
        """
        self.skipTest("Migration test cases skipped for non-hourly streams - already tested in hourly reports")

    def test_incremental_read_with_state_returns_records_after_migration(self):
        """
        Skip migration tests for non-hourly streams since we have thoroughly tested them in hourly reports.
        """
        self.skipTest("Migration test cases skipped for non-hourly streams - already tested in hourly reports")

    def test_incremental_read_with_state_returns_records_after_migration_with_records_further_state_cursor(self):
        """
        Skip migration tests for non-hourly streams since we have thoroughly tested them in hourly reports.
        """
        self.skipTest("Migration test cases skipped for non-hourly streams - already tested in hourly reports")

    def test_incremental_read_with_legacy_state_returns_records_after_migration_with_records_further_state_cursor(self):
        """
        Skip migration tests for non-hourly streams since we have thoroughly tested them in hourly reports.

        """
        self.skipTest("Migration test cases skipped for non-hourly streams - already tested in hourly reports")
