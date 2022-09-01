#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import pytest


@pytest.fixture(scope="session")
def config():
    return {
        "url": "https://example.com",
        "project_code": "org",
        "username": "airbyte",
        "password": "air!@#byte",
        "is_dev_env": False,
        "ark_salt": "ark_salt"
    }


@pytest.fixture(scope="session")
def config_with_package():
    return {
        "url": "https://example.com",
        "project_code": "org",
        "username": "airbyte",
        "password": "air!@#byte",
        "package": "fortnox_plus",
        "ark_salt": "ark_salt"
    }