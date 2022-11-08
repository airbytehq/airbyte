#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest


@pytest.fixture(scope="session", name="config")
def config_fixture():
    return {"api_token": "test_api_key", "domain_name": "example.atlassian.net", "email": "test@example.com"}
