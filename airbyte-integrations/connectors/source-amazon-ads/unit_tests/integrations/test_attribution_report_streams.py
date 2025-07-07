# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime, timedelta, timezone
from unittest import TestCase
from unittest.mock import patch
from zoneinfo import ZoneInfo

import freezegun

from airbyte_cdk.models import Level as LogLevel
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker

from .ad_requests import AttributionReportRequestBuilder, OAuthRequestBuilder, ProfilesRequestBuilder
from .ad_responses import AttributionReportResponseBuilder, ErrorResponseBuilder, OAuthResponseBuilder, ProfilesResponseBuilder
from .ad_responses.pagination_strategies import CursorBasedPaginationStrategy
from .ad_responses.records import AttributionReportRecordBuilder, ErrorRecordBuilder, ProfilesRecordBuilder
from .config import ConfigBuilder
from .utils import get_log_messages_by_log_level, read_stream


REPORTING_PERIOD = 90
_NOW = datetime.now(timezone.utc)
_A_START_DATE = _NOW - timedelta(days=REPORTING_PERIOD)


@freezegun.freeze_time(_NOW.isoformat())
class TestAttributionReportStreamsFullRefresh(TestCase):
    @property
    def _config(self):
        profile_timezone = ProfilesRecordBuilder.profiles_record().build().get("timezone")
        return ConfigBuilder().with_start_date(_A_START_DATE.astimezone(ZoneInfo(profile_timezone)).date()).build()

    def _given_oauth_and_profiles(self, http_mocker: HttpMocker, config: dict) -> None:
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
    def test_given_non_breaking_error_when_read_products_then_stream_is_ignored(self, http_mocker):
        """
        Check products stream: non-breaking errors are ignored
        When error of this kind happen, we warn and then keep syncing another streams
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        profile_timezone = ProfilesRecordBuilder.profiles_record().build().get("timezone")
        non_breaking_error = ErrorRecordBuilder.non_breaking_error()

        http_mocker.post(
            AttributionReportRequestBuilder.products_endpoint(
                self._config["client_id"],
                self._config["access_token"],
                self._config["profiles"][0],
                start_date=_A_START_DATE.astimezone(ZoneInfo(profile_timezone)).date(),
                end_date=_NOW.astimezone(ZoneInfo(profile_timezone)).date(),
            ).build(),
            ErrorResponseBuilder.non_breaking_error_response().with_record(non_breaking_error).with_status_code(400).build(),
        )

        output = read_stream("attribution_report_products", SyncMode.full_refresh, self._config)
        assert len(output.records) == 0

        info_logs = get_log_messages_by_log_level(output.logs, LogLevel.INFO)
        assert any([non_breaking_error.build().get("details") in info for info in info_logs])

    @HttpMocker()
    def test_given_breaking_error_when_read_products_then_stream_is_ignored(self, http_mocker):
        """
        Check products stream: when unknown error happen we stop syncing with raising the error
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        profile_timezone = ProfilesRecordBuilder.profiles_record().build().get("timezone")
        breaking_error = ErrorRecordBuilder.breaking_error()

        http_mocker.post(
            AttributionReportRequestBuilder.products_endpoint(
                self._config["client_id"],
                self._config["access_token"],
                self._config["profiles"][0],
                start_date=_A_START_DATE.astimezone(ZoneInfo(profile_timezone)).date(),
                end_date=_NOW.astimezone(ZoneInfo(profile_timezone)).date(),
            ).build(),
            ErrorResponseBuilder.breaking_error_response().with_record(breaking_error).with_status_code(500).build(),
        )

        with patch("time.sleep", return_value=None):
            output = read_stream("attribution_report_products", SyncMode.full_refresh, self._config)
        assert len(output.records) == 0

        error_logs = get_log_messages_by_log_level(output.logs, LogLevel.ERROR)
        assert any([breaking_error.build().get("message") in error for error in error_logs])

    @HttpMocker()
    def test_given_one_page_when_read_products_then_return_records(self, http_mocker):
        """
        Check prodcts stream: normal full refresh sync without pagination
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        profile_timezone = ProfilesRecordBuilder.profiles_record().build().get("timezone")

        http_mocker.post(
            AttributionReportRequestBuilder.products_endpoint(
                self._config["client_id"],
                self._config["access_token"],
                self._config["profiles"][0],
                start_date=_A_START_DATE.astimezone(ZoneInfo(profile_timezone)).date(),
                end_date=_NOW.astimezone(ZoneInfo(profile_timezone)).date(),
            ).build(),
            AttributionReportResponseBuilder.products_response().with_record(AttributionReportRecordBuilder.products_record()).build(),
        )

        output = read_stream("attribution_report_products", SyncMode.full_refresh, self._config)
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_many_pages_when_read_products_then_return_records(self, http_mocker):
        """
        Check products stream: normal full refresh sync with pagination
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        profile_timezone = ProfilesRecordBuilder.profiles_record().build().get("timezone")

        http_mocker.post(
            AttributionReportRequestBuilder.products_endpoint(
                self._config["client_id"],
                self._config["access_token"],
                self._config["profiles"][0],
                start_date=_A_START_DATE.astimezone(ZoneInfo(profile_timezone)).date(),
                end_date=_NOW.astimezone(ZoneInfo(profile_timezone)).date(),
            ).build(),
            AttributionReportResponseBuilder.products_response(CursorBasedPaginationStrategy())
            .with_record(AttributionReportRecordBuilder.products_record())
            .with_pagination()
            .build(),
        )
        http_mocker.post(
            AttributionReportRequestBuilder.products_endpoint(
                self._config["client_id"],
                self._config["access_token"],
                self._config["profiles"][0],
                start_date=_A_START_DATE.astimezone(ZoneInfo(profile_timezone)).date(),
                end_date=_NOW.astimezone(ZoneInfo(profile_timezone)).date(),
            )
            .with_cursor_field("next-page-token")
            .build(),
            AttributionReportResponseBuilder.products_response().with_record(AttributionReportRecordBuilder.products_record()).build(),
        )

        output = read_stream("attribution_report_products", SyncMode.full_refresh, self._config)
        assert len(output.records) == 2

    @HttpMocker()
    def test_given_non_breaking_error_when_read_performance_adgroup_then_stream_is_ignored(self, http_mocker):
        """
        Check performance ad group stream: non-breaking errors are ignored
        When error of this kind happen, we warn and then keep syncing another streams
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        profile_timezone = ProfilesRecordBuilder.profiles_record().build().get("timezone")
        non_breaking_error = ErrorRecordBuilder.non_breaking_error()

        http_mocker.post(
            AttributionReportRequestBuilder.performance_adgroup_endpoint(
                self._config["client_id"],
                self._config["access_token"],
                self._config["profiles"][0],
                start_date=_A_START_DATE.astimezone(ZoneInfo(profile_timezone)).date(),
                end_date=_NOW.astimezone(ZoneInfo(profile_timezone)).date(),
            ).build(),
            ErrorResponseBuilder.non_breaking_error_response().with_record(non_breaking_error).with_status_code(400).build(),
        )

        output = read_stream("attribution_report_performance_adgroup", SyncMode.full_refresh, self._config)
        assert len(output.records) == 0

        info_logs = get_log_messages_by_log_level(output.logs, LogLevel.INFO)
        assert any([non_breaking_error.build().get("details") in info for info in info_logs])

    @HttpMocker()
    def test_given_breaking_error_when_read_performance_adgroup_then_stream_is_ignored(self, http_mocker):
        """
        Check performance ad group stream: when unknown error happen we stop syncing with raising the error
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        profile_timezone = ProfilesRecordBuilder.profiles_record().build().get("timezone")
        breaking_error = ErrorRecordBuilder.breaking_error()

        http_mocker.post(
            AttributionReportRequestBuilder.performance_adgroup_endpoint(
                self._config["client_id"],
                self._config["access_token"],
                self._config["profiles"][0],
                start_date=_A_START_DATE.astimezone(ZoneInfo(profile_timezone)).date(),
                end_date=_NOW.astimezone(ZoneInfo(profile_timezone)).date(),
            ).build(),
            ErrorResponseBuilder.breaking_error_response().with_record(breaking_error).with_status_code(500).build(),
        )

        with patch("time.sleep", return_value=None):
            output = read_stream("attribution_report_performance_adgroup", SyncMode.full_refresh, self._config)
        assert len(output.records) == 0

        error_logs = get_log_messages_by_log_level(output.logs, LogLevel.ERROR)
        assert any([breaking_error.build().get("message") in error for error in error_logs])

    @HttpMocker()
    def test_given_one_page_when_read_performance_adgroup_then_return_records(self, http_mocker):
        """
        Check performance ad group stream: normal full refresh sync without pagination
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        profile_timezone = ProfilesRecordBuilder.profiles_record().build().get("timezone")

        http_mocker.post(
            AttributionReportRequestBuilder.performance_adgroup_endpoint(
                self._config["client_id"],
                self._config["access_token"],
                self._config["profiles"][0],
                start_date=_A_START_DATE.astimezone(ZoneInfo(profile_timezone)).date(),
                end_date=_NOW.astimezone(ZoneInfo(profile_timezone)).date(),
            ).build(),
            AttributionReportResponseBuilder.performance_adgroup_response()
            .with_record(AttributionReportRecordBuilder.performance_adgroup_record())
            .build(),
        )

        output = read_stream("attribution_report_performance_adgroup", SyncMode.full_refresh, self._config)
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_many_pages_when_read_performance_adgroup_then_return_records(self, http_mocker):
        """
        Check performance ad group stream: normal full refresh sync with pagination
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        profile_timezone = ProfilesRecordBuilder.profiles_record().build().get("timezone")

        http_mocker.post(
            AttributionReportRequestBuilder.performance_adgroup_endpoint(
                self._config["client_id"],
                self._config["access_token"],
                self._config["profiles"][0],
                start_date=_A_START_DATE.astimezone(ZoneInfo(profile_timezone)).date(),
                end_date=_NOW.astimezone(ZoneInfo(profile_timezone)).date(),
            ).build(),
            AttributionReportResponseBuilder.performance_adgroup_response(CursorBasedPaginationStrategy())
            .with_record(AttributionReportRecordBuilder.performance_adgroup_record())
            .with_pagination()
            .build(),
        )
        http_mocker.post(
            AttributionReportRequestBuilder.performance_adgroup_endpoint(
                self._config["client_id"],
                self._config["access_token"],
                self._config["profiles"][0],
                start_date=_A_START_DATE.astimezone(ZoneInfo(profile_timezone)).date(),
                end_date=_NOW.astimezone(ZoneInfo(profile_timezone)).date(),
            )
            .with_cursor_field("next-page-token")
            .build(),
            AttributionReportResponseBuilder.performance_adgroup_response()
            .with_record(AttributionReportRecordBuilder.performance_adgroup_record())
            .build(),
        )

        output = read_stream("attribution_report_performance_adgroup", SyncMode.full_refresh, self._config)
        assert len(output.records) == 2

    @HttpMocker()
    def test_given_non_breaking_error_when_read_performance_campaign_then_stream_is_ignored(self, http_mocker):
        """
        Check performance campaign stream: non-breaking errors are ignored
        When error of this kind happen, we warn and then keep syncing another streams
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        profile_timezone = ProfilesRecordBuilder.profiles_record().build().get("timezone")
        non_breaking_error = ErrorRecordBuilder.non_breaking_error()

        http_mocker.post(
            AttributionReportRequestBuilder.performance_campaign_endpoint(
                self._config["client_id"],
                self._config["access_token"],
                self._config["profiles"][0],
                start_date=_A_START_DATE.astimezone(ZoneInfo(profile_timezone)).date(),
                end_date=_NOW.astimezone(ZoneInfo(profile_timezone)).date(),
            ).build(),
            ErrorResponseBuilder.non_breaking_error_response().with_record(non_breaking_error).with_status_code(400).build(),
        )

        output = read_stream("attribution_report_performance_campaign", SyncMode.full_refresh, self._config)
        assert len(output.records) == 0

        info_logs = get_log_messages_by_log_level(output.logs, LogLevel.INFO)
        assert any([non_breaking_error.build().get("details") in info for info in info_logs])

    @HttpMocker()
    def test_given_breaking_error_when_read_performance_campaign_then_stream_is_ignored(self, http_mocker):
        """
        Check performance campaign stream: when unknown error happen we stop syncing with raising the error
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        profile_timezone = ProfilesRecordBuilder.profiles_record().build().get("timezone")
        breaking_error = ErrorRecordBuilder.breaking_error()

        http_mocker.post(
            AttributionReportRequestBuilder.performance_campaign_endpoint(
                self._config["client_id"],
                self._config["access_token"],
                self._config["profiles"][0],
                start_date=_A_START_DATE.astimezone(ZoneInfo(profile_timezone)).date(),
                end_date=_NOW.astimezone(ZoneInfo(profile_timezone)).date(),
            ).build(),
            ErrorResponseBuilder.breaking_error_response().with_record(breaking_error).with_status_code(500).build(),
        )

        with patch("time.sleep", return_value=None):
            output = read_stream("attribution_report_performance_campaign", SyncMode.full_refresh, self._config)
        assert len(output.records) == 0

        error_logs = get_log_messages_by_log_level(output.logs, LogLevel.ERROR)
        assert any([breaking_error.build().get("message") in error for error in error_logs])

    @HttpMocker()
    def test_given_one_page_when_read_performance_campaign_then_return_records(self, http_mocker):
        """
        Check performance campaign stream: normal full refresh sync without pagination
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        profile_timezone = ProfilesRecordBuilder.profiles_record().build().get("timezone")

        http_mocker.post(
            AttributionReportRequestBuilder.performance_campaign_endpoint(
                self._config["client_id"],
                self._config["access_token"],
                self._config["profiles"][0],
                start_date=_A_START_DATE.astimezone(ZoneInfo(profile_timezone)).date(),
                end_date=_NOW.astimezone(ZoneInfo(profile_timezone)).date(),
            ).build(),
            AttributionReportResponseBuilder.performance_campaign_response()
            .with_record(AttributionReportRecordBuilder.performance_campaign_record())
            .build(),
        )

        output = read_stream("attribution_report_performance_campaign", SyncMode.full_refresh, self._config)
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_many_pages_when_read_performance_campaign_then_return_records(self, http_mocker):
        """
        Check performance campaign stream: normal full refresh sync with pagination
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        profile_timezone = ProfilesRecordBuilder.profiles_record().build().get("timezone")

        http_mocker.post(
            AttributionReportRequestBuilder.performance_campaign_endpoint(
                self._config["client_id"],
                self._config["access_token"],
                self._config["profiles"][0],
                start_date=_A_START_DATE.astimezone(ZoneInfo(profile_timezone)).date(),
                end_date=_NOW.astimezone(ZoneInfo(profile_timezone)).date(),
            ).build(),
            AttributionReportResponseBuilder.performance_campaign_response(CursorBasedPaginationStrategy())
            .with_record(AttributionReportRecordBuilder.performance_campaign_record())
            .with_pagination()
            .build(),
        )
        http_mocker.post(
            AttributionReportRequestBuilder.performance_campaign_endpoint(
                self._config["client_id"],
                self._config["access_token"],
                self._config["profiles"][0],
                start_date=_A_START_DATE.astimezone(ZoneInfo(profile_timezone)).date(),
                end_date=_NOW.astimezone(ZoneInfo(profile_timezone)).date(),
            )
            .with_cursor_field("next-page-token")
            .build(),
            AttributionReportResponseBuilder.performance_campaign_response()
            .with_record(AttributionReportRecordBuilder.performance_campaign_record())
            .build(),
        )

        output = read_stream("attribution_report_performance_campaign", SyncMode.full_refresh, self._config)
        assert len(output.records) == 2

    @HttpMocker()
    def test_given_non_breaking_error_when_read_performance_creative_then_stream_is_ignored(self, http_mocker):
        """
        Check performance creative stream: non-breaking errors are ignored
        When error of this kind happen, we warn and then keep syncing another streams
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        profile_timezone = ProfilesRecordBuilder.profiles_record().build().get("timezone")
        non_breaking_error = ErrorRecordBuilder.non_breaking_error()

        http_mocker.post(
            AttributionReportRequestBuilder.performance_creative_endpoint(
                self._config["client_id"],
                self._config["access_token"],
                self._config["profiles"][0],
                start_date=_A_START_DATE.astimezone(ZoneInfo(profile_timezone)).date(),
                end_date=_NOW.astimezone(ZoneInfo(profile_timezone)).date(),
            ).build(),
            ErrorResponseBuilder.non_breaking_error_response().with_record(non_breaking_error).with_status_code(400).build(),
        )

        output = read_stream("attribution_report_performance_creative", SyncMode.full_refresh, self._config)
        assert len(output.records) == 0

        info_logs = get_log_messages_by_log_level(output.logs, LogLevel.INFO)
        assert any([non_breaking_error.build().get("details") in info for info in info_logs])

    @HttpMocker()
    def test_given_breaking_error_when_read_performance_creative_then_stream_is_ignored(self, http_mocker):
        """
        Check performance creative stream: when unknown error happen we stop syncing with raising the error
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        profile_timezone = ProfilesRecordBuilder.profiles_record().build().get("timezone")
        breaking_error = ErrorRecordBuilder.breaking_error()

        http_mocker.post(
            AttributionReportRequestBuilder.performance_creative_endpoint(
                self._config["client_id"],
                self._config["access_token"],
                self._config["profiles"][0],
                start_date=_A_START_DATE.astimezone(ZoneInfo(profile_timezone)).date(),
                end_date=_NOW.astimezone(ZoneInfo(profile_timezone)).date(),
            ).build(),
            ErrorResponseBuilder.breaking_error_response().with_record(breaking_error).with_status_code(500).build(),
        )

        with patch("time.sleep", return_value=None):
            output = read_stream("attribution_report_performance_creative", SyncMode.full_refresh, self._config)
        assert len(output.records) == 0

        error_logs = get_log_messages_by_log_level(output.logs, LogLevel.ERROR)
        assert any([breaking_error.build().get("message") in error for error in error_logs])

    @HttpMocker()
    def test_given_one_page_when_read_performance_creative_then_return_records(self, http_mocker):
        """
        Check performance creative stream: normal full refresh sync without pagination
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        profile_timezone = ProfilesRecordBuilder.profiles_record().build().get("timezone")

        http_mocker.post(
            AttributionReportRequestBuilder.performance_creative_endpoint(
                self._config["client_id"],
                self._config["access_token"],
                self._config["profiles"][0],
                start_date=_A_START_DATE.astimezone(ZoneInfo(profile_timezone)).date(),
                end_date=_NOW.astimezone(ZoneInfo(profile_timezone)).date(),
            ).build(),
            AttributionReportResponseBuilder.performance_creative_response()
            .with_record(AttributionReportRecordBuilder.performance_creative_record())
            .build(),
        )

        output = read_stream("attribution_report_performance_creative", SyncMode.full_refresh, self._config)
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_many_pages_when_read_performance_creative_then_return_records(self, http_mocker):
        """
        Check performance creative stream: normal full refresh sync with pagination
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        profile_timezone = ProfilesRecordBuilder.profiles_record().build().get("timezone")

        http_mocker.post(
            AttributionReportRequestBuilder.performance_creative_endpoint(
                self._config["client_id"],
                self._config["access_token"],
                self._config["profiles"][0],
                start_date=_A_START_DATE.astimezone(ZoneInfo(profile_timezone)).date(),
                end_date=_NOW.astimezone(ZoneInfo(profile_timezone)).date(),
            ).build(),
            AttributionReportResponseBuilder.performance_creative_response(CursorBasedPaginationStrategy())
            .with_record(AttributionReportRecordBuilder.performance_creative_record())
            .with_pagination()
            .build(),
        )
        http_mocker.post(
            AttributionReportRequestBuilder.performance_creative_endpoint(
                self._config["client_id"],
                self._config["access_token"],
                self._config["profiles"][0],
                start_date=_A_START_DATE.astimezone(ZoneInfo(profile_timezone)).date(),
                end_date=_NOW.astimezone(ZoneInfo(profile_timezone)).date(),
            )
            .with_cursor_field("next-page-token")
            .build(),
            AttributionReportResponseBuilder.performance_creative_response()
            .with_record(AttributionReportRecordBuilder.performance_creative_record())
            .build(),
        )

        output = read_stream("attribution_report_performance_creative", SyncMode.full_refresh, self._config)
        assert len(output.records) == 2
