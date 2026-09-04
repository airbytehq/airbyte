# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import gzip
import json
from pathlib import Path
from typing import Any, Mapping

import pytest
import requests_mock
import yaml

from airbyte_cdk.models import Level as LogLevel
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now
from unit_tests.conftest import get_source


_MANIFEST_PATH = Path(__file__).parent.parent.parent / "manifest.yaml"
_MANIFEST = yaml.safe_load(_MANIFEST_PATH.read_text())


def _report_stream_configurations(predicate=None) -> list:
    """`(stream_name, report configuration, schema)` for every report stream in the manifest.

    A report stream is one whose `creation_requester` sends a `configuration` carrying a
    `reportTypeId`. Callers narrow the set with `predicate(stream_name, configuration)`.
    """
    configurations = []
    for name, stream in _MANIFEST["definitions"]["streams"].items():
        configuration = stream.get("retriever", {}).get("creation_requester", {}).get("request_body_json", {}).get("configuration")
        if not configuration or "reportTypeId" not in configuration:
            continue
        if predicate and not predicate(name, configuration):
            continue
        schema = _MANIFEST["schemas"][stream["schema_loader"]["schema"]["$ref"].split("/")[-1]]
        configurations.append((name, configuration, schema))
    return configurations


def _report_stream_names(predicate) -> list:
    return [name for name, _, _ in _report_stream_configurations(predicate)]


# Derived from the manifest rather than hardcoded. These lists were previously maintained by hand in
# three separate places, so a stream could be added to the manifest and silently miss every read test.
_ALL_DAILY_STREAMS = _report_stream_names(lambda name, configuration: configuration["timeUnit"] == "DAILY")
_ALL_SPONSORED_PRODUCTS_SUMMARY_STREAMS = _report_stream_names(
    lambda name, configuration: configuration["timeUnit"] == "SUMMARY" and name.startswith("sponsored_products_")
)

# Metrics the removed V2 `sponsored_brands_video_report_stream` returned, under their V3 names.
# `vtr` became `viewabilityRate` and `vctr` became `viewClickThroughRate`. Amazon does not offer
# every one of them on every Sponsored Brands report type, so the expectations differ per stream.
_V2_VIDEO_METRICS = {
    "video5SecondViewRate",
    "video5SecondViews",
    "videoCompleteViews",
    "videoFirstQuartileViews",
    "videoMidpointViews",
    "videoThirdQuartileViews",
    "videoUnmutes",
    "viewabilityRate",
}

_SPONSORED_BRANDS_VIDEO_METRICS = {
    "sponsored_brands_campaigns_report_stream": _V2_VIDEO_METRICS | {"viewableImpressions", "viewClickThroughRate"},
    "sponsored_brands_adgroups_report_stream": _V2_VIDEO_METRICS,
    "sponsored_brands_ads_report_stream": _V2_VIDEO_METRICS | {"viewableImpressions"},
}


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
        source = get_source(config, state)
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
        start_date = ab_datetime_now()
        assert output.most_recent_state.stream_state.states == [
            {"cursor": {"reportDate": start_date.strftime("%Y-%m-%d")}, "partition": {"parent_slice": {}, "profileId": 1}}
        ]
        assert len(output.records) == 1

    def test_given_file_when_read_brands_campaigns_report_then_return_cost_records(
        self, requests_mock: requests_mock.Mocker, config: Mapping[str, Any], mock_oauth, mock_profiles
    ):
        report_id = "report-id-brands-campaigns"
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
        report_data = gzip.compress(b'[{"campaignId": "c1", "cost": 12.34, "clicks": 5, "impressions": 100}]')
        requests_mock.get(
            download_url,
            content=report_data,
            status_code=200,
        )
        output = self._read(config, "sponsored_brands_campaigns_report_stream", SyncMode.incremental)
        created_report_request = next(
            request.json() for request in requests_mock.request_history if request.url.endswith("/reporting/reports")
        )

        assert created_report_request["configuration"]["reportTypeId"] == "sbCampaigns"
        assert created_report_request["configuration"]["groupBy"] == ["campaign"]
        assert "cost" in created_report_request["configuration"]["columns"]
        assert len(output.records) == 1
        assert output.records[0].record.data["cost"] == 12.34

    def test_given_file_when_read_brands_adgroups_report_then_return_cost_records(
        self, requests_mock: requests_mock.Mocker, config: Mapping[str, Any], mock_oauth, mock_profiles
    ):
        report_id = "report-id-brands-adgroups"
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
        report_data = gzip.compress(b'[{"adGroupId": "a1", "adGroupName": "group", "cost": 4.56, "clicks": 3, "impressions": 50}]')
        requests_mock.get(
            download_url,
            content=report_data,
            status_code=200,
        )
        output = self._read(config, "sponsored_brands_adgroups_report_stream", SyncMode.incremental)
        created_report_request = next(
            request.json() for request in requests_mock.request_history if request.url.endswith("/reporting/reports")
        )

        assert created_report_request["configuration"]["reportTypeId"] == "sbAdGroup"
        assert created_report_request["configuration"]["groupBy"] == ["adGroup"]
        assert "cost" in created_report_request["configuration"]["columns"]
        assert len(output.records) == 1
        assert output.records[0].record.data["cost"] == 4.56

    def test_given_file_when_read_brands_ads_report_then_return_video_metrics(
        self, requests_mock: requests_mock.Mocker, config: Mapping[str, Any], mock_oauth, mock_profiles
    ):
        report_id = "report-id-brands-ads"
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
        # Reporting v3 returns numeric ids; the stream schema declares `adId` as integer.
        report_data = gzip.compress(b'[{"adId": 275827446150944, "cost": 1.5, "videoCompleteViews": 42, "video5SecondViews": 90}]')
        requests_mock.get(download_url, content=report_data, status_code=200)

        output = self._read(config, "sponsored_brands_ads_report_stream", SyncMode.incremental)
        created_report_request = next(
            request.json() for request in requests_mock.request_history if request.url.endswith("/reporting/reports")
        )
        configuration = created_report_request["configuration"]

        assert configuration["reportTypeId"] == "sbAds"
        assert configuration["groupBy"] == ["ads"]
        assert "adId" in configuration["columns"]
        assert len(output.records) == 1
        assert output.records[0].record.data["videoCompleteViews"] == 42

    @pytest.mark.parametrize("stream_name, expected_metrics", sorted(_SPONSORED_BRANDS_VIDEO_METRICS.items()))
    def test_sponsored_brands_reports_request_video_metrics(self, stream_name: str, expected_metrics: set) -> None:
        """The V2 `sponsored_brands_video_report_stream` was removed in 6.0.0; its metrics live on
        these V3 report types and must stay in the requested column lists."""
        manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
        for name in (stream_name, f"{stream_name}_daily"):
            columns = set(
                manifest["definitions"]["streams"][name]["retriever"]["creation_requester"]["request_body_json"]["configuration"]["columns"]
            )
            assert expected_metrics <= columns, f"{name} is missing {sorted(expected_metrics - columns)}"

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
        for stream_name in _ALL_SPONSORED_PRODUCTS_SUMMARY_STREAMS:
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
            # Asserted per stream rather than as a total across the loop: a single sum lets a stream
            # silently drop out of the list as long as someone also adjusts the total, which hides
            # exactly the regression this test exists to catch.
            assert len(output.records) == 1, f"{stream_name}: expected 1 record, got {len(output.records)}"

    @pytest.mark.parametrize(
        "stream_name, expected_time_unit",
        [
            ("sponsored_products_search_terms_report_stream", "SUMMARY"),
            ("sponsored_products_search_terms_report_stream_daily", "DAILY"),
        ],
    )
    def test_search_terms_report_requests_sp_search_term_report_type(
        self,
        requests_mock: requests_mock.Mocker,
        config: Mapping[str, Any],
        mock_oauth,
        mock_profiles,
        stream_name: str,
        expected_time_unit: str,
    ):
        """Pin the report request the search terms streams send to Amazon.

        The generic read tests register a catch-all POST and never inspect the body, so swapping
        `reportTypeId` or `groupBy` for another report type's values leaves them green while the
        stream silently returns a different report. Amazon rejects an unknown `reportTypeId`
        outright, but an unintended *valid* one (`spTargeting`, say) fails only as wrong data.
        """
        report_id = f"report-id-{stream_name}-request-body"
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
        requests_mock.get(download_url, content=gzip.compress(b"[]"), status_code=200)

        self._read(config, stream_name)
        created_report_request = next(
            request.json() for request in requests_mock.request_history if request.url.endswith("/reporting/reports")
        )
        configuration = created_report_request["configuration"]

        assert configuration["adProduct"] == "SPONSORED_PRODUCTS"
        assert configuration["reportTypeId"] == "spSearchTerm"
        assert configuration["groupBy"] == ["searchTerm"]
        assert configuration["timeUnit"] == expected_time_unit
        assert configuration["format"] == "GZIP_JSON"
        # `searchTerm` is the grouping dimension, so its columns are what distinguish this report
        # from the keywords/targets reports that share most of the metric list.
        assert {"searchTerm", "targeting", "keywordType"} <= set(configuration["columns"])
        # Unlike the keywords stream (BROAD/PHRASE/EXACT) and the targets stream
        # (TARGETING_EXPRESSION*), this stream deliberately requests all five keyword types in one
        # report. Pinned so narrowing the filter shows up as a test change, not a quiet data loss.
        assert configuration["filters"] == [
            {
                "field": "keywordType",
                "values": ["BROAD", "PHRASE", "EXACT", "TARGETING_EXPRESSION", "TARGETING_EXPRESSION_PREDEFINED"],
            }
        ]

    @pytest.mark.parametrize(
        "stream_name, cursor_field",
        [
            ("sponsored_products_search_terms_report_stream", "reportDate"),
            ("sponsored_products_search_terms_report_stream_daily", "date"),
        ],
    )
    def test_search_terms_report_record_carries_every_primary_key_field(
        self,
        requests_mock: requests_mock.Mocker,
        config: Mapping[str, Any],
        mock_oauth,
        mock_profiles,
        stream_name: str,
        cursor_field: str,
    ):
        """Read a realistically shaped report row and check the composite PK survives to the record.

        The other read tests download placeholder payloads (`{"record": "data"}`) whose fields are
        in neither schema, so they cannot show that the PK fields are actually populated -
        `profileId` and `reportDate` come from `transformation_report_add_fields` rather than from
        Amazon, and a broken transformation would leave the PK partly null without failing a read.
        """
        report_id = f"report-id-{stream_name}-records"
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
        report_row = {
            "searchTerm": "wireless headphones",
            "targeting": "wireless headphones",
            "keywordType": "BROAD",
            "keywordId": 987654321,
            "keyword": "headphones",
            "matchType": "BROAD",
            "campaignId": 111,
            "campaignName": "Test Campaign",
            "adGroupId": 222,
            "adGroupName": "Test Ad Group",
            "impressions": 1000,
            "clicks": 25,
            "cost": 12.34,
            "sales7d": 99.99,
        }
        if cursor_field == "date":
            # Only DAILY reports carry `date`; the SUMMARY stream gets its `reportDate` injected.
            report_row["date"] = "2023-01-15"
        requests_mock.get(
            download_url,
            content=gzip.compress(json.dumps([report_row]).encode()),
            status_code=200,
        )

        output = self._read(config, stream_name, SyncMode.incremental)

        assert len(output.records) == 1
        record = output.records[0].record.data
        primary_key = _MANIFEST["definitions"]["streams"][stream_name]["primary_key"]
        assert primary_key == ["profileId", cursor_field, "searchTerm", "keywordId"]
        for field in primary_key:
            assert record.get(field) is not None, f"{stream_name}: primary key field '{field}' is missing or null"
        assert record["searchTerm"] == "wireless headphones"
        assert record["keywordType"] == "BROAD"
        assert record["cost"] == 12.34
        assert output.most_recent_state.stream_state.states[0]["cursor"][cursor_field] is not None

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

    @pytest.mark.parametrize("stream_name", _ALL_DAILY_STREAMS)
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

    @pytest.mark.parametrize(
        "stream_name",
        [
            "sponsored_brands_v3_report_stream_daily",
            "sponsored_brands_campaigns_report_stream_daily",
            "sponsored_brands_adgroups_report_stream_daily",
            "sponsored_brands_ads_report_stream_daily",
            "sponsored_display_campaigns_report_stream_daily",
            "sponsored_display_targets_report_stream_daily",
            "sponsored_products_campaigns_report_stream_daily",
            "sponsored_products_search_terms_report_stream_daily",
        ],
    )
    def test_daily_stream_uses_date_as_cursor(self, requests_mock, config, mock_oauth, mock_profiles, stream_name):
        """
        Verify that daily streams use the 'date' field from the API response as the cursor field
        instead of the synthetic 'reportDate'. This ensures correct deduplication when using
        incremental + dedup sync mode with a 30-day step.
        """
        report_id = f"report-id-{stream_name}-date-cursor"
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
        report_data = gzip.compress(b'[{"date": "2023-01-15", "campaignId": "c1"}, {"date": "2023-01-16", "campaignId": "c2"}]')
        requests_mock.get(
            download_url,
            content=report_data,
            status_code=200,
        )
        output = self._read(config, stream_name, SyncMode.incremental)
        assert len(output.records) == 2
        # Daily streams should use 'date' as cursor field, not 'reportDate'
        dates = [record.record.data["date"] for record in output.records]
        assert dates == ["2023-01-15", "2023-01-16"]
        # reportDate is still populated (from stream_interval.end_time via the shared transformation)
        assert "reportDate" in output.records[0].record.data
        # Verify the cursor state uses 'date' field
        assert output.most_recent_state.stream_state.states[0]["cursor"]["date"] is not None

    def test_non_daily_stream_uses_report_date_as_cursor(
        self, requests_mock: requests_mock.Mocker, config: Mapping[str, Any], mock_oauth, mock_profiles
    ):
        """
        Verify that non-daily (SUMMARY) streams continue to use 'reportDate' as the cursor field
        with the value set from stream_interval.end_time.
        """
        report_id = "report-id-brands-v3-summary"
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
        report_data = gzip.compress(b'[{"campaignId": "c1", "impressions": 100}]')
        requests_mock.get(
            download_url,
            content=report_data,
            status_code=200,
        )
        output = self._read(config, "sponsored_brands_v3_report_stream", SyncMode.incremental)
        assert len(output.records) == 1
        # SUMMARY streams should still use 'reportDate' as cursor, set from stream_interval.end_time
        assert "reportDate" in output.records[0].record.data
        assert output.records[0].record.data["reportDate"] is not None
        # Verify cursor state uses 'reportDate' field
        assert output.most_recent_state.stream_state.states[0]["cursor"]["reportDate"] is not None


@pytest.mark.parametrize("stream_name", _ALL_DAILY_STREAMS)
def test_daily_stream_schema_has_date_in_properties(stream_name: str) -> None:
    """Verify that the `date` field used as PK/cursor is inside `properties`."""
    schema = _MANIFEST["schemas"][stream_name]
    assert "date" in schema["properties"], (
        f"{stream_name}: 'date' field is missing from the schema's 'properties' block. "
        "It may be misplaced at the schema root level due to a YAML indentation error."
    )


# Bump deliberately when adding or removing a report stream. A silent drop here would empty the
# guard tests below, and pytest reports an empty parameter set as SKIPPED rather than FAILED.
_EXPECTED_REPORT_STREAM_COUNT = 34
_EXPECTED_DAILY_REPORT_STREAM_COUNT = 17
_EXPECTED_SPONSORED_PRODUCTS_SUMMARY_STREAM_COUNT = 8


def test_report_stream_discovery_covers_every_report_stream() -> None:
    """Kept standalone on purpose: `_report_stream_configurations()` is evaluated at import time by
    the `@pytest.mark.parametrize` decorators below, so asserting inside it turns a count change into
    a collection error that takes down every test in this module - including the finer column and
    schema guards that would have named the actual regression.
    """
    configurations = _report_stream_configurations()
    assert len(configurations) == _EXPECTED_REPORT_STREAM_COUNT, (
        f"expected {_EXPECTED_REPORT_STREAM_COUNT} report stream configurations, found {len(configurations)}: "
        "a manifest restructuring may have moved `creation_requester`/`request_body_json` and silently "
        "narrowed the report-column guard tests"
    )
    # The read tests derive their stream lists from the same helper, so the same restructuring would
    # quietly shrink them into passing-but-empty loops. Pin those subsets too.
    assert len(_ALL_DAILY_STREAMS) == _EXPECTED_DAILY_REPORT_STREAM_COUNT
    assert len(_ALL_SPONSORED_PRODUCTS_SUMMARY_STREAMS) == _EXPECTED_SPONSORED_PRODUCTS_SUMMARY_STREAM_COUNT


# `transformation_report_add_fields` (manifest.yaml) injects these into every report record, so they
# are the only schema properties that legitimately have no matching requested column.
_INJECTED_REPORT_FIELDS = {"profileId", "reportDate"}


@pytest.mark.parametrize("stream_name, configuration, schema", _report_stream_configurations())
def test_requested_report_columns_and_schema_properties_match_exactly(stream_name: str, configuration: dict, schema: dict) -> None:
    """The requested column list and the schema must stay in lockstep in both directions.

    A column requested from Amazon but absent from the schema is invisible during discovery and is
    dropped by destinations that enforce the catalog. A property with no requested column means the
    column was dropped from the request and the stream silently stopped emitting that metric. Tying
    the two together means a column can only be removed by also removing its property, which makes
    the loss show up as a schema diff in review.
    """
    columns = set(configuration["columns"])
    properties = set(schema["properties"]) - _INJECTED_REPORT_FIELDS
    undeclared = sorted(columns - properties)
    unrequested = sorted(properties - columns)
    assert not undeclared, f"{stream_name}: requested but not declared in schema: {undeclared}"
    assert not unrequested, f"{stream_name}: declared in schema but never requested: {unrequested}"


@pytest.mark.parametrize("stream_name, configuration, schema", _report_stream_configurations())
def test_report_date_columns_match_time_unit(stream_name: str, configuration: dict, schema: dict) -> None:
    """Amazon pairs the date columns with `timeUnit`: DAILY reports carry `date`, SUMMARY reports
    carry `startDate`/`endDate`. Mixing them makes the report request fail.
    See https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/get-started#timeunit-and-supported-columns
    """
    columns = set(configuration["columns"])
    if configuration["timeUnit"] == "DAILY":
        assert "date" in columns, f"{stream_name}: DAILY report is missing the `date` column"
        assert not {"startDate", "endDate"} & columns, f"{stream_name}: DAILY report requests SUMMARY-only date columns"
    else:
        assert "date" not in columns, f"{stream_name}: SUMMARY report requests the DAILY-only `date` column"


@pytest.mark.parametrize("stream_name, configuration, schema", _report_stream_configurations())
def test_report_stream_primary_key_fields_are_declared_in_schema(stream_name: str, configuration: dict, schema: dict) -> None:
    """Every primary key component must exist as a schema property.

    A PK naming a field the schema does not declare dedupes on a value that is always null, which
    collapses a whole sync into one row per partition. Destinations that enforce the catalog drop the
    undeclared field before deduplication, so the damage happens downstream of any connector-level
    error and this is the last place it can be caught cheaply.

    Structural only - it cannot say whether the chosen fields are *sufficient* to make a row unique.
    """
    properties = set(schema["properties"])
    stream = _MANIFEST["definitions"]["streams"][stream_name]
    missing = [field for field in stream.get("primary_key", []) if field not in properties]
    assert not missing, f"{stream_name}: primary key fields absent from the schema: {missing}"


@pytest.mark.parametrize("stream_name, configuration, schema", _report_stream_configurations())
def test_report_stream_primary_key_includes_the_cursor_field(stream_name: str, configuration: dict, schema: dict) -> None:
    """DAILY streams must dedupe on `date` and SUMMARY streams on `reportDate`.

    Report streams re-request overlapping windows, so a PK that omits the cursor makes every row of
    a later slice collide with the same row from an earlier one and the newer metrics overwrite the
    older ones. `test_daily_stream_uses_date_as_cursor` covers the cursor side of this pairing.
    """
    expected_cursor = "date" if configuration["timeUnit"] == "DAILY" else "reportDate"
    primary_key = _MANIFEST["definitions"]["streams"][stream_name].get("primary_key", [])
    assert expected_cursor in primary_key, (
        f"{stream_name}: {configuration['timeUnit']} report must include `{expected_cursor}` in its "
        f"primary key to dedupe correctly across overlapping slices, got {primary_key}"
    )
