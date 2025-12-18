# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import FieldPath
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import SatisfactionRatingsRecordBuilder, SatisfactionRatingsResponseBuilder
from .utils import datetime_to_string, read_stream, string_to_datetime


_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))


@freezegun.freeze_time(_NOW.isoformat())
class TestSatisfactionRatingsStreamFullRefresh(TestCase):
    @property
    def _config(self):
        return (
            ConfigBuilder()
            .with_basic_auth_credentials("user@example.com", "password")
            .with_subdomain("d3v-airbyte")
            .with_start_date(_START_DATE)
            .build()
        )

    def _get_authenticator(self, config):
        return ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])

    @HttpMocker()
    def test_given_one_page_when_read_satisfaction_ratings_then_return_records(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        http_mocker.get(
            ZendeskSupportRequestBuilder.satisfaction_ratings_endpoint(api_token_authenticator)
            .with_sort("created_at")
            .with_page_size(100)
            .with_start_time(self._config["start_date"])
            .build(),
            SatisfactionRatingsResponseBuilder.satisfaction_ratings_response()
            .with_record(SatisfactionRatingsRecordBuilder.satisfaction_ratings_record())
            .build(),
        )

        output = read_stream("satisfaction_ratings", SyncMode.full_refresh, self._config)

        assert len(output.records) == 1


@freezegun.freeze_time(_NOW.isoformat())
class TestSatisfactionRatingsStreamIncremental(TestCase):
    @property
    def _config(self):
        return (
            ConfigBuilder()
            .with_basic_auth_credentials("user@example.com", "password")
            .with_subdomain("d3v-airbyte")
            .with_start_date(_START_DATE)
            .build()
        )

    def _get_authenticator(self, config):
        return ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])

    @HttpMocker()
    def test_given_no_state_when_read_satisfaction_ratings_then_return_records_and_emit_state(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])
        cursor_value = datetime_to_string(start_date.add(timedelta(days=1)))

        http_mocker.get(
            ZendeskSupportRequestBuilder.satisfaction_ratings_endpoint(api_token_authenticator)
            .with_sort("created_at")
            .with_page_size(100)
            .with_start_time(self._config["start_date"])
            .build(),
            SatisfactionRatingsResponseBuilder.satisfaction_ratings_response()
            .with_record(SatisfactionRatingsRecordBuilder.satisfaction_ratings_record().with_field(FieldPath("updated_at"), cursor_value))
            .build(),
        )

        output = read_stream("satisfaction_ratings", SyncMode.incremental, self._config)

        assert len(output.records) == 1
        assert output.most_recent_state is not None
        assert output.most_recent_state.stream_descriptor.name == "satisfaction_ratings"

    @HttpMocker()
    def test_given_state_when_read_satisfaction_ratings_then_use_state_cursor(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        state_cursor_value = _START_DATE.add(timedelta(days=30))
        new_cursor_value = datetime_to_string(state_cursor_value.add(timedelta(days=1)))

        http_mocker.get(
            ZendeskSupportRequestBuilder.satisfaction_ratings_endpoint(api_token_authenticator)
            .with_sort("created_at")
            .with_page_size(100)
            .with_start_time(datetime_to_string(state_cursor_value))
            .build(),
            SatisfactionRatingsResponseBuilder.satisfaction_ratings_response()
            .with_record(
                SatisfactionRatingsRecordBuilder.satisfaction_ratings_record().with_field(FieldPath("updated_at"), new_cursor_value)
            )
            .build(),
        )

        state = StateBuilder().with_stream_state("satisfaction_ratings", {"updated_at": datetime_to_string(state_cursor_value)}).build()

        output = read_stream("satisfaction_ratings", SyncMode.incremental, self._config, state)

        assert len(output.records) == 1
        assert output.most_recent_state is not None
        assert output.most_recent_state.stream_descriptor.name == "satisfaction_ratings"
