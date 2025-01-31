# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os

import pytest
import responses
from airbyte_cdk.testing.proxy_cache.fixtures.auto import mitmproxy_auto
from airbyte_cdk.testing.proxy_cache.fixtures.manual import mitmproxy_cache


os.environ["REQUEST_CACHE_PATH"] = "REQUEST_CACHE_PATH"


@pytest.fixture(name="rate_limit_mock_response")
def rate_limit_mock_response():
    rate_limit_response = {
        "resources": {
            "core": {"limit": 5000, "used": 0, "remaining": 5000, "reset": 4070908800},
            "graphql": {"limit": 5000, "used": 0, "remaining": 5000, "reset": 4070908800},
        }
    }
    responses.add(responses.GET, "https://api.github.com/rate_limit", json=rate_limit_response)
