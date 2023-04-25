#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_genesys.source import SourceGenesys


def test_check_connection(mocker):
    source = SourceGenesys()
    logger_mock, config_mock = MagicMock(), MagicMock()
    SourceGenesys.get_connection_response = MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceGenesys()
    config_mock = MagicMock()
    config_mock.__getitem__.side_effect = lambda key: "Americas (US East)" if key == "tenant_endpoint" else None
    SourceGenesys.get_connection_response = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 16
    assert len(streams) == expected_streams_number

    expected_url_base = "https://api.mypurecloud.com/api/v2/"
    for stream in streams:
        assert stream.url_base == expected_url_base
