#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import requests
from source_persistiq.source import SourcePersistiq


def test_check_connection(mocker, requests_mock):
    source = SourcePersistiq()
    mock_logger = mocker.Mock()
    test_config = {"api_key": "mybeautifulkey"}
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
    assert source.check_connection(mock_logger, test_config) == (True, None)

    # failure
    requests_mock.get("https://api.persistiq.com/v1/users", status_code=500)
    connection_success, connection_failure = source.check_connection(mock_logger, test_config)
    assert not connection_success
    assert isinstance(connection_failure, requests.exceptions.HTTPError)


def test_streams():
    source = SourcePersistiq()
    config = {"api_key": "my-api-key"}
    streams = source.streams(config)
    assert len(streams) == 3
