#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_hydrovu.source import SourceHydrovu

import pytest
from pytest import fixture

import requests_mock
import traceback


@fixture
def config():
    return {"config": {"token_refresh_endpoint": "https://www.hydrovu.com/public-api/oauth/token", "client_id": "ABC", "client_secret": "secret", }}


def test_check_connection(mocker, requests_mock, config):
    source = SourceHydrovu()
    logger_mock, config_mock = MagicMock(), MagicMock()

    logger_mock = MagicMock()

    requests_mock.post(
        'https://www.hydrovu.com/public-api/oauth/token',
        json=
            {'access_token': 'oMRyv5kYocI60byApqhmkD5sR2I', 'token_type': 'bearer', 'expires_in': 35999, 'scope': 'read:locations read:data'}

    )

    assert source.check_connection(logger_mock, **config) == (True, None)


