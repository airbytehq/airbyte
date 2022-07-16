#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from airbyte_cdk.logger import AirbyteLogger

import pytest
import requests_mock
from source_facebook_pages.source import SourceFacebookPages
from source_facebook_pages.streams import Post

logger = AirbyteLogger()


class MockResponse:
    def __init__(self, value):
        self.value = value

    def json(self):
        return json.loads(self.value)


@pytest.fixture(name="config")
def config_fixture():
    config = {
        "access_token": "TOKEN",
        "page_id": "105762628872670",
    }

    return config


def test_check_connection_ok(config):
    with requests_mock.Mocker() as m:
        m.get(f"https://graph.facebook.com/{config['page_id']}", json={"access_token": "PAGE_TOKEN"})
        m.get(f"https://graph.facebook.com/v14.0/{config['page_id']}?access_token=PAGE_TOKEN", json={})
    
        ok, error_msg = SourceFacebookPages().check_connection(logger, config=config)

        assert ok
        assert not error_msg


def test_check_connection_empty_config():
    ok, error_msg = SourceFacebookPages().check_connection(logger, config={})

    assert not ok
    assert error_msg == 'You must provide both Access token and Page ID'


def test_check_connection_invalid_config(config):
    config.pop("page_id")
    ok, error_msg = SourceFacebookPages().check_connection(logger, config=config)

    assert not ok
    assert error_msg == 'You must provide both Access token and Page ID'


def test_check_connection_exception(config):
    with requests_mock.Mocker() as m:
        m.get(f"https://graph.facebook.com/{config['page_id']}", json={"error": {"message": "Invalid access token"}}, status_code=400)
        
        ok, error_msg = SourceFacebookPages().check_connection(logger, config=config)

        assert not ok
        assert error_msg == 'Invalid access token'


@pytest.mark.parametrize(
    "data, expected",
    [
        ('{"data":[1, 2, 3],"paging":{"cursors":{"after": "next"}}}', "next"),
        ('{"data":[1, 2, 3]}', None),
        ('{"data": []}', None),
    ],
)
def test_pagination(data, expected):
    stream = Post()
    assert stream.next_page_token(MockResponse(data)).get("after") == expected
