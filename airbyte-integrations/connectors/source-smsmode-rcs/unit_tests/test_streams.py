# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import requests_mock

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


def get_source(config):
    return YamlDeclarativeSource(path_to_yaml="manifest.yaml", config=config, catalog=None)


TEST_CONFIG = {"api_key": "fake-key", "start_date": "2025-01-01"}


def test_rcs_messages_stream_extracts_records(requests_mock):
    requests_mock.get(
        "https://rest.smsmode.com/rcs/v1/messages",
        json={"items": [{"messageId": "abc123", "from": "TestSender"}]},
    )
    source = get_source(TEST_CONFIG)
    streams = source.streams(config=TEST_CONFIG)
    rcs_stream = next(s for s in streams if s.name == "rcs_messages")
    records = list(rcs_stream.read_records(sync_mode="full_refresh"))
    assert len(records) == 1
    assert records[0]["messageId"] == "abc123"


def test_consumptions_rcs_stream_extracts_records(requests_mock):
    requests_mock.get(
        "https://rest.smsmode.com/commons/v1/consumptions",
        json={"items": [{"consumptionId": "cons-1", "quantity": 42}]},
    )
    source = get_source(TEST_CONFIG)
    streams = source.streams(config=TEST_CONFIG)
    consumptions_stream = next(s for s in streams if s.name == "consumptions_rcs")
    records = list(consumptions_stream.read_records(sync_mode="full_refresh"))
    assert len(records) == 1
    assert records[0]["consumptionId"] == "cons-1"


def test_api_key_sent_as_header_on_rcs_messages(requests_mock):
    mock = requests_mock.get("https://rest.smsmode.com/rcs/v1/messages", json={"items": []})
    source = get_source(TEST_CONFIG)
    streams = source.streams(config=TEST_CONFIG)
    rcs_stream = next(s for s in streams if s.name == "rcs_messages")
    list(rcs_stream.read_records(sync_mode="full_refresh"))
    assert mock.last_request.headers["X-Api-Key"] == "fake-key"
