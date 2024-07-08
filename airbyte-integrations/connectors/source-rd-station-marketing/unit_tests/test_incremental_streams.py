#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from source_rd_station_marketing.source import SourceRDStationMarketing


def mock_response():
    return {
        "account_id": 3127612,
        "query_date": {
            "start_date": "2024-06-22",
            "end_date": "2024-06-22"
        },
        "assets_type": "[LandingPage]",
        "conversions": [
            {
                "asset_id": 1495004,
                "asset_identifier": "Como aumentar suas taxas de conversão",
                "asset_type": "LandingPage",
                "asset_created_at": "2022-06-30T19:11:05.191Z",
                "asset_updated_at": "2022-06-30T20:11:05.191Z",
                "visits_count": 1500,
                "conversions_count": 150,
                "conversion_rate": 10
            }
        ]
    }
    # return {"updated_time": "2021-10-22"}


def get_stream_by_name(stream_name: str, config: Mapping[str, Any]) -> Stream:
    source = SourceRDStationMarketing()
    matches_by_name = [stream_config for stream_config in source.streams(config) if stream_config.name == stream_name]
    if not matches_by_name:
        raise ValueError("Please provide a valid stream name.")
    return matches_by_name[0]


def test_cursor_field(config_pass):
    stream = get_stream_by_name("analytics_conversions", config_pass)
    expected_cursor_field = "asset_updated_at"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(requests_mock, config_pass, auth_url, auth_token, analytics_conversions_url):
    requests_mock.get(url=analytics_conversions_url, status_code=200, json=mock_response())
    requests_mock.post(url=auth_url, json=auth_token)
    stream = get_stream_by_name("analytics_conversions", config_pass)
    stream.state = {"asset_updated_at": "2022-01-01T00:00:00.000Z"}
    records = []
    for stream_slice in stream.stream_slices(sync_mode=SyncMode.incremental):
        for record in stream.read_records(sync_mode=SyncMode.incremental, stream_slice=stream_slice):
            record_dict = dict(record)
            records.append(record_dict)
            new_stream_state = record_dict.get("asset_updated_at")
            stream.state = {"asset_updated_at": new_stream_state}
    expected_state = {"asset_updated_at": "2022-06-30T20:11:05.191Z"}
    assert stream.state == expected_state


def test_stream_slices(requests_mock, config_pass, auth_url, auth_token, analytics_conversions_url):
    requests_mock.get(url=analytics_conversions_url, status_code=200, json=mock_response())
    requests_mock.post(url=auth_url, json=auth_token)
    stream = get_stream_by_name("analytics_conversions", config_pass)
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": ["asset_updated_at"],
              "stream_state": {"updatedAt": "2022-05-01T00:00:00.000Z"}}
    assert stream.stream_slices(**inputs) is not None


def test_supports_incremental(config_pass):
    stream = get_stream_by_name("analytics_conversions", config_pass)
    assert stream.supports_incremental


def test_source_defined_cursor(config_pass):
    stream = get_stream_by_name("analytics_conversions", config_pass)
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(config_pass):
    stream = get_stream_by_name("analytics_conversions", config_pass)
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
