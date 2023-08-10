#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import responses

from unittest.mock import MagicMock

from source_fiserv.source import SourceFiserv, BASE_URL


def mock_success():
    responses.add(
        responses.POST,
        f"{BASE_URL}reporting/v1/reference/sites/search",
        json=[
            {
                "siteID": "dummy",
            }
        ],
    )


@responses.activate
def test_check_connection_success(mocker):
    mock_success()

    source = SourceFiserv()
    logger_mock = MagicMock()
    config_mock = {
        "start_date": "2023-08-04",
        "api_key": "api_key",
        "api_secret": "api_secret",
    }
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceFiserv()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 9
    assert len(streams) == expected_streams_number
