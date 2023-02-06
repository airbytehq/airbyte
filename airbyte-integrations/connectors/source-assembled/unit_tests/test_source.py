#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import responses
from source_assembled.source import BASE_URL, SourceAssembled


def setup_good_response():
    responses.add(
        responses.GET,
        f"{BASE_URL}people",
        json={
            "people": {
                "b7b9aefe-597a-4dd5-b55a-9c78b1ed942d": {
                    "id": "b7b9aefe-597a-4dd5-b55a-9c78b1ed942d",
                    "agent_id": None,
                    "first_name": "Assembled",
                    "last_name": "Team",
                    "email": "test@assembledhq.com",
                    "timezone": "America/Los_Angeles",
                    "imported_id": None,
                    "role": "admin",
                    "channels": None,
                    "site": None,
                    "teams": [],
                    "queues": [],
                    "skills": [],
                    "platforms": {},
                    "start_date": None,
                    "end_date": None,
                    "created_at": 1664489241,
                    "deleted": False,
                    "staffable": False,
                    "productivity": None,
                }
            },
            "total": 1,
            "limit": 500,
            "offset": 0,
        },
    )


def setup_bad_response():
    responses.add(
        responses.GET,
        f"{BASE_URL}people",
        status=401,
    )


@responses.activate
def test_check_connection(mocker):
    setup_good_response()
    source = SourceAssembled()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (True, None)


@responses.activate
def test_check_connection_failed(mocker):
    setup_bad_response()
    source = SourceAssembled()
    logger_mock, config_mock = MagicMock(), MagicMock()
    check, msg = source.check_connection(logger_mock, config_mock)
    assert not check
    assert "Unauthorized" in msg


def test_streams(mocker):
    source = SourceAssembled()
    config_mock = {"api_key": "test_api_key", "start_date": "2021-01-01T00:00:00Z"}
    streams = source.streams(config_mock)
    expected_streams_number = 14
    assert len(streams) == expected_streams_number
