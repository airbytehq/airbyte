#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_rd_station_marketing.source import SourceRDStationMarketing


def test_check_connection(requests_mock, config_pass, auth_url, auth_token, segmentations_url, mock_segmentations_response):
    requests_mock.post(auth_url, json=auth_token)
    requests_mock.get(url=segmentations_url, status_code=200, json=mock_segmentations_response)
    source = SourceRDStationMarketing()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, config_pass) == (True, None)


def test_streams(requests_mock, config_pass, auth_url, auth_token, segmentations_url, mock_segmentations_response):
    requests_mock.post(auth_url, json=auth_token)
    requests_mock.get(url=segmentations_url, status_code=200, json=mock_segmentations_response)
    source = SourceRDStationMarketing()
    streams = source.streams(config_pass)
    expected_streams_number = 11
    assert len(streams) == expected_streams_number
