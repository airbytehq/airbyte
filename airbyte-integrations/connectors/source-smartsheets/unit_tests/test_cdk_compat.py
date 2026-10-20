#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import hashlib
import json
import logging
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock
from urllib.parse import parse_qs

from source_smartsheets.sheet import SmartSheetAPIWrapper
from source_smartsheets.source import SourceSmartsheets

from airbyte_cdk.models import (
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStream,
    AirbyteStreamState,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    StreamDescriptor,
    SyncMode,
    Type,
)


TOKEN_ENDPOINT = "https://api.smartsheet.com/2.0/token"


def test_oauth_refresh_updates_rotated_credentials(requests_mock):
    config = {
        "spreadsheet_id": "id",
        "credentials": {
            "auth_type": "oauth2.0",
            "client_id": "cid",
            "client_secret": "secret",
            "refresh_token": "old_rt",
            "access_token": "old_at",
            "token_expiry_date": "2020-01-01T00:00:00+00:00",
        },
    }
    requests_mock.post(TOKEN_ENDPOINT, json={"access_token": "new_at", "refresh_token": "new_rt", "expires_in": 3600})

    access_token = SmartSheetAPIWrapper(config).get_access_token(config)

    assert access_token == "new_at"
    assert config["credentials"]["refresh_token"] == "new_rt"
    assert config["credentials"]["access_token"] == "new_at"
    assert datetime.fromisoformat(config["credentials"]["token_expiry_date"]) > datetime.now(timezone.utc)

    request_body = requests_mock.last_request.text
    try:
        request_body = json.loads(request_body)
    except json.JSONDecodeError:
        request_body = {key: value[0] for key, value in parse_qs(request_body).items()}
    expected_request_fields = {
        "grant_type": "refresh_token",
        "refresh_token": "old_rt",
        "client_id": "cid",
        "client_secret": "secret",
        "hash": hashlib.sha256(b"secret|old_rt").hexdigest(),
    }
    for field, value in expected_request_fields.items():
        assert request_body[field] == value


def test_oauth_does_not_refresh_non_expired_token(requests_mock):
    config = {
        "spreadsheet_id": "id",
        "credentials": {
            "auth_type": "oauth2.0",
            "client_id": "cid",
            "client_secret": "secret",
            "refresh_token": "rt",
            "access_token": "at",
            "token_expiry_date": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        },
    }

    assert SmartSheetAPIWrapper(config).get_access_token(config) == "at"
    assert requests_mock.call_count == 0


def test_read_uses_incremental_stream_state_with_cdk_7(mocker):
    stream_name = "aws_s3_sample"
    incoming_state = {"modifiedAt": "2021-01-01T00:00:00+00:00"}
    records = [
        {"id": "1", "modifiedAt": "2021-01-02T00:00:00+00:00"},
        {"id": "2", "modifiedAt": "2021-01-03T00:00:00+00:00"},
    ]
    smartsheet = Mock()
    smartsheet.name = stream_name
    smartsheet.is_report = False
    smartsheet.primary_key = "id"
    smartsheet.json_schema = {
        "type": "object",
        "properties": {"id": {"type": "string"}, "modifiedAt": {"type": "string", "format": "date-time"}},
    }
    smartsheet.read_records.return_value = records
    mocker.patch("source_smartsheets.source.SmartSheetAPIWrapper", return_value=smartsheet)

    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name=stream_name,
                    json_schema=smartsheet.json_schema,
                    supported_sync_modes=[SyncMode.incremental],
                ),
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.append,
                cursor_field=["modifiedAt"],
            )
        ]
    )
    state = [
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name=stream_name),
                stream_state=AirbyteStateBlob(**incoming_state),
            ),
        )
    ]

    messages = list(SourceSmartsheets().read(logging.getLogger(), {"spreadsheet_id": "id"}, catalog, state))

    emitted_records = [message.record.data for message in messages if message.type == Type.RECORD]
    assert emitted_records == records
    smartsheet.read_records.assert_called_once_with(incoming_state["modifiedAt"])

    state_messages = [message.state for message in messages if message.type == Type.STATE]
    assert state_messages[-1].stream.stream_state.__dict__ == {"modifiedAt": "2021-01-03T00:00:00+00:00"}
