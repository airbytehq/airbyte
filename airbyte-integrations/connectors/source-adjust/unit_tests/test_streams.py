#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from typing import Any, Mapping

from airbyte_cdk.sources.streams import Stream
from airbyte_protocol.models import SyncMode
from jsonref import requests
from source_adjust.source import SourceAdjust


def get_stream_by_name(stream_name: str, config: Mapping[str, Any]) -> Stream:
    source = SourceAdjust()
    matches_by_name = [stream_config for stream_config in source.streams(config) if stream_config.name == stream_name]
    if not matches_by_name:
        raise ValueError("Please provide a valid stream name.")
    return matches_by_name[0]


def test_next_page_token(requests_mock, config_pass, report_url, mock_report_response):
    requests_mock.get(url=report_url, status_code=200, json=mock_report_response)
    stream = get_stream_by_name("AdjustReport", config_pass)
    inputs = {"response": requests.get(report_url)}
    expected_token = {}
    assert stream.retriever._next_page_token(**inputs) == expected_token


def test_parse_response(requests_mock, config_pass, report_url, mock_report_response):
    requests_mock.get(url=report_url, status_code=200, json=mock_report_response)
    stream = get_stream_by_name("AdjustReport", config_pass)
    expected_parsed_record = {
        "attr_dependency": {
            "campaign_id_network": "unknown",
            "partner_id": "-300",
            "partner": "Organic"
        },
        "app": "Test app",
        "partner_name": "Organic",
        "campaign": "unknown",
        "campaign_id_network": "unknown",
        "campaign_network": "unknown",
        "installs": "10",
        "network_installs": "0",
        "network_cost": "0.0",
        "network_ecpi": "0.0"
    }
    records = []
    for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
        records.extend(list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)))
    days_difference = (datetime.today() - datetime.strptime(config_pass["ingest_start"], "%Y-%m-%dT%H:%M:%SZ")).days
    assert len(records) == days_difference + 1
    assert sorted(records[0].keys()) == sorted(expected_parsed_record.keys())


def test_request_headers(requests_mock, config_pass, report_url, mock_report_response):
    requests_mock.get(url=report_url, status_code=200, json=mock_report_response)
    stream = get_stream_by_name("AdjustReport", config_pass)
    inputs = {
        "stream_slice": None,
        "stream_state": None,
        "next_page_token": None,
    }
    assert stream.retriever.requester.get_request_headers(**inputs) == {}


def test_http_method(requests_mock, config_pass, report_url, mock_report_response):
    requests_mock.get(url=report_url, status_code=200, json=mock_report_response)
    stream = get_stream_by_name("AdjustReport", config_pass)
    expected_method = "GET"
    assert stream.retriever.requester.http_method.value == expected_method
