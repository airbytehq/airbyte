#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
import logging
from urllib.parse import parse_qs

import requests_mock
from source_microsoft_dataverse import SourceMicrosoftDataverse

from airbyte_cdk.models import AirbyteStateMessageSerializer, ConfiguredAirbyteCatalogSerializer, SyncMode, Type


CONFIG = {
    "url": "https://org.crm.dynamics.com",
    "tenant_id": "tenant",
    "client_id": "client",
    "client_secret_value": "secret",
    "odata_maxpagesize": 5000,
}
API_URL = f"{CONFIG['url']}/api/data/v9.2/"


def _catalog(sync_mode):
    stream = {
        "stream": {
            "name": "account",
            "json_schema": {
                "properties": {
                    "accountid": {"type": "string"},
                    "modifiedon": {"type": "string"},
                }
            },
            "supported_sync_modes": ["full_refresh", "incremental"],
            "source_defined_cursor": True,
            "default_cursor_field": ["modifiedon"],
            "source_defined_primary_key": [["accountid"]],
        },
        "sync_mode": sync_mode.value,
        "destination_sync_mode": "append" if sync_mode == SyncMode.incremental else "overwrite",
        "primary_key": [["accountid"]],
    }
    if sync_mode == SyncMode.incremental:
        stream["cursor_field"] = ["modifiedon"]
    return ConfiguredAirbyteCatalogSerializer.load({"streams": [stream]})


def _run_read(sync_mode, stream_state=None):
    state = []
    if stream_state is not None:
        state = [
            AirbyteStateMessageSerializer.load(
                {
                    "type": "STREAM",
                    "stream": {
                        "stream_descriptor": {"name": "account"},
                        "stream_state": stream_state,
                    },
                }
            )
        ]

    with requests_mock.Mocker() as mock:
        mock.post(
            f"https://login.microsoftonline.com/{CONFIG['tenant_id']}/oauth2/v2.0/token",
            json={"access_token": "token", "expires_in": 3600},
        )
        mock.get(
            f"{API_URL}EntityDefinitions(LogicalName='account')?$select=EntitySetName",
            json={"EntitySetName": "accounts"},
        )

        account_request_urls = []

        def account_response(request, context):
            account_request_urls.append(request.url)
            if "skiptoken=PAGE2" in request.url:
                return {
                    "value": [{"accountid": "2", "modifiedon": "2024-01-02"}],
                    "@odata.deltaLink": f"{API_URL}accounts?$deltatoken=DT2",
                }
            if "deltatoken=DT1" in request.url:
                return {
                    "value": [{"accountid": "3", "modifiedon": "2024-01-03"}],
                    "@odata.deltaLink": f"{API_URL}accounts?$deltatoken=DT3",
                }
            if len(account_request_urls) > 1:
                return {
                    "value": [{"accountid": "2", "modifiedon": "2024-01-02"}],
                    "@odata.deltaLink": f"{API_URL}accounts?$deltatoken=DT2",
                }
            return {
                "value": [{"accountid": "1", "modifiedon": "2024-01-01"}],
                "@odata.nextLink": f"{API_URL}accounts?$skiptoken=PAGE2",
            }

        mock.get(f"{API_URL}accounts", json=account_response)
        messages = list(SourceMicrosoftDataverse().read(logging.getLogger("test"), CONFIG, _catalog(sync_mode), state))
        account_requests = [request.url for request in mock.request_history if request.url.startswith(f"{API_URL}accounts")]
        token_request = next(request for request in mock.request_history if request.method == "POST")

    records = [message for message in messages if message.type == Type.RECORD]
    states = [message.state.stream.stream_state.__dict__ for message in messages if message.type == Type.STATE]
    token_body = parse_qs(token_request.text)
    return account_requests, records, states, token_body


def test_full_refresh_ignores_incoming_state_and_does_not_checkpoint_pages():
    expected_requests = [
        f"{API_URL}accounts",
        f"{API_URL}accounts?%24skiptoken=PAGE2",
    ]
    for incoming_state in (None, {"$deltatoken": "DT1"}):
        account_requests, records, states, token_body = _run_read(SyncMode.full_refresh, incoming_state)
        assert account_requests == expected_requests
        assert len(records) == 2
        assert states == [{"__ab_no_cursor_state_message": True}]
        assert token_body["grant_type"] == ["client_credentials"]
        assert token_body["scope"] == [f"{CONFIG['url']}/.default"]


def test_incremental_without_state_starts_at_first_page():
    account_requests, records, states, token_body = _run_read(SyncMode.incremental)
    assert account_requests == [
        f"{API_URL}accounts",
        f"{API_URL}accounts?%24skiptoken=PAGE2",
    ]
    assert len(records) == 2
    assert states == [{"$deltatoken": "DT2"}]
    assert token_body["grant_type"] == ["client_credentials"]
    assert token_body["scope"] == [f"{CONFIG['url']}/.default"]


def test_incremental_with_state_uses_delta_token():
    account_requests, records, states, token_body = _run_read(SyncMode.incremental, {"$deltatoken": "DT1"})
    assert account_requests == [f"{API_URL}accounts?%24deltatoken=DT1"]
    assert len(records) == 1
    assert states == [{"$deltatoken": "DT3"}]
    assert token_body["grant_type"] == ["client_credentials"]
    assert token_body["scope"] == [f"{CONFIG['url']}/.default"]
