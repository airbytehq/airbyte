#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from requests.auth import HTTPBasicAuth


@pytest.fixture(name="config")
def config_fixture():
    return {"domain": "test.freshdesk.com", "api_key": "secret_api_key", "requests_per_minute": 50, "start_date": "2002-02-10T22:21:44Z"}


@pytest.fixture(name="authenticator")
def authenticator_fixture(config):
    return HTTPBasicAuth(username=config["api_key"], password="unused_with_api_key")
