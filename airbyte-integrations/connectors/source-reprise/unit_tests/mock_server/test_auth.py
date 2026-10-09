# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""SessionTokenAuthenticator behaviour: portal API token in, warehouse JWT out."""

from unittest import TestCase

import freezegun
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover, read
from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.helpers import (
    API_TOKEN,
    NOW,
    SESSION_TOKEN,
    config,
    data_request,
    data_response,
    login_request,
    login_response,
)


_STREAM_NAME = "replay_change_feed"
_RECORD = {
    "entity_id": "entity-1",
    "changed_at": "2026-08-20 01:00:00",
    "change_type": "updated",
    "entity_type": "replay",
    "ingested_at": "2026-08-20 01:30:00",
}


@freezegun.freeze_time(NOW)
class TestWarehouseTokenAuth(TestCase):
    @HttpMocker()
    def test_given_api_token_when_read_then_login_uses_bearer_header_and_data_request_carries_session_token(
        self, http_mocker: HttpMocker
    ) -> None:
        # The login mock only matches when the connector sends `Authorization: Bearer <api_token>`.
        login = login_request(API_TOKEN)
        # The data mock only matches when `token` equals the value read from the login response body.
        data = data_request(_STREAM_NAME, session_token=SESSION_TOKEN)
        http_mocker.post(login, login_response(SESSION_TOKEN))
        http_mocker.get(data, data_response([_RECORD]))

        output = read(
            get_source(config=config()),
            config=config(),
            catalog=CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build(),
        )

        assert output.errors == []
        assert len(output.records) == 1
        http_mocker.assert_number_of_calls(login, 1)
        http_mocker.assert_number_of_calls(data, 1)

    @HttpMocker()
    def test_given_custom_api_token_when_read_then_that_token_is_forwarded_to_login(self, http_mocker: HttpMocker) -> None:
        # A different api_token must reach the login endpoint verbatim, and a different session
        # token must reach the data endpoint verbatim. Any hardcoding in the manifest breaks this.
        custom_config = config(api_token="another-portal-token")
        login = login_request("another-portal-token")
        data = data_request(_STREAM_NAME, session_token="another-session-jwt")
        http_mocker.post(login, login_response("another-session-jwt"))
        http_mocker.get(data, data_response([_RECORD]))

        output = read(
            get_source(config=custom_config),
            config=custom_config,
            catalog=CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build(),
        )

        assert output.errors == []
        assert len(output.records) == 1

    def test_discover_exposes_all_five_streams(self) -> None:
        output = discover(get_source(config=config()), config=config())

        catalog = output.catalog.catalog
        assert sorted(stream.name for stream in catalog.streams) == [
            "replay_change_feed",
            "replay_metrics",
            "replay_session_activity",
            "replay_session_summary",
            "replicate_session_activity",
        ]
        cursor_fields = {stream.name: stream.default_cursor_field for stream in catalog.streams}
        assert cursor_fields == {
            "replay_session_activity": ["since_created_at"],
            "replay_session_summary": ["since_created_at"],
            "replay_metrics": ["window_start"],
            "replay_change_feed": ["since_ingested_at"],
            "replicate_session_activity": ["since_created_at"],
        }
