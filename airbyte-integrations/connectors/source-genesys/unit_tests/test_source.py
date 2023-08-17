#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_genesys.source import SourceGenesys
import pytest


def test_check_connection(mocker):
    source = SourceGenesys()
    logger_mock, config_mock = MagicMock(), MagicMock()
    SourceGenesys.get_connection_response = MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceGenesys()
    config_mock = MagicMock()
    SourceGenesys.get_connection_response = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 16
    assert len(streams) == expected_streams_number


@pytest.mark.parametrize(
    ("tenant_endpoint", "url_base"),
    [
        ("Americas (US East)", "https://api.mypurecloud.com/api/v2/"),
        ("Americas (US East 2)", "https://api.use2.us-gov-pure.cloud/api/v2/"),
        ("Americas (US West)", "https://api.usw2.pure.cloud/api/v2/"),
        ("Americas (Canada)", "https://api.cac1.pure.cloud/api/v2/"),
        ("Americas (São Paulo)", "https://api.sae1.pure.cloud/api/v2/"),
        ("EMEA (Frankfurt)", "https://api.mypurecloud.de/api/v2/"),
        ("EMEA (Dublin)", "https://api.mypurecloud.ie/api/v2/"),
        ("EMEA (London)", "https://api.euw2.pure.cloud/api/v2/"),
        ("Asia Pacific (Mumbai)", "https://api.aps1.pure.cloud/api/v2/"),
        ("Asia Pacific (Seoul)", "https://api.apne2.pure.cloud/api/v2/"),
        ("Asia Pacific (Sydney)", "https://api.mypurecloud.com.au/api/v2/"),
    ],
)
def test_url_base(tenant_endpoint, url_base):
    source = SourceGenesys()
    config_mock = MagicMock()
    config_mock.__getitem__.side_effect = lambda key: tenant_endpoint if key == "tenant_endpoint" else None
    SourceGenesys.get_connection_response = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 16
    assert len(streams) == expected_streams_number

    for stream in streams:
        assert stream.url_base == url_base
