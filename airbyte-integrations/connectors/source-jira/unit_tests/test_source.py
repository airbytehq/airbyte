#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
import responses

from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


@responses.activate
def test_streams(config):
    source = YamlDeclarativeSource(config=config, catalog=None, state=None, path_to_yaml=manifest_path)
    streams = source.streams(config)
    expected_streams_number = 55
    assert len(streams) == expected_streams_number


@responses.activate
def test_check_connection_config_no_access_to_one_stream(config, caplog, projects_response, avatars_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/project/search?maxResults=50&expand=description%2Clead&status=live&status=archived&status=deleted",
        json=projects_response,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/applicationrole",
        status=401,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/avatar/issuetype/system",
        json=avatars_response,
    )
    responses.add(responses.GET, f"https://{config['domain']}/rest/api/3/label?maxResults=50", status=401)
    source = SourceJira(config=config, catalog=None, state=None)
    logger_mock = MagicMock()
    assert source.check_connection(logger=logger_mock, config=config) == (True, None)


@responses.activate
def test_check_connection_404_error(config):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/project/search?maxResults=50&expand=description%2Clead&status=live&status=archived&status=deleted",
        status=404,
    )
    responses.add(responses.GET, f"https://{config['domain']}/rest/api/3/label?maxResults=50", status=404)
    source = SourceJira(config=config, catalog=None, state=None)
    logger_mock = MagicMock()
    with pytest.raises(AirbyteTracedException) as e:
        source.check_connection(logger=logger_mock, config=config)

    assert (
        e.value.message == "Config validation error: please check that your domain is valid and does not include protocol (e.g: https://)."
    )
