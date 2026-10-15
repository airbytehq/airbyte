# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime, timedelta, timezone
from unittest import TestCase
from unittest.mock import patch
from zoneinfo import ZoneInfo

import freezegun
import pytest

from airbyte_cdk.models import Level as LogLevel
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder

from .ad_requests import AttributionReportRequestBuilder, OAuthRequestBuilder, ProfilesRequestBuilder
from .ad_responses import AttributionReportResponseBuilder, ErrorResponseBuilder, OAuthResponseBuilder, ProfilesResponseBuilder
from .ad_responses.pagination_strategies import CursorBasedPaginationStrategy, JsonCursorPaginationStrategy, NullCursorPaginationStrategy
from .ad_responses.pagination_strategies.json_cursor_pagination_strategy import JSON_CURSOR_TOKEN
from .ad_responses.records import AttributionReportRecordBuilder, ErrorRecordBuilder, ProfilesRecordBuilder
from .config import ConfigBuilder
from .utils import get_log_messages_by_log_level, read_stream


REPORTING_PERIOD = 60
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

    # --- HTTP 403 "not authorized to use Amazon Attribution" must be ignored ---

    @HttpMocker()
    def test_given_attribution_not_authorized_403_when_read_performance_adgroup_then_stream_is_ignored(self, http_mocker):
        self._given_oauth_and_profiles(http_mocker, self._config)

        profile_timezone = ProfilesRecordBuilder.profiles_record().build().get("timezone")
        not_authorized_error = ErrorRecordBuilder.breaking_error().with_error_message(
            "This profileID is not authorized to use Amazon Attribution"
        )

        http_mocker.post(
            AttributionReportRequestBuilder.performance_adgroup_endpoint(
                self._config["client_id"],
                self._config["access_token"],
                self._config["profiles"][0],
                start_date=_A_START_DATE.astimezone(ZoneInfo(profile_timezone)).date(),
                end_date=_NOW.astimezone(ZoneInfo(profile_timezone)).date(),
            ).build(),
            ErrorResponseBuilder.breaking_error_response().with_record(not_authorized_error).with_status_code(403).build(),
        )

        output = read_stream("attribution_report_performance_adgroup", SyncMode.full_refresh, self._config)
        assert len(output.records) == 0

        error_logs = get_log_messages_by_log_level(output.logs, LogLevel.ERROR)
        assert not any(["not authorized" in error for error in error_logs])

    @HttpMocker()
    def test_given_attribution_not_authorized_403_when_read_performance_campaign_then_stream_is_ignored(self, http_mocker):
        self._given_oauth_and_profiles(http_mocker, self._config)

        profile_timezone = ProfilesRecordBuilder.profiles_record().build().get("timezone")
        not_authorized_error = ErrorRecordBuilder.breaking_error().with_error_message(
            "This profileID is not authorized to use Amazon Attribution"
        )

        http_mocker.post(
            AttributionReportRequestBuilder.performance_campaign_endpoint(
                self._config["client_id"],
                self._config["access_token"],
                self._config["profiles"][0],
                start_date=_A_START_DATE.astimezone(ZoneInfo(profile_timezone)).date(),
                end_date=_NOW.astimezone(ZoneInfo(profile_timezone)).date(),
            ).build(),
            ErrorResponseBuilder.breaking_error_response().with_record(not_authorized_error).with_status_code(403).build(),
        )

        output = read_stream("attribution_report_performance_campaign", SyncMode.full_refresh, self._config)
        assert len(output.records) == 0

        error_logs = get_log_messages_by_log_level(output.logs, LogLevel.ERROR)
        assert not any(["not authorized" in error for error in error_logs])

    @HttpMocker()
    def test_given_attribution_not_authorized_403_when_read_performance_creative_then_stream_is_ignored(self, http_mocker):
        self._given_oauth_and_profiles(http_mocker, self._config)

        profile_timezone = ProfilesRecordBuilder.profiles_record().build().get("timezone")
        not_authorized_error = ErrorRecordBuilder.breaking_error().with_error_message(
            "This profileID is not authorized to use Amazon Attribution"
        )

        http_mocker.post(
            AttributionReportRequestBuilder.performance_creative_endpoint(
                self._config["client_id"],
                self._config["access_token"],
                self._config["profiles"][0],
                start_date=_A_START_DATE.astimezone(ZoneInfo(profile_timezone)).date(),
                end_date=_NOW.astimezone(ZoneInfo(profile_timezone)).date(),
            ).build(),
            ErrorResponseBuilder.breaking_error_response().with_record(not_authorized_error).with_status_code(403).build(),
        )

        output = read_stream("attribution_report_performance_creative", SyncMode.full_refresh, self._config)
        assert len(output.records) == 0

        error_logs = get_log_messages_by_log_level(output.logs, LogLevel.ERROR)
        assert not any(["not authorized" in error for error in error_logs])

    # --- HTTP 401 {"message": "Unauthorized"} on /attribution/report must be ignored ---

    def _assert_attribution_unauthorized_401_is_ignored(self, http_mocker, stream_name: str, endpoint_factory) -> None:
        self._given_oauth_and_profiles(http_mocker, self._config)

        profile_timezone = ProfilesRecordBuilder.profiles_record().build().get("timezone")
        unauthorized_error = ErrorRecordBuilder.breaking_error().with_error_message("Unauthorized")

        http_mocker.post(
            endpoint_factory(
                self._config["client_id"],
                self._config["access_token"],
                self._config["profiles"][0],
                start_date=_A_START_DATE.astimezone(ZoneInfo(profile_timezone)).date(),
                end_date=_NOW.astimezone(ZoneInfo(profile_timezone)).date(),
            ).build(),
            ErrorResponseBuilder.breaking_error_response().with_record(unauthorized_error).with_status_code(401).build(),
        )

        output = read_stream(stream_name, SyncMode.full_refresh, self._config)
        assert len(output.records) == 0
        assert not output.errors

        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert not any(["Unauthorized" in error for error in error_logs])

        info_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.INFO))
        assert any(["Amazon returned 401 Unauthorized from the Attribution API" in info for info in info_logs])

    @HttpMocker()
    def test_given_attribution_unauthorized_401_when_read_products_then_stream_is_ignored(self, http_mocker):
        self._assert_attribution_unauthorized_401_is_ignored(
            http_mocker, "attribution_report_products", AttributionReportRequestBuilder.products_endpoint
        )

    @HttpMocker()
    def test_given_attribution_unauthorized_401_when_read_performance_adgroup_then_stream_is_ignored(self, http_mocker):
        self._assert_attribution_unauthorized_401_is_ignored(
            http_mocker, "attribution_report_performance_adgroup", AttributionReportRequestBuilder.performance_adgroup_endpoint
        )

    @HttpMocker()
    def test_given_attribution_unauthorized_401_when_read_performance_campaign_then_stream_is_ignored(self, http_mocker):
        self._assert_attribution_unauthorized_401_is_ignored(
            http_mocker, "attribution_report_performance_campaign", AttributionReportRequestBuilder.performance_campaign_endpoint
        )

    @HttpMocker()
    def test_given_attribution_unauthorized_401_when_read_performance_creative_then_stream_is_ignored(self, http_mocker):
        self._assert_attribution_unauthorized_401_is_ignored(
            http_mocker, "attribution_report_performance_creative", AttributionReportRequestBuilder.performance_creative_endpoint
        )

    @HttpMocker()
    def test_given_one_profile_unauthorized_401_when_read_products_then_other_profiles_are_synced(self, http_mocker):
        unauthorized_profile_id, authorized_profile_id = 1, 2
        profile_timezone = ProfilesRecordBuilder.profiles_record().build().get("timezone")
        start_date = _A_START_DATE.astimezone(ZoneInfo(profile_timezone)).date()
        end_date = _NOW.astimezone(ZoneInfo(profile_timezone)).date()
        config = ConfigBuilder().with_start_date(start_date).with_profiles([unauthorized_profile_id, authorized_profile_id]).build()

        http_mocker.post(
            OAuthRequestBuilder.oauth_endpoint(
                client_id=config["client_id"], client_secred=config["client_secret"], refresh_token=config["refresh_token"]
            ).build(),
            OAuthResponseBuilder.token_response().build(),
        )
        http_mocker.get(
            ProfilesRequestBuilder.profiles_endpoint(client_id=config["client_id"], client_access_token=config["access_token"]).build(),
            ProfilesResponseBuilder.profiles_response()
            .with_record(ProfilesRecordBuilder.profiles_record().with_id(unauthorized_profile_id))
            .with_record(ProfilesRecordBuilder.profiles_record().with_id(authorized_profile_id))
            .build(),
        )

        unauthorized_error = ErrorRecordBuilder.breaking_error().with_error_message("Unauthorized")

        http_mocker.post(
            AttributionReportRequestBuilder.products_endpoint(
                config["client_id"], config["access_token"], unauthorized_profile_id, start_date=start_date, end_date=end_date
            ).build(),
            ErrorResponseBuilder.breaking_error_response().with_record(unauthorized_error).with_status_code(401).build(),
        )
        http_mocker.post(
            AttributionReportRequestBuilder.products_endpoint(
                config["client_id"], config["access_token"], authorized_profile_id, start_date=start_date, end_date=end_date
            ).build(),
            AttributionReportResponseBuilder.products_response().with_record(AttributionReportRecordBuilder.products_record()).build(),
        )

        output = read_stream("attribution_report_products", SyncMode.full_refresh, config)
        assert len(output.records) == 1
        assert not output.errors

    # --- cursorId as JSON-shaped string: must remain a string through pagination ---

    @HttpMocker()
    def test_given_json_cursor_when_read_products_then_cursor_stays_string(self, http_mocker):
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
            AttributionReportResponseBuilder.products_response(JsonCursorPaginationStrategy())
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
            .with_cursor_field(JSON_CURSOR_TOKEN)
            .build(),
            AttributionReportResponseBuilder.products_response().with_record(AttributionReportRecordBuilder.products_record()).build(),
        )

        output = read_stream("attribution_report_products", SyncMode.full_refresh, self._config)
        assert len(output.records) == 2

    @HttpMocker()
    def test_given_json_cursor_when_read_performance_adgroup_then_cursor_stays_string(self, http_mocker):
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
            AttributionReportResponseBuilder.performance_adgroup_response(JsonCursorPaginationStrategy())
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
            .with_cursor_field(JSON_CURSOR_TOKEN)
            .build(),
            AttributionReportResponseBuilder.performance_adgroup_response()
            .with_record(AttributionReportRecordBuilder.performance_adgroup_record())
            .build(),
        )

        output = read_stream("attribution_report_performance_adgroup", SyncMode.full_refresh, self._config)
        assert len(output.records) == 2

    @HttpMocker()
    def test_given_json_cursor_when_read_performance_campaign_then_cursor_stays_string(self, http_mocker):
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
            AttributionReportResponseBuilder.performance_campaign_response(JsonCursorPaginationStrategy())
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
            .with_cursor_field(JSON_CURSOR_TOKEN)
            .build(),
            AttributionReportResponseBuilder.performance_campaign_response()
            .with_record(AttributionReportRecordBuilder.performance_campaign_record())
            .build(),
        )

        output = read_stream("attribution_report_performance_campaign", SyncMode.full_refresh, self._config)
        assert len(output.records) == 2

    @HttpMocker()
    def test_given_json_cursor_when_read_performance_creative_then_cursor_stays_string(self, http_mocker):
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
            AttributionReportResponseBuilder.performance_creative_response(JsonCursorPaginationStrategy())
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
            .with_cursor_field(JSON_CURSOR_TOKEN)
            .build(),
            AttributionReportResponseBuilder.performance_creative_response()
            .with_record(AttributionReportRecordBuilder.performance_creative_record())
            .build(),
        )

        output = read_stream("attribution_report_performance_creative", SyncMode.full_refresh, self._config)
        assert len(output.records) == 2

    # --- cursorId = null in response: pagination must stop ---

    @HttpMocker()
    def test_given_null_cursor_when_read_products_then_pagination_stops(self, http_mocker):
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
            AttributionReportResponseBuilder.products_response(NullCursorPaginationStrategy())
            .with_record(AttributionReportRecordBuilder.products_record())
            .with_pagination()
            .build(),
        )

        output = read_stream("attribution_report_products", SyncMode.full_refresh, self._config)
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_null_cursor_when_read_performance_adgroup_then_pagination_stops(self, http_mocker):
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
            AttributionReportResponseBuilder.performance_adgroup_response(NullCursorPaginationStrategy())
            .with_record(AttributionReportRecordBuilder.performance_adgroup_record())
            .with_pagination()
            .build(),
        )

        output = read_stream("attribution_report_performance_adgroup", SyncMode.full_refresh, self._config)
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_null_cursor_when_read_performance_campaign_then_pagination_stops(self, http_mocker):
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
            AttributionReportResponseBuilder.performance_campaign_response(NullCursorPaginationStrategy())
            .with_record(AttributionReportRecordBuilder.performance_campaign_record())
            .with_pagination()
            .build(),
        )

        output = read_stream("attribution_report_performance_campaign", SyncMode.full_refresh, self._config)
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_null_cursor_when_read_performance_creative_then_pagination_stops(self, http_mocker):
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
            AttributionReportResponseBuilder.performance_creative_response(NullCursorPaginationStrategy())
            .with_record(AttributionReportRecordBuilder.performance_creative_record())
            .with_pagination()
            .build(),
        )

        output = read_stream("attribution_report_performance_creative", SyncMode.full_refresh, self._config)
        assert len(output.records) == 1


_ATTRIBUTION_STREAMS = [
    ("attribution_report_products", "products"),
    ("attribution_report_performance_adgroup", "performance_adgroup"),
    ("attribution_report_performance_campaign", "performance_campaign"),
    ("attribution_report_performance_creative", "performance_creative"),
]
_PROFILE_IDS = [1, 2]
_ATTRIBUTION_WINDOW_DAYS = 14


@freezegun.freeze_time(_NOW.isoformat())
class TestAttributionReportStreamsIncremental:
    _profile_timezone = ZoneInfo(ProfilesRecordBuilder.profiles_record().build().get("timezone"))
    _today = _NOW.astimezone(_profile_timezone).date()
    _window_start = _A_START_DATE.astimezone(_profile_timezone).date()
    _sync_end_date = _NOW.date().isoformat()

    def _config(self, look_back_window=None) -> dict:
        config = ConfigBuilder().with_start_date(self._window_start).with_profiles(_PROFILE_IDS).build()
        if look_back_window is not None:
            config["look_back_window"] = look_back_window
        return config

    def _given_oauth_and_profiles(self, http_mocker: HttpMocker, config: dict) -> None:
        http_mocker.post(
            OAuthRequestBuilder.oauth_endpoint(
                client_id=config["client_id"], client_secred=config["client_secret"], refresh_token=config["refresh_token"]
            ).build(),
            OAuthResponseBuilder.token_response().build(),
        )
        profiles_response = ProfilesResponseBuilder.profiles_response()
        for profile_id in _PROFILE_IDS:
            profiles_response = profiles_response.with_record(ProfilesRecordBuilder.profiles_record().with_id(profile_id))
        http_mocker.get(
            ProfilesRequestBuilder.profiles_endpoint(client_id=config["client_id"], client_access_token=config["access_token"]).build(),
            profiles_response.build(),
        )

    def _given_report(self, http_mocker: HttpMocker, config: dict, endpoint: str, profile_id: int, start_date) -> None:
        http_mocker.post(
            getattr(AttributionReportRequestBuilder, f"{endpoint}_endpoint")(
                config["client_id"],
                config["access_token"],
                profile_id,
                start_date=start_date,
                end_date=self._today,
            ).build(),
            getattr(AttributionReportResponseBuilder, f"{endpoint}_response")()
            .with_record(getattr(AttributionReportRecordBuilder, f"{endpoint}_record")())
            .build(),
        )

    @staticmethod
    def _state(stream_name: str, cursor_per_profile: dict) -> list:
        return (
            StateBuilder()
            .with_stream_state(
                stream_name,
                {
                    "states": [
                        {"partition": {"parent_slice": {}, "profileId": profile_id}, "cursor": {"reportDate": cursor.isoformat()}}
                        for profile_id, cursor in cursor_per_profile.items()
                    ]
                },
            )
            .build()
        )

    @staticmethod
    def _cursor_per_profile(output) -> dict:
        return {state["partition"]["profileId"]: state["cursor"]["reportDate"] for state in output.most_recent_state.stream_state.states}

    @pytest.mark.parametrize("stream_name,endpoint", _ATTRIBUTION_STREAMS)
    def test_given_no_state_when_read_incremental_then_request_full_window_and_emit_state(self, stream_name, endpoint):
        config = self._config()
        with HttpMocker() as http_mocker:
            self._given_oauth_and_profiles(http_mocker, config)
            for profile_id in _PROFILE_IDS:
                self._given_report(http_mocker, config, endpoint, profile_id, start_date=self._window_start)

            output = read_stream(stream_name, SyncMode.incremental, config)

        assert len(output.records) == 2
        assert all(record.record.data["reportDate"] == self._sync_end_date for record in output.records)
        assert self._cursor_per_profile(output) == {profile_id: self._sync_end_date for profile_id in _PROFILE_IDS}

    @pytest.mark.parametrize("stream_name,endpoint", _ATTRIBUTION_STREAMS)
    def test_given_state_when_read_incremental_then_request_start_date_from_state_minus_attribution_window(self, stream_name, endpoint):
        config = self._config()
        recent_cursor = self._today - timedelta(days=20)
        cursor_older_than_retention = self._today - timedelta(days=90)
        state = self._state(stream_name, {1: recent_cursor, 2: cursor_older_than_retention})
        with HttpMocker() as http_mocker:
            self._given_oauth_and_profiles(http_mocker, config)
            self._given_report(http_mocker, config, endpoint, 1, start_date=recent_cursor - timedelta(days=_ATTRIBUTION_WINDOW_DAYS))
            self._given_report(http_mocker, config, endpoint, 2, start_date=self._window_start)

            output = read_stream(stream_name, SyncMode.incremental, config, state)

        assert len(output.records) == 2
        assert self._cursor_per_profile(output) == {profile_id: self._sync_end_date for profile_id in _PROFILE_IDS}

    def test_given_look_back_window_longer_than_attribution_window_when_read_incremental_then_use_look_back_window(self):
        stream_name, endpoint = _ATTRIBUTION_STREAMS[0]
        config = self._config(look_back_window=30)
        cursor = self._today - timedelta(days=10)
        state = self._state(stream_name, {profile_id: cursor for profile_id in _PROFILE_IDS})
        with HttpMocker() as http_mocker:
            self._given_oauth_and_profiles(http_mocker, config)
            for profile_id in _PROFILE_IDS:
                self._given_report(http_mocker, config, endpoint, profile_id, start_date=cursor - timedelta(days=30))

            output = read_stream(stream_name, SyncMode.incremental, config, state)

        assert len(output.records) == 2
