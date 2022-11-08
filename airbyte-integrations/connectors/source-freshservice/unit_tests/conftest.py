#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest


@pytest.fixture
def test_config():
    return {
        "domain_name": "test.freshservice.com",
        "api_key": "test_api_key",
        "start_date": "2021-05-07T00:00:00Z",
    }
