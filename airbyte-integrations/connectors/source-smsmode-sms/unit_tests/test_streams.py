# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import requests_mock

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


def get_source(config):
    return YamlDeclarativeSource(path_to_yaml="manifest.yaml", config=config, catalog=None)


def test_messages_stream_extracts_records(requests_mock):
    requests_mock.get(
        "https://rest.smsmode.com/sms/v1/messages",
        json={"items": [{"messageId": "123", "from": "Test"}]},
    )
    source = get_source({"api_key": "fake-key"})
    streams = source.streams(config={"api_key": "fake-key"})
    messages_stream = next(s for s in streams if s.name == "messages")
    records = list(messages_stream.read_records(sync_mode="full_refresh"))
    assert len(records) == 1
    assert records[0]["messageId"] == "123"


def test_api_key_sent_as_header(requests_mock):
    mock = requests_mock.get("https://rest.smsmode.com/sms/v1/messages", json={"items": []})
    source = get_source({"api_key": "fake-key"})
    streams = source.streams(config={"api_key": "fake-key"})
    messages_stream = next(s for s in streams if s.name == "messages")
    list(messages_stream.read_records(sync_mode="full_refresh"))
    assert mock.last_request.headers["X-Api-Key"] == "fake-key"
