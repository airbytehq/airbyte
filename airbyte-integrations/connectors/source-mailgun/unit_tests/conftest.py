from base64 import b64encode
from typing import Dict, Any
from unittest.mock import MagicMock

import pytest
import responses


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as r:
        yield r


# @pytest.fixture
# def test_config() -> Dict[str, Any]:
#     return {
#         "private_key": "test_private_key",
#     }.copy()
#

@pytest.fixture
def auth_header(test_config):
    encoded_auth = b64encode(f"api:{test_config['private_key']}".encode()).decode()
    return {
        "Authorization": f"Basic {encoded_auth}"
    }


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
            }
        }
    )

    return response
