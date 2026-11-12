#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime
from typing import Any, Mapping

from source_adjust.source import SourceAdjust

from airbyte_cdk.models import ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode, Type
from airbyte_cdk.sources.streams import Stream


def get_stream_by_name(stream_name: str, config: Mapping[str, Any]) -> Stream:
    source = SourceAdjust(config=config, catalog=None, state=None)
    matches_by_name = [stream_config for stream_config in source.streams(config) if stream_config.name == stream_name]
    if not matches_by_name:
        raise ValueError("Please provide a valid stream name.")
    return matches_by_name[0]


def read_messages(config: Mapping[str, Any]):
    source = SourceAdjust(config=config, catalog=None, state=None)
    stream = get_stream_by_name("AdjustReport", config)
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=stream.as_airbyte_stream(),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            )
        ]
    )
    return list(source.read(logging.getLogger(), config, catalog, []))


def config_for_one_day(config: Mapping[str, Any]) -> dict[str, Any]:
    return {**config, "ingest_start": datetime.today().strftime("%Y-%m-%dT%H:%M:%SZ")}


def test_single_report_request_without_pagination(requests_mock, config_pass, report_url, mock_report_response):
    requests_mock.get(url=report_url, status_code=200, json=mock_report_response)
    read_messages(config_for_one_day(config_pass))

    assert len(requests_mock.request_history) == 1


def test_parse_response(requests_mock, config_pass, report_url, mock_report_response):
    requests_mock.get(url=report_url, status_code=200, json=mock_report_response)
    config = config_for_one_day(config_pass)
    expected_parsed_record = {
        "attr_dependency": {"campaign_id_network": "unknown", "partner_id": "-300", "partner": "Organic"},
        "app": "Test app",
        "partner_name": "Organic",
        "campaign": "unknown",
        "campaign_id_network": "unknown",
        "campaign_network": "unknown",
        "installs": "10",
        "network_installs": "0",
        "network_cost": "0.0",
        "network_ecpi": "0.0",
    }
    records = [message.record.data for message in read_messages(config) if message.type == Type.RECORD]

    assert len(records) == 1
    assert sorted(records[0].keys()) == sorted(expected_parsed_record.keys())


def test_http_method(requests_mock, config_pass, report_url, mock_report_response):
    requests_mock.get(url=report_url, status_code=200, json=mock_report_response)
    read_messages(config_for_one_day(config_pass))

    assert [request.method for request in requests_mock.request_history] == ["GET"]
