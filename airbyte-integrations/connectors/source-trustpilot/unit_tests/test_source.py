#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import MagicMock

from source_trustpilot.source import SourceTrustpilot


def test_check_connection(mocker):
    source = SourceTrustpilot()
    with open('secrets/config.json') as f:
        logger_mock, config_mock = MagicMock(), json.load(f)
        assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceTrustpilot()
    config_mock = {
        'credentials': {
            'auth_type': '__api_key__',
            'client_id': '__client_id__'
        },
        'business_units': [
            'my_domain.com'
        ],
        'start_date': '2023-01-01T00:00:00Z'
    }
    streams = source.streams(config_mock)
    expected_streams_number = 2
    assert len(streams) == expected_streams_number
