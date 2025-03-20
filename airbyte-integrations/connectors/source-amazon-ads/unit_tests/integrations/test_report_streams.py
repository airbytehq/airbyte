# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


import uuid
from unittest import TestCase

import pendulum
import requests_mock

from airbyte_cdk.models import Level as LogLevel
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequestMatcher

from .ad_requests import (
    OAuthRequestBuilder,
    ProfilesRequestBuilder,
    ReportCheckStatusRequestBuilder,
    ReportDownloadRequestBuilder,
    SponsoredBrandsV3ReportRequestBuilder,
    SponsoredDisplayReportRequestBuilder,
    SponsoredProductsReportRequestBuilder,
)
from .ad_responses import (
    ErrorResponseBuilder,
    OAuthResponseBuilder,
    ProfilesResponseBuilder,
    ReportCheckStatusResponseBuilder,
    ReportDownloadResponseBuilder,
    ReportInitResponseBuilder,
)
from .ad_responses.records import (
    ErrorRecordBuilder,
    ProfilesRecordBuilder,
    ReportCheckStatusRecordBuilder,
    ReportFileRecordBuilder,
    ReportInitResponseRecordBuilder,
)
from .config import ConfigBuilder
from .metrics_map import BRANDS_METRICS_MAP_V3, DISPLAY_REPORT_METRICS_MAP, PRODUCTS_REPORT_METRICS_MAP
from .utils import get_log_messages_by_log_level, read_stream


class TestDisplayReportStreams(TestCase):
    @property
    def _config(self):
        return ConfigBuilder().build()

    def _given_oauth_and_profiles(self, http_mocker: HttpMocker, config: dict) -> None:
        """
        Authenticate and get profiles
        """
        http_mocker.post(
            OAuthRequestBuilder.oauth_endpoint(
                client_id=config["client_id"], client_secred=config["client_secret"], refresh_token=config["refresh_token"]
            ).build(),
            OAuthResponseBuilder.token_response().build(),
        )
        http_mocker.get(
            ProfilesRequestBuilder.profiles_endpoint(client_id=config["client_id"], client_access_token=config["access_token"]).build(),
            ProfilesResponseBuilder.profiles_response().with_record(ProfilesRecordBuilder.profiles_record()).build(),
        )

    @HttpMocker()
    def test_given_file_when_read_display_report_then_return_records(self, http_mocker):
        """
        Check display report stream: normal stream read flow
        In this test we prepare http mocker to handle all report types and tactics as well as workaround to handle gzipped file content
        Request structure:
            1. Request report for start processing
            2. Check status and get a download link
            3. Download report file using the link
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        profile_timezone = ProfilesRecordBuilder.profiles_record().build().get("timezone")
        start_date = pendulum.today(tz=profile_timezone).date()

        for report_type, metrics in DISPLAY_REPORT_METRICS_MAP.items():
            report_id = str(uuid.uuid4())
            http_mocker.post(
                SponsoredDisplayReportRequestBuilder._init_report_endpoint(
                    self._config["client_id"], self._config["access_token"], self._config["profiles"][0], report_type, metrics, start_date
                ).build(),
                ReportInitResponseBuilder.report_init_response()
                .with_record(ReportInitResponseRecordBuilder.init_response_record().with_status("PENDING").with_id(report_id))
                .with_status_code(200)
                .build(),
            )
            download_request_builder = ReportDownloadRequestBuilder.download_endpoint(report_id)
            http_mocker.get(
                ReportCheckStatusRequestBuilder.check_sponsored_display_report_status_endpoint(
                    self._config["client_id"], self._config["access_token"], self._config["profiles"][0], report_id
                ).build(),
                ReportCheckStatusResponseBuilder.check_status_response()
                .with_record(ReportCheckStatusRecordBuilder.status_record().with_status("COMPLETED").with_url(download_request_builder.url))
                .build(),
            )

            # a workaround to pass compressed document to the mocked response
            gzip_file_report_response = (
                ReportDownloadResponseBuilder.download_report().with_record(ReportFileRecordBuilder.report_file_record()).build()
            )
            request_matcher = HttpRequestMatcher(download_request_builder.build(), minimum_number_of_expected_match=1)
            http_mocker._matchers.append(request_matcher)

            http_mocker._mocker.get(
                requests_mock.ANY,
                additional_matcher=http_mocker._matches_wrapper(request_matcher),
                response_list=[{"content": gzip_file_report_response.body, "status_code": gzip_file_report_response.status_code}],
            )

        number_of_records = 0
        for stream_name in (
            "sponsored_display_campaigns_report_stream",
            "sponsored_display_adgroups_report_stream",
            "sponsored_display_productads_report_stream",
            "sponsored_display_targets_report_stream",
            "sponsored_display_asins_report_stream",
        ):
            output = read_stream(stream_name, SyncMode.full_refresh, self._config)
            number_of_records += len(output.records)
        assert number_of_records == 5

    @HttpMocker()
    def test_given_file_when_read_products_report_then_return_records(self, http_mocker):
        """
        Check products report stream: normal stream read flow.
        In this test we prepare http mocker to handle all report types based on metrics defined for the report stream
        as well as workaround to handle gzipped file content.
        Request structure:
            1. Request report for start processing
            2. Check status and get a download link
            3. Download report file using the link
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        profile_timezone = ProfilesRecordBuilder.profiles_record().build().get("timezone")
        start_date = pendulum.today(tz=profile_timezone).date()

        for report_type, metrics in PRODUCTS_REPORT_METRICS_MAP.items():
            report_id = str(uuid.uuid4())
            http_mocker.post(
                SponsoredProductsReportRequestBuilder._init_report_endpoint(
                    self._config["client_id"], self._config["access_token"], self._config["profiles"][0], report_type, metrics, start_date
                ).build(),
                ReportInitResponseBuilder.report_init_response()
                .with_record(ReportInitResponseRecordBuilder.init_response_record().with_status("PENDING").with_id(report_id))
                .with_status_code(200)
                .build(),
            )
            download_request_builder = ReportDownloadRequestBuilder.download_endpoint(report_id)
            http_mocker.get(
                ReportCheckStatusRequestBuilder.check_sponsored_products_report_status_endpoint(
                    self._config["client_id"], self._config["access_token"], self._config["profiles"][0], report_id
                ).build(),
                ReportCheckStatusResponseBuilder.check_status_response()
                .with_record(ReportCheckStatusRecordBuilder.status_record().with_status("COMPLETED").with_url(download_request_builder.url))
                .build(),
            )

            # a workaround to pass compressed document to the mocked response
            gzip_file_report_response = (
                ReportDownloadResponseBuilder.download_report().with_record(ReportFileRecordBuilder.report_file_record()).build()
            )
            request_matcher = HttpRequestMatcher(download_request_builder.build(), minimum_number_of_expected_match=1)
            http_mocker._matchers.append(request_matcher)

            http_mocker._mocker.get(
                requests_mock.ANY,
                additional_matcher=http_mocker._matches_wrapper(request_matcher),
                response_list=[{"content": gzip_file_report_response.body, "status_code": gzip_file_report_response.status_code}],
            )
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
            output = read_stream(stream_name, SyncMode.full_refresh, self._config)
            number_of_records += len(output.records)
        assert number_of_records == 7

    @HttpMocker()
    def test_given_file_when_read_brands_v3_report_then_return_records(self, http_mocker):
        """
        Check brands v3 report stream: normal stream read flow.
        In this test we prepare http mocker to handle all report types based on metrics defined for the report stream
        as well as workaround to handle gzipped file content.
        Request structure:
            1. Request report for start processing
            2. Check status and get a download link
            3. Download report file using the link
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        profile_timezone = ProfilesRecordBuilder.profiles_record().build().get("timezone")
        start_date = pendulum.today(tz=profile_timezone).date()
        for report_type, metrics in BRANDS_METRICS_MAP_V3.items():
            report_id = str(uuid.uuid4())
            http_mocker.post(
                SponsoredBrandsV3ReportRequestBuilder._init_report_endpoint(
                    self._config["client_id"], self._config["access_token"], self._config["profiles"][0], report_type, metrics, start_date
                ).build(),
                ReportInitResponseBuilder.report_init_response()
                .with_record(ReportInitResponseRecordBuilder.init_response_record().with_status("PENDING").with_id(report_id))
                .with_status_code(200)
                .build(),
            )
            download_request_builder = ReportDownloadRequestBuilder.download_endpoint(report_id)
            http_mocker.get(
                ReportCheckStatusRequestBuilder.check_sponsored_brands_v3_report_status_endpoint(
                    self._config["client_id"], self._config["access_token"], self._config["profiles"][0], report_id
                ).build(),
                ReportCheckStatusResponseBuilder.check_status_response()
                .with_record(ReportCheckStatusRecordBuilder.status_record().with_status("COMPLETED").with_url(download_request_builder.url))
                .build(),
            )

            # a workaround to pass compressed document to the mocked response
            gzip_file_report_response = (
                ReportDownloadResponseBuilder.download_report().with_record(ReportFileRecordBuilder.report_file_record()).build()
            )
            request_matcher = HttpRequestMatcher(download_request_builder.build(), minimum_number_of_expected_match=1)
            http_mocker._matchers.append(request_matcher)

            http_mocker._mocker.get(
                requests_mock.ANY,
                additional_matcher=http_mocker._matches_wrapper(request_matcher),
                response_list=[{"content": gzip_file_report_response.body, "status_code": gzip_file_report_response.status_code}],
            )

        output = read_stream("sponsored_brands_v3_report_stream", SyncMode.incremental, self._config)
        # OLd format
        # assert output.most_recent_state.stream_state == AirbyteStateBlob({"1": {"reportDate": start_date.format("YYYY-MM-DD")}})
        assert output.most_recent_state.stream_state.states == [
            {"cursor": {"reportDate": start_date.format("YYYY-MM-DD")}, "partition": {"parent_slice": {}, "profileId": 1}}
        ]
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_known_error_when_read_brands_v3_report_then_skip_report(self, http_mocker):
        """
        Check brands v3 stream: non-breaking errors are ignored.
        When error of this kind happen, we warn and then keep syncing another reports if possible.
        In this test all report init requests are failed with known error and skipped
        """

        ERRORS = [
            (400, "KDP authors do not have access to Sponsored Brands functionality"),
            (401, "Not authorized to access scope 0001"),
            (406, "Report date is too far in the past."),
        ]

        for status_code, msg in ERRORS:
            self._given_oauth_and_profiles(http_mocker, self._config)
            profile_timezone = ProfilesRecordBuilder.profiles_record().build().get("timezone")
            start_date = pendulum.today(tz=profile_timezone).date()
            non_breaking_error = ErrorRecordBuilder.non_breaking_error().with_error_message(msg)

            for report_type, metrics in BRANDS_METRICS_MAP_V3.items():
                http_mocker.post(
                    SponsoredBrandsV3ReportRequestBuilder._init_report_endpoint(
                        self._config["client_id"],
                        self._config["access_token"],
                        self._config["profiles"][0],
                        report_type,
                        metrics,
                        start_date,
                    ).build(),
                    ErrorResponseBuilder.non_breaking_error_response()
                    .with_record(non_breaking_error)
                    .with_status_code(status_code)
                    .build(),
                )

            output = read_stream("sponsored_brands_v3_report_stream", SyncMode.full_refresh, self._config)
            assert len(output.records) == 0

            warning_logs = get_log_messages_by_log_level(output.logs, LogLevel.WARN)
            expected_warning_log = f"Exception has occurred during job creation: {msg}"
            assert any([expected_warning_log in warn for warn in warning_logs])
            http_mocker.clear_all_matchers()

    @HttpMocker()
    def test_given_known_error_when_read_display_report_then_partially_skip_records(self, http_mocker):
        """
        Check display v3 stream: non-breaking errors are ignored.
        When error of this kind happen, we warn and then keep syncing another reports if possible.
        In this test half of report init requests are failed with known error and skipped while another half of reports successfully processed
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        profile_timezone = ProfilesRecordBuilder.profiles_record().build().get("timezone")
        start_date = pendulum.today(tz=profile_timezone).date()

        for report_type, metrics in DISPLAY_REPORT_METRICS_MAP.items():
            report_id = str(uuid.uuid4())
            http_mocker.post(
                SponsoredDisplayReportRequestBuilder._init_report_endpoint(
                    self._config["client_id"], self._config["access_token"], self._config["profiles"][0], report_type, metrics, start_date
                ).build(),
                ReportInitResponseBuilder.report_init_response()
                .with_record(ReportInitResponseRecordBuilder.init_response_record().with_status("PENDING").with_id(report_id))
                .with_status_code(200)
                .build(),
            )
            download_request_builder = ReportDownloadRequestBuilder.download_endpoint(report_id)
            http_mocker.get(
                ReportCheckStatusRequestBuilder.check_sponsored_display_report_status_endpoint(
                    self._config["client_id"], self._config["access_token"], self._config["profiles"][0], report_id
                ).build(),
                ReportCheckStatusResponseBuilder.check_status_response()
                .with_record(ReportCheckStatusRecordBuilder.status_record().with_status("COMPLETED").with_url(download_request_builder.url))
                .build(),
            )

            # a workaround to pass compressed document to the mocked response
            gzip_file_report_response = (
                ReportDownloadResponseBuilder.download_report().with_record(ReportFileRecordBuilder.report_file_record()).build()
            )
            request_matcher = HttpRequestMatcher(download_request_builder.build(), minimum_number_of_expected_match=1)
            http_mocker._matchers.append(request_matcher)

            http_mocker._mocker.get(
                requests_mock.ANY,
                additional_matcher=http_mocker._matches_wrapper(request_matcher),
                response_list=[{"content": gzip_file_report_response.body, "status_code": gzip_file_report_response.status_code}],
            )

        number_of_records = 0
        for stream_name in (
            "sponsored_display_campaigns_report_stream",
            "sponsored_display_adgroups_report_stream",
            "sponsored_display_productads_report_stream",
            "sponsored_display_targets_report_stream",
            "sponsored_display_asins_report_stream",
        ):
            output = read_stream(stream_name, SyncMode.full_refresh, self._config)
            number_of_records += len(output.records)
        assert number_of_records == 5
