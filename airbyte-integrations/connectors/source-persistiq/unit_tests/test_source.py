#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import ANY, MagicMock

from source_persistiq.source import SourcePersistiq


def test_check_connection(mocker, requests_mock):
    source = SourcePersistiq()
    logger_mock = MagicMock(), MagicMock()
    config_mock = {"api_key": "mybeautifulkey"}
    # success
    requests_mock.get(
        "https://api.persistiq.com/v1/users",
        json={
            "id": "u_3an2Jp",
            "name": "Gabriel Rossmann",
            "email": "gabriel@punctual.cc",
            "activated": "true",
            "default_mailbox_id": "mbox_38ymEp",
            "salesforce_id": "",
        },
    )
    assert source.check_connection(logger_mock, config_mock) == (True, None)

    # failure
    requests_mock.get("https://api.persistiq.com/v1/users", status_code=500)
    assert source.check_connection(logger_mock, config_mock) == (False, ANY)


def test_streams(mocker):
    source = SourcePersistiq()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 3
    assert len(streams) == expected_streams_number
