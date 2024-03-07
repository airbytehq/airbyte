# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from unittest import TestCase
from unittest.mock import patch

from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_protocol.models import Level as LogLevel
from airbyte_protocol.models import SyncMode

from .ad_requests import OAuthRequestBuilder, ProfilesRequestBuilder, SponsoredBrandsRequestBuilder
from .ad_responses import ErrorResponseBuilder, OAuthResponseBuilder, ProfilesResponseBuilder, SponsoredBrandsResponseBuilder
from .ad_responses.pagination_strategies import CountBasedPaginationStrategy
from .ad_responses.records import ErrorRecordBuilder, ProfilesRecordBuilder, SponsoredBrandsRecordBuilder
from .config import ConfigBuilder
from .utils import get_log_messages_by_log_level, read_stream


class TestSponsoredBrandsStreamsFullRefresh(TestCase):
    @property
    def _config(self):
        return ConfigBuilder().build()

    def _given_oauth_and_profiles(self, http_mocker: HttpMocker, config: dict) -> None:
        """
        Authenticate and get profiles
        """
        http_mocker.post(
            OAuthRequestBuilder.oauth_endpoint(client_id=config["client_id"], client_secred=config["client_secret"], refresh_token=config["refresh_token"]).build(),
            OAuthResponseBuilder.token_response().build()
        )
        http_mocker.get(
            ProfilesRequestBuilder.profiles_endpoint(client_id=config["client_id"], client_access_token=config["access_token"]).build(),
            ProfilesResponseBuilder.profiles_response().with_record(ProfilesRecordBuilder.profiles_record()).build()
        )

    @HttpMocker()
    def test_given_non_breaking_error_when_read_ad_groups_then_stream_is_ignored(self, http_mocker):
        """
        Check ad groups stream: non-breaking errors are ignored
        When error of this kind happen, we warn and then keep syncing another streams
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        non_breaking_error = ErrorRecordBuilder.non_breaking_error()
        http_mocker.get(
            SponsoredBrandsRequestBuilder.ad_groups_endpoint(self._config["client_id"], self._config["access_token"], self._config["profiles"][0], limit=100).build(),
            ErrorResponseBuilder.non_breaking_error_response().with_record(non_breaking_error).with_status_code(400).build()
        )
        output = read_stream("sponsored_brands_ad_groups", SyncMode.full_refresh, self._config)
        assert len(output.records) == 0

        warning_logs = get_log_messages_by_log_level(output.logs, LogLevel.WARN)
        assert any([non_breaking_error.build().get("details") in worning for worning in warning_logs])

    @HttpMocker()
    def test_given_breaking_error_when_read_ad_groups_then_stream_stop_syncing(self, http_mocker):
        """
        Check ad groups stream: when unknown error happen we stop syncing with raising the error
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        breaking_error = ErrorRecordBuilder.breaking_error()
        http_mocker.get(
            SponsoredBrandsRequestBuilder.ad_groups_endpoint(self._config["client_id"], self._config["access_token"], self._config["profiles"][0], limit=100).build(),
            ErrorResponseBuilder.breaking_error_response().with_record(breaking_error).with_status_code(500).build()
        )
        with patch('time.sleep', return_value=None):
            output = read_stream("sponsored_brands_ad_groups", SyncMode.full_refresh, self._config)
        assert len(output.records) == 0

        error_logs = get_log_messages_by_log_level(output.logs, LogLevel.ERROR)
        assert any([breaking_error.build().get("message") in error for error in error_logs])

    @HttpMocker()
    def test_given_one_page_when_read_ad_groups_then_return_records(self, http_mocker):
        """
        Check ad groups stream: normal full refresh sync without pagination
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        http_mocker.get(
            SponsoredBrandsRequestBuilder.ad_groups_endpoint(self._config["client_id"], self._config["access_token"], self._config["profiles"][0], limit=100).build(),
            SponsoredBrandsResponseBuilder.ad_groups_response().with_record(SponsoredBrandsRecordBuilder.ad_groups_record()).build()
        )

        output = read_stream("sponsored_brands_ad_groups", SyncMode.full_refresh, self._config)
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_many_pages_when_read_ad_groups_then_return_records(self, http_mocker):
        """
        Check ad groups stream: normal full refresh sync with pagination
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        http_mocker.get(
            SponsoredBrandsRequestBuilder.ad_groups_endpoint(self._config["client_id"], self._config["access_token"], self._config["profiles"][0], limit=100).build(),
            SponsoredBrandsResponseBuilder.ad_groups_response(CountBasedPaginationStrategy()).with_record(SponsoredBrandsRecordBuilder.ad_groups_record()).with_pagination().build()
        )
        http_mocker.get(
            SponsoredBrandsRequestBuilder.ad_groups_endpoint(self._config["client_id"], self._config["access_token"], self._config["profiles"][0], limit=100, start_index=100).build(),
            SponsoredBrandsResponseBuilder.ad_groups_response(CountBasedPaginationStrategy()).with_record(SponsoredBrandsRecordBuilder.ad_groups_record()).with_pagination().build()
        )
        http_mocker.get(
            SponsoredBrandsRequestBuilder.ad_groups_endpoint(self._config["client_id"], self._config["access_token"], self._config["profiles"][0], limit=100, start_index=200).build(),
            SponsoredBrandsResponseBuilder.ad_groups_response().with_record(SponsoredBrandsRecordBuilder.ad_groups_record()).build()
        )

        output = read_stream("sponsored_brands_ad_groups", SyncMode.full_refresh, self._config)
        assert len(output.records) == 201

    @HttpMocker()
    def test_given_non_breaking_error_when_read_campaigns_then_stream_is_ignored(self, http_mocker):
        """
        Check campaigns stream: non-breaking errors are ignored
        When error of this kind happen, we warn and then keep syncing another streams
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        non_breaking_error = ErrorRecordBuilder.non_breaking_error()
        http_mocker.get(
            SponsoredBrandsRequestBuilder.campaigns_endpoint(self._config["client_id"], self._config["access_token"], self._config["profiles"][0], limit=100).build(),
            ErrorResponseBuilder.non_breaking_error_response().with_record(non_breaking_error).with_status_code(400).build()
        )
        output = read_stream("sponsored_brands_campaigns", SyncMode.full_refresh, self._config)
        assert len(output.records) == 0

        warning_logs = get_log_messages_by_log_level(output.logs, LogLevel.WARN)
        assert any([non_breaking_error.build().get("details") in worning for worning in warning_logs])

    @HttpMocker()
    def test_given_breaking_error_when_read_campaigns_then_stream_stop_syncing(self, http_mocker):
        """
        Check campaigns stream: when unknown error happen we stop syncing with raising the error
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        breaking_error = ErrorRecordBuilder.breaking_error()
        http_mocker.get(
            SponsoredBrandsRequestBuilder.campaigns_endpoint(self._config["client_id"], self._config["access_token"], self._config["profiles"][0], limit=100).build(),
            ErrorResponseBuilder.breaking_error_response().with_record(breaking_error).with_status_code(500).build()
        )
        with patch('time.sleep', return_value=None):
            output = read_stream("sponsored_brands_campaigns", SyncMode.full_refresh, self._config)
        assert len(output.records) == 0

        error_logs = get_log_messages_by_log_level(output.logs, LogLevel.ERROR)
        assert any([breaking_error.build().get("message") in error for error in error_logs])

    @HttpMocker()
    def test_given_one_page_when_read_campaigns_then_return_records(self, http_mocker):
        """
        Check campaigns stream: normal full refresh sync without pagination
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        http_mocker.get(
            SponsoredBrandsRequestBuilder.campaigns_endpoint(self._config["client_id"], self._config["access_token"], self._config["profiles"][0], limit=100).build(),
            SponsoredBrandsResponseBuilder.campaigns_response().with_record(SponsoredBrandsRecordBuilder.campaigns_record()).build()
        )

        output = read_stream("sponsored_brands_campaigns", SyncMode.full_refresh, self._config)
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_many_pages_when_read_campaigns_then_return_records(self, http_mocker):
        """
        Check campaigns stream: normal full refresh sync with pagination
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        http_mocker.get(
            SponsoredBrandsRequestBuilder.campaigns_endpoint(self._config["client_id"], self._config["access_token"], self._config["profiles"][0], limit=100).build(),
            SponsoredBrandsResponseBuilder.campaigns_response(CountBasedPaginationStrategy()).with_record(SponsoredBrandsRecordBuilder.campaigns_record()).with_pagination().build()
        )
        http_mocker.get(
            SponsoredBrandsRequestBuilder.campaigns_endpoint(self._config["client_id"], self._config["access_token"], self._config["profiles"][0], limit=100, start_index=100).build(),
            SponsoredBrandsResponseBuilder.campaigns_response(CountBasedPaginationStrategy()).with_record(SponsoredBrandsRecordBuilder.campaigns_record()).with_pagination().build()
        )
        http_mocker.get(
            SponsoredBrandsRequestBuilder.campaigns_endpoint(self._config["client_id"], self._config["access_token"], self._config["profiles"][0], limit=100, start_index=200).build(),
            SponsoredBrandsResponseBuilder.campaigns_response().with_record(SponsoredBrandsRecordBuilder.campaigns_record()).build()
        )

        output = read_stream("sponsored_brands_campaigns", SyncMode.full_refresh, self._config)
        assert len(output.records) == 201

    @HttpMocker()
    def test_given_non_breaking_error_when_read_keywords_then_stream_is_ignored(self, http_mocker):
        """
        Check keywords stream: non-breaking errors are ignored
        When error of this kind happen, we warn and then keep syncing another streams
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        non_breaking_error = ErrorRecordBuilder.non_breaking_error()
        http_mocker.get(
            SponsoredBrandsRequestBuilder.keywords_endpoint(self._config["client_id"], self._config["access_token"], self._config["profiles"][0], limit=100).build(),
            ErrorResponseBuilder.non_breaking_error_response().with_record(non_breaking_error).with_status_code(400).build()
        )
        output = read_stream("sponsored_brands_keywords", SyncMode.full_refresh, self._config)
        assert len(output.records) == 0

        warning_logs = get_log_messages_by_log_level(output.logs, LogLevel.WARN)
        assert any([non_breaking_error.build().get("details") in worning for worning in warning_logs])

    @HttpMocker()
    def test_given_breaking_error_when_read_keywords_then_stream_stop_syncing(self, http_mocker):
        """
        Check keywords stream: when unknown error happen we stop syncing with raising the error
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        breaking_error = ErrorRecordBuilder.breaking_error()
        http_mocker.get(
            SponsoredBrandsRequestBuilder.keywords_endpoint(self._config["client_id"], self._config["access_token"], self._config["profiles"][0], limit=100).build(),
            ErrorResponseBuilder.breaking_error_response().with_record(breaking_error).with_status_code(500).build()
        )
        with patch('time.sleep', return_value=None):
            output = read_stream("sponsored_brands_keywords", SyncMode.full_refresh, self._config)
        assert len(output.records) == 0

        error_logs = get_log_messages_by_log_level(output.logs, LogLevel.ERROR)
        assert any([breaking_error.build().get("message") in error for error in error_logs])

    @HttpMocker()
    def test_given_one_page_when_read_keywords_then_return_records(self, http_mocker):
        """
        Check keywords stream: normal full refresh sync without pagination
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        http_mocker.get(
            SponsoredBrandsRequestBuilder.keywords_endpoint(self._config["client_id"], self._config["access_token"], self._config["profiles"][0], limit=100).build(),
            SponsoredBrandsResponseBuilder.keywords_response().with_record(SponsoredBrandsRecordBuilder.keywords_record()).build()
        )

        output = read_stream("sponsored_brands_keywords", SyncMode.full_refresh, self._config)
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_many_pages_when_read_keywords_then_return_records(self, http_mocker):
        """
        Check keywords stream: normal full refresh sync with pagination
        """
        self._given_oauth_and_profiles(http_mocker, self._config)

        http_mocker.get(
            SponsoredBrandsRequestBuilder.keywords_endpoint(self._config["client_id"], self._config["access_token"], self._config["profiles"][0], limit=100).build(),
            SponsoredBrandsResponseBuilder.keywords_response(CountBasedPaginationStrategy()).with_record(SponsoredBrandsRecordBuilder.keywords_record()).with_pagination().build()
        )
        http_mocker.get(
            SponsoredBrandsRequestBuilder.keywords_endpoint(self._config["client_id"], self._config["access_token"], self._config["profiles"][0], limit=100, start_index=100).build(),
            SponsoredBrandsResponseBuilder.keywords_response(CountBasedPaginationStrategy()).with_record(SponsoredBrandsRecordBuilder.keywords_record()).with_pagination().build()
        )
        http_mocker.get(
            SponsoredBrandsRequestBuilder.keywords_endpoint(self._config["client_id"], self._config["access_token"], self._config["profiles"][0], limit=100, start_index=200).build(),
            SponsoredBrandsResponseBuilder.keywords_response().with_record(SponsoredBrandsRecordBuilder.keywords_record()).build()
        )

        output = read_stream("sponsored_brands_keywords", SyncMode.full_refresh, self._config)
        assert len(output.records) == 201
