#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_amazon_dsp_campaign.source import SourceAmazonDspCampaign


def test_check_connection(mocker):
    source = SourceAmazonDspCampaign()
    logger_mock, config_mock = MagicMock(), MagicMock()
    
    # Valid configuration mock
    valid_config_mock = {
        'client_id': 'valid_client_id',
        'client_secret': 'valid_client_secret',
        'refresh_token': 'valid_refresh_token'
    }
    # Mocking the valid_list module to simulate valid credentials
    valid_list_mock = MagicMock()
    valid_list_mock.l = {
        'client_id': ['valid_client_id'],
        'client_secret': ['valid_client_secret'],
        'refresh_token': ['valid_refresh_token']
    }
    # Check with valid credentials
    # mocker.patch('SourceAmazonDspCampaign.source.valid_list', valid_list_mock)
    mocker.patch('source_amazon_dsp_campaign.source.valid_list', valid_list_mock)
    assert source.check_connection(logger_mock, valid_config_mock) == (True, None)

    # Invalid configuration mock
    invalid_config_mock = {
        'client_id': 'invalid',
        'client_secret': 'invalid',
        'refresh_token': 'invalid'
    }
    
    # Check with invalid credentials
    # mocker.patch('SourceAmazonDspCampaign.source.valid_list', valid_list_mock)
    mocker.patch('source_amazon_dsp_campaign.source.valid_list', valid_list_mock)
    result, error_msg = source.check_connection(logger_mock, invalid_config_mock)
    assert result == False
    assert "invalid" in error_msg

    # assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceAmazonDspCampaign()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    # TODO: replace this with your streams number
    expected_streams_number = 1
    assert len(streams) == expected_streams_number

