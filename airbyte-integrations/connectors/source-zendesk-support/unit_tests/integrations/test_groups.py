# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .helpers import given_groups_with_later_records
from .utils import datetime_to_string, read_stream, string_to_datetime
from .zs_requests.request_authenticators import ApiTokenAuthenticator


_NOW = ab_datetime_now()


class TestGroupsStreamFullRefresh(TestCase):
    @property
    def _config(self):
        return (
            ConfigBuilder()
            .with_basic_auth_credentials("user@example.com", "password")
            .with_subdomain("d3v-airbyte")
            .with_start_date(ab_datetime_now().subtract(timedelta(weeks=104)))
            .build()
        )

    @staticmethod
    def get_authenticator(config):
        return ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])

    @HttpMocker()
    def test_given_incoming_state_semi_incremental_groups_does_not_emit_earlier_record(self, http_mocker):
        """
        Perform a semi-incremental sync where records that came before the current state are not included in the set
        of records emitted
        """
        api_token_authenticator = self.get_authenticator(self._config)
        given_groups_with_later_records(
            http_mocker,
            string_to_datetime(self._config["start_date"]),
            timedelta(weeks=12),
            api_token_authenticator,
        )

        output = read_stream("groups", SyncMode.full_refresh, self._config)
        assert len(output.records) == 2

    @HttpMocker()
    def test_given_incoming_state_semi_incremental_groups_does_not_emit_earlier_record(self, http_mocker):
        """
        Perform a semi-incremental sync where records that came before the current state are not included in the set
        of records emitted
        """
        api_token_authenticator = self.get_authenticator(self._config)
        given_groups_with_later_records(
            http_mocker,
            string_to_datetime(self._config["start_date"]),
            timedelta(weeks=12),
            api_token_authenticator,
        )

        state_value = {"updated_at": datetime_to_string(ab_datetime_now().subtract(timedelta(weeks=102)))}

        state = StateBuilder().with_stream_state("groups", state_value).build()

        output = read_stream("groups", SyncMode.full_refresh, self._config, state=state)
        assert len(output.records) == 1
