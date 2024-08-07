#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.sources.streams import Stream
from airbyte_protocol.models import SyncMode
from jsonref import requests
from source_rd_station_marketing.source import SourceRDStationMarketing


def mock_response():
    return {
        "segmentations": [
            {
                "id": 71625167165,
                "name": "A mock segmentation",
                "standard": True,
                "created_at": "2019-09-04T18:05:42.638-03:00",
                "updated_at": "2019-09-04T18:05:42.638-03:00",
                "process_status": "processed",
                "links": [
                    {
                        "rel": "SEGMENTATIONS.CONTACTS",
                        "href": "https://api.rd.services/platform/segmentations/71625167165/contacts",
                        "media": "application/json",
                        "type": "GET",
                    }
                ],
            }
        ]
    }


def get_stream_by_name(stream_name: str, config: Mapping[str, Any]) -> Stream:
    source = SourceRDStationMarketing()
    matches_by_name = [stream_config for stream_config in source.streams(config) if stream_config.name == stream_name]
    if not matches_by_name:
        raise ValueError("Please provide a valid stream name.")
    return matches_by_name[0]


def test_request_params(config_pass):
    stream = get_stream_by_name("segmentations", config_pass)
    expected_params = {}
    assert stream.retriever.requester.get_request_params() == expected_params


def test_next_page_token(requests_mock, config_pass, auth_url, auth_token, segmentations_url):
    requests_mock.get(url=segmentations_url, status_code=200, json=mock_response())
    requests_mock.post(url=auth_url, json=auth_token)
    stream = get_stream_by_name("segmentations", config_pass)
    inputs = {"response": requests.get(segmentations_url)}
    expected_token = None
    assert stream.retriever._next_page_token(**inputs) == expected_token


def test_parse_response(requests_mock, config_pass, auth_url, auth_token, segmentations_url):
    requests_mock.get(url=segmentations_url, status_code=200, json=mock_response())
    requests_mock.post(url=auth_url, json=auth_token)
    stream = get_stream_by_name("segmentations", config_pass)
    expected_parsed_records = [
        {
            "id": 71625167165,
            "name": "A mock segmentation",
            "standard": True,
            "created_at": "2019-09-04T18:05:42.638-03:00",
            "updated_at": "2019-09-04T18:05:42.638-03:00",
            "process_status": "processed",
            "links": [
                {
                    "rel": "SEGMENTATIONS.CONTACTS",
                    "href": "https://api.rd.services/platform/segmentations/71625167165/contacts",
                    "media": "application/json",
                    "type": "GET",
                }
            ],
        }
    ]
    records = []
    for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
        records.extend(list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)))
    records.sort()
    expected_parsed_records.sort()
    assert len(records) == len(expected_parsed_records)
    for i in range(len(records)):
        assert sorted(records[i].keys()) == sorted(expected_parsed_records[i].keys())


def test_request_headers(requests_mock, config_pass, auth_url, auth_token, segmentations_url):
    requests_mock.get(url=segmentations_url, status_code=200, json=mock_response())
    requests_mock.post(url=auth_url, json=auth_token)
    stream = get_stream_by_name("segmentations", config_pass)
    inputs = {
        "stream_slice": {"slice": "test_slice"},
        "stream_state": {"updatedAt": "12-10-2024"},
        "next_page_token": {"offset": "next_page_cursor"},
    }
    assert stream.retriever.requester.get_request_headers(**inputs) == {}


def test_http_method(requests_mock, config_pass, auth_url, auth_token, segmentations_url):
    requests_mock.get(url=segmentations_url, status_code=200, json=mock_response())
    requests_mock.post(url=auth_url, json=auth_token)
    stream = get_stream_by_name("segmentations", config_pass)
    expected_method = "GET"
    assert stream.retriever.requester.http_method.value == expected_method


def test_should_retry(requests_mock, config_pass, auth_url, auth_token, segmentations_url):
    requests_mock.get(url=segmentations_url, status_code=301)
    requests_mock.post(url=auth_url, json=auth_token)
    stream = get_stream_by_name("segmentations", config_pass)
    records = []
    for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
        records.extend(list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)))
    assert records == []
    assert requests_mock.call_count == 2
