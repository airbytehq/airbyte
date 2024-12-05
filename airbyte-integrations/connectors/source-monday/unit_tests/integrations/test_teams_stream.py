# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase
from unittest.mock import patch

from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_protocol.models import Level as LogLevel
from airbyte_protocol.models import SyncMode

from .config import ConfigBuilder
from .monday_requests import TeamsRequestBuilder
from .monday_requests.request_authenticators import ApiTokenAuthenticator
from .monday_responses import ErrorResponseBuilder, TeamsResponseBuilder
from .monday_responses.records import TeamsRecordBuilder
from .utils import get_log_messages_by_log_level, read_stream


class TestTeamsStreamFullRefresh(TestCase):
    @property
    def _config(self):
        return ConfigBuilder().with_api_token_credentials("api-token").build()

    def get_authenticator(self, config):
        return ApiTokenAuthenticator(api_token=config["credentials"]["api_token"])

    @HttpMocker()
    def test_given_one_page_when_read_teams_then_return_records(self, http_mocker):
        """
        A normal full refresh sync without pagination
        """
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            TeamsRequestBuilder.teams_endpoint(api_token_authenticator).build(),
            TeamsResponseBuilder.teams_response().with_record(TeamsRecordBuilder.teams_record()).build(),
        )

        output = read_stream("teams", SyncMode.full_refresh, self._config)
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_retryable_error_and_one_page_when_read_teams_then_return_records(self, http_mocker):
        """
        A full refresh sync without pagination completes successfully after one retry
        """
        test_cases = [
            ("200_ComplexityException", "ComplexityException"),
            ("200_complexityBudgetExhausted", "complexityBudgetExhausted"),
        ]
        for test_values in test_cases:
            response, error_code = test_values[0], test_values[1]
            api_token_authenticator = self.get_authenticator(self._config)

            http_mocker.get(
                TeamsRequestBuilder.teams_endpoint(api_token_authenticator).build(),
                [
                    ErrorResponseBuilder.response_with_status(200).build(response),
                    TeamsResponseBuilder.teams_response().with_record(TeamsRecordBuilder.teams_record()).build(),
                ],
            )

            with patch("time.sleep", return_value=None):
                output = read_stream("teams", SyncMode.full_refresh, self._config)

            assert len(output.records) == 1

            error_logs = [
                error
                for error in get_log_messages_by_log_level(output.logs, LogLevel.INFO)
                if f'Response Code: 200, Response Text: {json.dumps({"error_code": error_code, "status_code": 200})}' in error
            ]
            assert len(error_logs) == 1

    @HttpMocker()
    def test_given_retryable_error_when_read_teams_then_stop_syncing(self, http_mocker):
        """
        A full refresh sync without pagination give up after 6 retries
        """
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            TeamsRequestBuilder.teams_endpoint(api_token_authenticator).build(), ErrorResponseBuilder.response_with_status(200).build()
        )

        with patch("time.sleep", return_value=None):
            output = read_stream("teams", SyncMode.full_refresh, self._config)

        assert len(output.records) == 0

        error_logs = [
            error
            for error in get_log_messages_by_log_level(output.logs, LogLevel.INFO)
            if f'Response Code: 200, Response Text: {json.dumps({"error_code": "ComplexityException", "status_code": 200})}' in error
        ]
        assert len(error_logs) == 6

    @HttpMocker()
    def test_given_retryable_500_error_when_read_teams_then_stop_syncing(self, http_mocker):
        """
        A full refresh sync without pagination give up after 6 retries
        """
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            TeamsRequestBuilder.teams_endpoint(api_token_authenticator).build(), ErrorResponseBuilder.response_with_status(500).build()
        )

        with patch("time.sleep", return_value=None):
            output = read_stream("teams", SyncMode.full_refresh, self._config)

        assert len(output.records) == 0

        error_logs = [
            error
            for error in get_log_messages_by_log_level(output.logs, LogLevel.INFO)
            if f'Response Code: 500, Response Text: {json.dumps({"error_message": "Internal server error", "status_code": 500})}' in error
        ]
        assert len(error_logs) == 6

    @HttpMocker()
    def test_given_403_error_when_read_teams_then_ignore_the_stream(self, http_mocker):
        """
        A full refresh sync without pagination ignore failed stream
        """
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            TeamsRequestBuilder.teams_endpoint(api_token_authenticator).build(), ErrorResponseBuilder.response_with_status(403).build()
        )

        with patch("time.sleep", return_value=None):
            output = read_stream("teams", SyncMode.full_refresh, self._config)

        assert len(output.records) == 0

        error_logs = [
            error
            for error in get_log_messages_by_log_level(output.logs, LogLevel.INFO)
            if "Ignoring response for failed request with error message None" in error
        ]
        assert len(error_logs) == 1
