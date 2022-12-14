#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from pytest import fixture
from source_zendesk_sell.source import SourceZendeskSell


@fixture
def config():
    return {"config": {"user_auth_key": "", "start_date": "2021-01-01T00:00:00Z", "outcome_names": ""}}


def test_check_connection(mocker, requests_mock, config):
    source = SourceZendeskSell()
    logger_mock, config_mock = MagicMock(), MagicMock()
    requests_mock.get("https://api.getbase.com/v2/contacts", json={"items": [{"data": {}}]})

    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceZendeskSell()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 23
    assert len(streams) == expected_streams_number
