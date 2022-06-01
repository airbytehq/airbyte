#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from base64 import b64encode
from unittest.mock import MagicMock

import pytest
import responses

from . import TEST_CONFIG


@pytest.fixture
def test_config():
    return TEST_CONFIG.copy()


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as r:
        yield r


@pytest.fixture
def auth_header(test_config):
    encoded_auth = b64encode(f"api:{test_config['private_key']}".encode()).decode()
    return f"Basic {encoded_auth}"


@pytest.fixture
def next_page_url():
    return "next-page-url"


@pytest.fixture
def test_records():
    return [
        {"name": "Item 1"},
        {"name": "Item 2"},
    ]


@pytest.fixture
def normal_response(next_page_url, test_records):
    response = MagicMock()
    response.json = MagicMock(
        return_value={
            "items": test_records,
            "paging": {
                "next": next_page_url,
            },
        }
    )

    return response
