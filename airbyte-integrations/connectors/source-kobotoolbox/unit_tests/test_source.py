#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import pytest
from source_kobotoolbox.source import SourceKobotoolbox


@pytest.mark.parametrize('config, err_msg', [
    (
        {"password": "some_password"},
        "username in credentials is not provided"
    ),
    (
        {"username": "username"},
        "password in credentials is not provided"
    ),
    (
        {"username": "username", "password": "some_password"},
        'Something went wrong. Please check your credentials'
    )
])
def test_check_connection(config, err_msg):
    response = SourceKobotoolbox().check_connection(logger=None, config=config)
    assert response == (False, err_msg)


@pytest.mark.parametrize('config', [
    (
        {"username": "username", "password": "some_password"}
    )
])
def test_streams(config):
    response = SourceKobotoolbox().streams(config)
    assert response == []
