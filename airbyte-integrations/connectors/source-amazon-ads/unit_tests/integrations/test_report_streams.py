# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import gzip
from typing import Any, Mapping

import pendulum
import pytest
import requests_mock
from source_amazon_ads import SourceAmazonAds

from airbyte_cdk.models import Level as LogLevel
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


# Fixture for the configuration with a valid region value
@pytest.fixture(name="config")
def config_fixture() -> Mapping[str, Any]:
    return {
        "client_id": "amzn.app-oa2-client.test",
        "client_secret": "test-secret",
        "refresh_token": "test-refresh-token",
        "region": "NA",
        "report_wait_timeout": 3600,
        "report_generation_max_retry": 5,
    }


# Fixture to mock OAuth token endpoint
@pytest.fixture(name="mock_oauth")
def mock_oauth_fixture(requests_mock: requests_mock.Mocker) -> None:
    requests_mock.post(
        "https://api.amazon.com/auth/o2/token",
        json={"access_token": "test-access-token", "token_type": "bearer", "expires_in": 3600},
        status_code=200,
    )


# Fixture to mock profiles endpoint
@pytest.fixture(name="mock_profiles")
def mock_profiles_fixture(requests_mock: requests_mock.Mocker) -> None:
    requests_mock.get(
        "https://advertising-api.amazon.com/v2/profiles?profileTypeFilter=seller,vendor",
        json=[{"profileId": 1, "timezone": "UTC"}],
        status_code=200,
        request_headers={"Authorization": "Bearer test-access-token"},
    )


def get_log_messages_by_log_level(logs, level: LogLevel) -> list:
    """Utility to extract log messages by log level."""
    return [log.log.message for log in logs if log.type == "LOG" and log.log.level == level]


class TestDisplayReportStreams:
    @staticmethod
    def _read(config: Mapping[str, Any], stream_name: str, sync_mode: SyncMode = SyncMode.full_refresh) -> EntrypointOutput:
        catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
        state = StateBuilder().build()
        source = SourceAmazonAds(catalog, config, state)
        return read(source, config, catalog, state)

    def test_given_file_when_read_brands_v3_report_then_return_records(
        self, requests_mock: requests_mock.Mocker, config: Mapping[str, Any], mock_oauth, mock_profiles
    ):
        """
        Check Sponsored Brands V3 report stream: normal stream read flow
        In this test, we prepare HTTP mocks to handle report initiation, status checks, and file downloads.
        Request structure:
            1. POST request to initiate report processing.
            2. GET request to check report status and retrieve the download URL.
            3. GET request to download the gzipped report file.
        """
        report_id = "report-id-brands-v3"
        download_url = f"https://advertising-api.amazon.com/reporting/reports/{report_id}/download"
        requests_mock.post(
            "https://advertising-api.amazon.com/reporting/reports",
            json={"reportId": report_id, "status": "PENDING"},
            status_code=202,
            request_headers={"Authorization": "Bearer test-access-token"},
        )
        requests_mock.get(
            f"https://advertising-api.amazon.com/reporting/reports/{report_id}",
            json={"status": "COMPLETED", "url": download_url},
            status_code=200,
            request_headers={"Authorization": "Bearer test-access-token"},
        )
        report_data = gzip.compress(b'[{"record": "data"}]')
        requests_mock.get(
            download_url,
            content=report_data,
            status_code=200,
        )
        output = self._read(config, "sponsored_brands_v3_report_stream", SyncMode.incremental)
        start_date = pendulum.today(tz="UTC").date()
        assert output.most_recent_state.stream_state.states == [
            {"cursor": {"reportDate": start_date.format("YYYY-MM-DD")}, "partition": {"parent_slice": {}, "profileId": 1}}
        ]
        assert len(output.records) == 1

    def test_given_file_when_read_display_report_then_return_records(
        self, requests_mock: requests_mock.Mocker, config: Mapping[str, Any], mock_oauth, mock_profiles
    ):
        """
        Check display report streams: normal stream read flow for multiple streams
        This test iterates over several Sponsored Display report streams, mocking the API responses for each.
        It ensures that each stream can successfully initiate, check status, and download a report.
        Request structure:
            1. POST request to initiate report processing for each stream.
            2. GET request to check report status and retrieve the download URL for each stream.
            3. GET request to download the gzipped report file for each stream.
        """
        number_of_records = 0
        for stream_name in (
            "sponsored_display_campaigns_report_stream",
            "sponsored_display_adgroups_report_stream",
            "sponsored_display_productads_report_stream",
            "sponsored_display_targets_report_stream",
            "sponsored_display_asins_report_stream",
        ):
            report_id = f"report-id-display-{stream_name}"
            download_url = f"https://advertising-api.amazon.com/reporting/reports/{report_id}/download"
            requests_mock.post(
                "https://advertising-api.amazon.com/reporting/reports",
                json={"reportId": report_id, "status": "PENDING"},
                status_code=202,
                request_headers={"Authorization": "Bearer test-access-token"},
            )
            requests_mock.get(
                f"https://advertising-api.amazon.com/reporting/reports/{report_id}",
                json={"status": "COMPLETED", "url": download_url},
                status_code=200,
                request_headers={"Authorization": "Bearer test-access-token"},
            )
            report_data = gzip.compress(b'[{"record": "data"}]')
            requests_mock.get(
                download_url,
                content=report_data,
                status_code=200,
            )
            output = self._read(config, stream_name)
            number_of_records += len(output.records)
        assert number_of_records == 5

    def test_given_file_when_read_products_report_then_return_records(
        self, requests_mock: requests_mock.Mocker, config: Mapping[str, Any], mock_oauth, mock_profiles
    ):
        """
        Check Sponsored Products report streams: normal stream read flow for multiple streams
        This test iterates over several Sponsored Products report streams, mocking the API responses for each.
        It ensures that each stream can successfully initiate, check status, and download a report.
        Request structure:
            1. POST request to initiate report processing for each stream.
            2. GET request to check report status and retrieve the download URL for each stream.
            3. GET request to download the gzipped report file for each stream.
        """
        number_of_records = 0
        for stream_name in (
            "sponsored_products_campaigns_report_stream",
            "sponsored_products_adgroups_report_stream",
            "sponsored_products_keywords_report_stream",
            "sponsored_products_targets_report_stream",
            "sponsored_products_productads_report_stream",
            "sponsored_products_asins_keywords_report_stream",
            "sponsored_products_asins_targets_report_stream",
        ):
            report_id = f"report-id-products-{stream_name}"
            download_url = f"https://advertising-api.amazon.com/reporting/reports/{report_id}/download"
            requests_mock.post(
                "https://advertising-api.amazon.com/reporting/reports",
                json={"reportId": report_id, "status": "PENDING"},
                status_code=202,
                request_headers={"Authorization": "Bearer test-access-token"},
            )
            requests_mock.get(
                f"https://advertising-api.amazon.com/reporting/reports/{report_id}",
                json={"status": "COMPLETED", "url": download_url},
                status_code=200,
                request_headers={"Authorization": "Bearer test-access-token"},
            )
            report_data = gzip.compress(b'[{"record": "data"}]')
            requests_mock.get(
                download_url,
                content=report_data,
                status_code=200,
            )
            output = self._read(config, stream_name)
            number_of_records += len(output.records)
        assert number_of_records == 7

    def test_given_known_error_when_read_brands_v3_report_then_skip_report(
        self, requests_mock: requests_mock.Mocker, config: Mapping[str, Any], mock_oauth, mock_profiles
    ):
        """
        Check error handling for Sponsored Brands V3 report stream
        This test simulates known errors (400, 401, 406) by mocking API responses to return empty reports.
        It verifies that the stream skips the report gracefully without logging warnings.
        Request structure:
            1. POST request to initiate report processing.
            2. GET request to check report status and retrieve the download URL.
            3. GET request to download the gzipped empty report file.
        """
        ERRORS = [
            (400, "KDP authors do not have access to Sponsored Brands functionality"),
            (401, "Not authorized to access scope 0001"),
            (406, "Report date is too far in the past."),
        ]
        for status_code, msg in ERRORS:
            report_id = f"report-id-brands-v3-{status_code}"
            download_url = f"https://advertising-api.amazon.com/reporting/reports/{report_id}/download"
            requests_mock.post(
                "https://advertising-api.amazon.com/reporting/reports",
                json={"reportId": report_id, "status": "PENDING"},
                status_code=202,
                request_headers={"Authorization": "Bearer test-access-token"},
            )
            requests_mock.get(
                f"https://advertising-api.amazon.com/reporting/reports/{report_id}",
                json={"status": "COMPLETED", "url": download_url},
                status_code=200,
                request_headers={"Authorization": "Bearer test-access-token"},
            )
            report_data = gzip.compress(b"[]")
            requests_mock.get(
                download_url,
                content=report_data,
                status_code=200,
            )
            output = self._read(config, "sponsored_brands_v3_report_stream")
            assert len(output.records) == 0
            warning_logs = get_log_messages_by_log_level(output.logs, LogLevel.WARN)
            assert len(warning_logs) == 0
            requests_mock.reset()

    def test_given_known_error_when_read_display_report_then_partially_skip_records(
        self, requests_mock: requests_mock.Mocker, config: Mapping[str, Any], mock_oauth, mock_profiles
    ):
        """
        Check partial error handling for Sponsored Display report streams
        This test simulates errors for some streams by mocking empty reports for odd-indexed streams.
        It ensures that the source skips failed streams gracefully while processing successful ones.
        Request structure:
            1. POST request to initiate report processing for each stream.
            2. GET request to check report status and retrieve the download URL for each stream.
            3. GET request to download the gzipped report file (data for even-indexed, empty for odd-indexed).
        """
        streams = (
            "sponsored_display_campaigns_report_stream",
            "sponsored_display_adgroups_report_stream",
            "sponsored_display_productads_report_stream",
            "sponsored_display_targets_report_stream",
            "sponsored_display_asins_report_stream",
        )
        number_of_records = 0
        for i, stream_name in enumerate(streams):
            report_id = f"report-id-display-{stream_name}"
            download_url = f"https://advertising-api.amazon.com/reporting/reports/{report_id}/download"
            requests_mock.post(
                "https://advertising-api.amazon.com/reporting/reports",
                json={"reportId": report_id, "status": "PENDING"},
                status_code=202,
                request_headers={"Authorization": "Bearer test-access-token"},
            )
            requests_mock.get(
                f"https://advertising-api.amazon.com/reporting/reports/{report_id}",
                json={"status": "COMPLETED", "url": download_url},
                status_code=200,
                request_headers={"Authorization": "Bearer test-access-token"},
            )
            report_data = gzip.compress(b'[{"record": "data"}]') if i % 2 == 0 else gzip.compress(b"[]")
            requests_mock.get(
                download_url,
                content=report_data,
                status_code=200,
            )
            output = self._read(config, stream_name)
            number_of_records += len(output.records)
            if i % 2 == 1:
                warning_logs = get_log_messages_by_log_level(output.logs, LogLevel.WARN)
                assert len(warning_logs) == 0
        assert number_of_records == 3

    @pytest.mark.parametrize(
        "stream_name",
        [
            "sponsored_brands_v3_report_stream_daily",
            "sponsored_display_campaigns_report_stream_daily",
            "sponsored_display_adgroups_report_stream_daily",
            "sponsored_display_productads_report_stream_daily",
            "sponsored_display_targets_report_stream_daily",
            "sponsored_display_asins_report_stream_daily",
            "sponsored_products_campaigns_report_stream_daily",
            "sponsored_products_adgroups_report_stream_daily",
            "sponsored_products_keywords_report_stream_daily",
            "sponsored_products_targets_report_stream_daily",
            "sponsored_products_productads_report_stream_daily",
            "sponsored_products_asins_keywords_report_stream_daily",
            "sponsored_products_asins_targets_report_stream_daily",
        ],
    )
    def test_daily_stream(self, requests_mock, config, mock_oauth, mock_profiles, stream_name):
        """
        Check daily report streams: parameterized test for all daily streams
        This test verifies that each daily stream can fetch and process records with the 'date' field.
        It uses HTTP mocks to simulate report initiation, status checks, and downloading gzipped daily data.
        Request structure:
            1. POST request to initiate report processing for the specified stream.
            2. GET request to check report status and retrieve the download URL.
            3. GET request to download the gzipped report file containing daily data.
        """
        report_id = f"report-id-{stream_name}"
        download_url = f"https://advertising-api.amazon.com/reporting/reports/{report_id}/download"
        requests_mock.post(
            "https://advertising-api.amazon.com/reporting/reports",
            json={"reportId": report_id, "status": "PENDING"},
            status_code=202,
            request_headers={"Authorization": "Bearer test-access-token"},
        )
        requests_mock.get(
            f"https://advertising-api.amazon.com/reporting/reports/{report_id}",
            json={"status": "COMPLETED", "url": download_url},
            status_code=200,
            request_headers={"Authorization": "Bearer test-access-token"},
        )
        report_data = gzip.compress(b'[{"date": "2023-01-01", "record": "data1"}, {"date": "2023-01-02", "record": "data2"}]')
        requests_mock.get(
            download_url,
            content=report_data,
            status_code=200,
        )
        output = self._read(config, stream_name)
        assert len(output.records) == 2
        assert all("date" in record.record.data for record in output.records)
        assert [record.record.data["date"] for record in output.records] == ["2023-01-01", "2023-01-02"]
