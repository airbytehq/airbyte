#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import responses
from pytest import fixture
from source_rd_station_marketing.source import SourceRDStationMarketing


@fixture
def test_config():
    return {
        "authorization": {
            "auth_type": "Client",
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "refresh_token": "test_refresh_token",
        },
        "start_date": "2022-01-01T00:00:00Z",
    }


def setup_responses():
    responses.add(
        responses.POST,
        "https://api.rd.services/auth/token",
        json={"access_token": "fake_access_token", "expires_in": 3600},
    )
    responses.add(
        responses.GET,
        "https://api.rd.services/platform/segmentations",
        json={
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
        },
    )


@responses.activate
def test_check_connection(test_config):
    setup_responses()
    source = SourceRDStationMarketing()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, test_config) == (True, None)


@responses.activate
def test_streams(test_config):
    setup_responses()
    source = SourceRDStationMarketing()
    streams = source.streams(test_config)
    expected_streams_number = 11
    assert len(streams) == expected_streams_number
