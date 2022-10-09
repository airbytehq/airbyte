#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest


@pytest.fixture(scope="session", name="config")
def config_fixture():
    return {"X-Api-Key": "test_api_key", "workspaceId": "workspaceId"}
