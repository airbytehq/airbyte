# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import datetime, timedelta, timezone
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder

from .config import ConfigBuilder
from .helpers import given_groups_with_later_records
from .utils import create_duration, datetime_to_string, now_utc, read_stream, string_to_datetime
from .zs_requests.request_authenticators import ApiTokenAuthenticator


_NOW = datetime.now(timezone.utc)


class TestGroupsStreamFullRefresh(TestCase):
    @property
    def _config(self):
        return (
            ConfigBuilder()
            .with_basic_auth_credentials("user@example.com", "password")
            .with_subdomain("d3v-airbyte")
            .with_start_date(now_utc().replace(year=now_utc().year - 2))
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
            create_duration(weeks=12),
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
            create_duration(weeks=12),
            api_token_authenticator,
        )

        now = now_utc()
        state_value = {"updated_at": datetime_to_string(now.replace(year=now.year - 1) - timedelta(weeks=50))}

        state = StateBuilder().with_stream_state("groups", state_value).build()

        output = read_stream("groups", SyncMode.full_refresh, self._config, state=state)
        assert len(output.records) == 1
