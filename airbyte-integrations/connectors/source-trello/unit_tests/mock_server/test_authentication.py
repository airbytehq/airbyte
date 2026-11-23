# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timedelta, timezone

import pytest

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.models.outcome import ExpectedOutcome
from mock_server.config import API_KEY, API_TOKEN, CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, START_DATE, ConfigBuilder
from mock_server.request_builder import PAGINATED_STREAMS, STREAM_ENDPOINTS, TrelloRequestBuilder, refresh_request
from mock_server.response_builder import TrelloResponseBuilder


BOARD_ID = "5f1e2d3c4b5a69788796a5b4"
STORED_ACCESS_TOKEN = "access-token-1"
NEW_ACCESS_TOKEN = "access-token-2"
NEW_REFRESH_TOKEN = "refresh-token-2"


def emitted_configs(stdout: str) -> list[dict]:
    """The configs of the CONNECTOR_CONFIG control messages the connector printed."""
    configs = []
    for line in stdout.splitlines():
        try:
            message = json.loads(line)
        except ValueError:
            continue
        if isinstance(message, dict) and message.get("type") == "CONTROL":
            configs.append(message["control"]["connectorConfig"]["config"])
    return configs


def catalog_of(*streams: str):
    catalog = CatalogBuilder()
    for stream in streams:
        catalog = catalog.with_stream(stream, SyncMode.full_refresh)
    return catalog.build()


@pytest.mark.parametrize(
    ("config", "expected_configs"),
    [
        pytest.param(
            ConfigBuilder().build(),
            # The top-level fields stay, so the migrated config still works on versions before 1.4.0.
            [
                {
                    "key": API_KEY,
                    "token": API_TOKEN,
                    "start_date": START_DATE,
                    "credentials": {"key": API_KEY, "token": API_TOKEN, "auth_type": "api_key"},
                }
            ],
            id="flat_config_of_earlier_versions_is_migrated",
        ),
        pytest.param(ConfigBuilder().with_api_key_credentials().build(), [], id="credentials_config_is_left_as_is"),
    ],
)
def test_api_key_and_token_authenticate_from_either_config_shape(source_factory, capsys, config, expected_configs):
    requests = TrelloRequestBuilder(config)
    catalog = catalog_of("boards")

    with HttpMocker() as http_mocker:
        boards = requests.parent("boards")
        http_mocker.get(boards, TrelloResponseBuilder.records([{"id": BOARD_ID}]))

        output = read(source_factory(config, catalog), config=config, catalog=catalog)

        assert [message.record.data["id"] for message in output.records] == [BOARD_ID]
        http_mocker.assert_number_of_calls(boards, 1)
    assert emitted_configs(capsys.readouterr().out) == expected_configs


def test_oauth_sync_of_every_stream_refreshes_once_and_persists_the_rotated_tokens(source_factory, capsys):
    # Trello refresh tokens are single use: a second refresh with the same token would break the chain.
    config = ConfigBuilder().with_oauth_credentials().build()
    requests = TrelloRequestBuilder(config, authorization=f"Bearer {NEW_ACCESS_TOKEN}")
    response = TrelloResponseBuilder.records
    catalog = catalog_of(*STREAM_ENDPOINTS)

    with HttpMocker() as http_mocker:
        refresh = refresh_request(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN)
        http_mocker.post(refresh, TrelloResponseBuilder.tokens(NEW_ACCESS_TOKEN, NEW_REFRESH_TOKEN))
        # Every request must carry the refreshed bearer token: a request with any other header matches nothing.
        http_mocker.get(requests.parent("boards"), response([{"id": BOARD_ID}]))
        http_mocker.get(requests.parent("organizations"), response([{"id": "organizations-1", "idBoards": [BOARD_ID]}]))
        board_requests = []
        for stream in STREAM_ENDPOINTS:
            if stream in ("boards", "organizations"):
                continue
            board_requests.append(requests.stream(stream, BOARD_ID))
            http_mocker.get(board_requests[-1], response([{"id": f"{stream}-1", "date": "2024-02-01T00:00:00.000Z"}]))
            if stream in PAGINATED_STREAMS:
                http_mocker.get(requests.stream(stream, BOARD_ID, before=f"{stream}-1"), response([]))

        output = read(source_factory(config, catalog), config=config, catalog=catalog)

        assert not output.errors
        assert sorted((message.record.stream, message.record.data["id"]) for message in output.records) == sorted(
            [("boards", BOARD_ID), ("organizations", "organizations-1")]
            + [(stream, f"{stream}-1") for stream in STREAM_ENDPOINTS if stream not in ("boards", "organizations")]
        )
        http_mocker.assert_number_of_calls(refresh, 1)
        for request in board_requests:
            http_mocker.assert_number_of_calls(request, 1)

    [emitted] = emitted_configs(capsys.readouterr().out)
    credentials = emitted["credentials"]
    expiry = datetime.fromisoformat(credentials.pop("token_expiry_date").replace("Z", "+00:00"))
    assert credentials == {
        "auth_type": "oauth2.0",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": NEW_REFRESH_TOKEN,
        "access_token": NEW_ACCESS_TOKEN,
    }
    # The expiry is computed from the clock at refresh time, so only its distance from now is fixed.
    assert timedelta(minutes=59) < expiry - datetime.now(timezone.utc) <= timedelta(hours=1)
    assert {key: value for key, value in emitted.items() if key != "credentials"} == {"start_date": START_DATE}


def test_oauth_access_token_rejected_before_its_expiry_is_refreshed_once_and_retried(source_factory, capsys, sleeps):
    # The connector refreshes only after the stored expiry, so a token Trello already rejects comes back as a 401.
    token_expiry_date = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
    config = ConfigBuilder().with_oauth_credentials(access_token=STORED_ACCESS_TOKEN, token_expiry_date=token_expiry_date).build()
    catalog = catalog_of("boards")

    with HttpMocker() as http_mocker:
        with_stored_token = TrelloRequestBuilder(config, authorization=f"Bearer {STORED_ACCESS_TOKEN}").parent("boards")
        with_new_token = TrelloRequestBuilder(config, authorization=f"Bearer {NEW_ACCESS_TOKEN}").parent("boards")
        refresh = refresh_request(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN)
        http_mocker.get(with_stored_token, TrelloResponseBuilder.bearer_rejected())
        http_mocker.post(refresh, TrelloResponseBuilder.tokens(NEW_ACCESS_TOKEN, NEW_REFRESH_TOKEN))
        http_mocker.get(with_new_token, TrelloResponseBuilder.records([{"id": BOARD_ID}]))

        output = read(source_factory(config, catalog), config=config, catalog=catalog)

        assert [message.record.data["id"] for message in output.records] == [BOARD_ID]
        http_mocker.assert_number_of_calls(with_stored_token, 1)
        http_mocker.assert_number_of_calls(refresh, 1)
        http_mocker.assert_number_of_calls(with_new_token, 1)
    assert [emitted["credentials"]["refresh_token"] for emitted in emitted_configs(capsys.readouterr().out)] == [NEW_REFRESH_TOKEN]


@pytest.mark.parametrize(
    ("status_code", "error", "message"),
    [
        (
            400,
            "invalid_grant",
            "Trello rejected the OAuth 2.0 refresh token because it expired, was revoked or was already used. "
            "Re-authenticate with Trello in the source settings.",
        ),
        (
            403,
            "invalid_grant",
            "Trello rejected the OAuth 2.0 refresh token because it expired, was revoked or was already used. "
            "Re-authenticate with Trello in the source settings.",
        ),
        (
            403,
            "unauthorized_client",
            "Trello rejected the OAuth 2.0 refresh token or client. Re-authenticate with Trello in the source settings.",
        ),
        (
            401,
            "invalid_client",
            "Trello rejected the OAuth 2.0 client ID or client secret. Re-authenticate with Trello in the source settings.",
        ),
    ],
)
def test_rejected_refresh_token_fails_as_a_config_error_without_calling_trello(source_factory, status_code, error, message):
    config = ConfigBuilder().with_oauth_credentials().build()
    catalog = catalog_of("boards")

    with HttpMocker() as http_mocker:
        refresh = refresh_request(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN)
        boards = TrelloRequestBuilder(config, authorization=f"Bearer {NEW_ACCESS_TOKEN}").parent("boards")
        http_mocker.post(refresh, TrelloResponseBuilder.token_error(status_code, error))
        http_mocker.get(boards, TrelloResponseBuilder.records([{"id": BOARD_ID}]))

        output = read(source_factory(config, catalog), config=config, catalog=catalog, expected_outcome=ExpectedOutcome.EXPECT_EXCEPTION)

        http_mocker.assert_number_of_calls(refresh, 1)
        http_mocker.assert_number_of_calls(boards, 0)
    error_trace = output.errors[0].trace.error
    assert error_trace.failure_type == FailureType.config_error
    assert error_trace.message == f"{message} Provider error: {error}"
