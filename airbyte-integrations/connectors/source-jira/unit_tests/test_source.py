#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import responses
from source_jira.source import SourceJira


@responses.activate
def test_streams(config):
    source = SourceJira()
    streams = source.streams(config)
    expected_streams_number = 51
    assert len(streams) == expected_streams_number


@responses.activate
def test_check_connection(config, projects_response, labels_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/project/search?maxResults=50&expand=description%2Clead",
        json=projects_response,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/label?maxResults=50",
        json=labels_response,
    )
    source = SourceJira()
    logger_mock = MagicMock()

    assert source.check_connection(logger=logger_mock, config=config) == (True, None)


def test_get_authenticator(config):
    source = SourceJira()
    authenticator = source.get_authenticator(config=config)

    assert authenticator.get_auth_header() == {'Authorization': 'Basic ZW1haWxAZW1haWwuY29tOnRva2Vu'}
