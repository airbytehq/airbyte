#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_xero.source import SourceXero


def test_check_connection(mock_auth, mock_stream, mock_response, config):
    mock_stream("Organisation", response={"Organisations": [{"OrganisationID": "tenant_id"}]})
    mock_auth({"access_token": "TOKEN", "expires_in": 123})
    source = SourceXero()
    logger_mock, config_mock = MagicMock(), config
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_check_connection_failed(mock_auth, mock_stream, mock_response, config, requests_mock):
    mock_stream("Organisation", response={"Organisations": [{"OrganisationID": "tenant_id"}]})
    mock_auth({"access_token": "TOKEN", "expires_in": 123})

    requests_mock.get(url="https://api.xero.com/api.xro/2.0/Organisation", status_code=403, content= b'{"status": 403, "code": "restricted_resource"}')

    source = SourceXero()
    check_succeeded, error = source.check_connection(MagicMock(), config)
    assert check_succeeded is False
    assert 'For oauth2 authentication try to re-authenticate and allow all requested scopes' in error


def test_streams(config):
    source = SourceXero()
    streams = source.streams(config)
    expected_streams_number = 21
    assert len(streams) == expected_streams_number
