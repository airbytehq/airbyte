#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from unittest.mock import MagicMock

import responses

from source_fortnox.source import SourceFortnox


@responses.activate
def test_check_connection(mocker, config):
    responses.add(responses.POST, config['url'], match=[
        responses.json_params_matcher({'service': 'fortnox', 'project_code': 'org', 'package': 'default'})
    ])
    responses.add(responses.GET, "https://api.fortnox.se/3/companyinformation", json={})

    source = SourceFortnox()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, config) == (True, None)

@responses.activate
def test_check_connection_package(mocker, config_with_package):
    responses.add(responses.POST, config_with_package['url'], match=[
        responses.json_params_matcher({'service': 'fortnox', 'project_code': 'org', 'package': 'fortnox_plus'})
    ])
    responses.add(responses.GET, "https://api.fortnox.se/3/companyinformation", json={})

    source = SourceFortnox()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, config_with_package) == (True, None)


def test_streams(mocker, config):
    source = SourceFortnox()
    streams = source.streams(config)
    expected_streams_number = 14
    assert len(streams) == expected_streams_number
