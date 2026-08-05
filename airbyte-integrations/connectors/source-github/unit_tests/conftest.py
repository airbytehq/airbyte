# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os
import shutil

import pytest


os.environ["REQUEST_CACHE_PATH"] = "REQUEST_CACHE_PATH"


@pytest.fixture(autouse=True)
def clear_request_cache():
    """The manifest resolver streams use `use_cache: true`, which persists HTTP
    responses in a sqlite file across tests — a cached listing from one test would
    shadow another test's mock for the same URL. Start every test with a clean cache."""
    shutil.rmtree(os.environ["REQUEST_CACHE_PATH"], ignore_errors=True)
    yield


@pytest.fixture(name="rate_limit_mock_response")
def rate_limit_mock_response(requests_mock):
    rate_limit_response = {
        "resources": {
            "core": {"limit": 5000, "used": 0, "remaining": 5000, "reset": 4070908800},
            "graphql": {"limit": 5000, "used": 0, "remaining": 5000, "reset": 4070908800},
        }
    }
    requests_mock.get("https://api.github.com/rate_limit", json=rate_limit_response)
