#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_xero.source import SourceXero


def test_check_connection(mock_auth, mock_stream, mock_response, config):
    mock_stream("Organisation", response={"Organisations": [{"OrganisationID": "tenant_id"}]})
    mock_auth({"access_token": "TOKEN", "expires_in": 123})
    source = SourceXero()
    logger_mock, config_mock = MagicMock(), config
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(config):
    source = SourceXero()
    streams = source.streams(config)
    expected_streams_number = 21
    assert len(streams) == expected_streams_number
