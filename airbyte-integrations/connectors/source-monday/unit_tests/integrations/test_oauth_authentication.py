# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from unittest import TestCase
from urllib.parse import parse_qs

from airbyte_cdk.models import SyncMode, Type
from airbyte_cdk.test.mock_http import HttpMocker

from .config import ConfigBuilder
from .monday_requests import TeamsRequestBuilder
from .monday_requests.request_authenticators import ApiTokenAuthenticator
from .monday_responses import TeamsResponseBuilder
from .monday_responses.records import TeamsRecordBuilder
from .utils import read_stream


_TOKEN_REFRESH_ENDPOINT = "https://auth.monday.com/oauth_ms/oauth/token"


_TOKEN_RESPONSE = {"access_token": "new-access", "refresh_token": "new-refresh", "token_type": "Bearer", "scope": "boards:read"}


class TestOAuthAuthentication(TestCase):
    @HttpMocker()
    def test_given_expired_token_when_read_then_refresh_token_and_emit_control_message(self, http_mocker):
        config = (
            ConfigBuilder()
            .with_oauth_credentials(
                client_id="client-id",
                client_secret="client-secret",
                access_token="stale-access",
                subdomain="airbyte",
                refresh_token="old-refresh",
            )
            .build()
        )

        http_mocker.post(
            TeamsRequestBuilder.teams_endpoint(ApiTokenAuthenticator("new-access")).build(),
            TeamsResponseBuilder.teams_response().with_record(TeamsRecordBuilder.teams_record()).build(),
        )
        # Registered last so requests_mock (reverse order) matches the token URL before the teams matcher, whose
        # JSON body matcher would otherwise choke on the form-encoded refresh payload.
        http_mocker._mocker.post(_TOKEN_REFRESH_ENDPOINT, json=_TOKEN_RESPONSE)

        output = read_stream("teams", SyncMode.full_refresh, config)

        assert len(output.records) == 1

        token_request_body = parse_qs(
            next(request.body for request in http_mocker._mocker.request_history if request.url == _TOKEN_REFRESH_ENDPOINT)
        )
        assert token_request_body["grant_type"] == ["refresh_token"]
        assert token_request_body["refresh_token"] == ["old-refresh"]
        assert token_request_body["client_id"] == ["client-id"]
        assert token_request_body["client_secret"] == ["client-secret"]

        control_messages = output.get_message_by_types([Type.CONTROL])
        assert len(control_messages) == 1
        updated_credentials = control_messages[0].control.connectorConfig.config["credentials"]
        assert updated_credentials["access_token"] == "new-access"
        assert updated_credentials["refresh_token"] == "new-refresh"
        assert updated_credentials["token_expiry_date"]

    @HttpMocker()
    def test_given_api_token_config_when_read_then_no_token_refresh(self, http_mocker):
        config = ConfigBuilder().with_api_token_credentials("api-token").build()

        http_mocker.post(
            TeamsRequestBuilder.teams_endpoint(ApiTokenAuthenticator("api-token")).build(),
            TeamsResponseBuilder.teams_response().with_record(TeamsRecordBuilder.teams_record()).build(),
        )

        output = read_stream("teams", SyncMode.full_refresh, config)

        assert len(output.records) == 1
        assert output.get_message_by_types([Type.CONTROL]) == []
