#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

from source_coda.source import SourceCoda


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception("Bad things happened")


def mocked_requests_get(fail=False):
    def wrapper(*args, **kwargs):
        if fail:
            return MockResponse(None, 404)

        return MockResponse(
            {"name": "John", "loginId": "john@example.com", "type": "user", "href": "https://coda.io/apis/v1/whoami", "tokenName": "as", "scoped": False, "pictureLink": "https://images-coda.io", "workspace":{
                "id": "test-id",
                "type": "workspace",
                "browserLink": "https://coda.io/link",
                "name": "title"
            }}, 200
        )

    return wrapper


@patch("requests.get", side_effect=mocked_requests_get())
def test_check_connection(mocker):
    source = SourceCoda()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceCoda()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 8
    assert len(streams) == expected_streams_number
