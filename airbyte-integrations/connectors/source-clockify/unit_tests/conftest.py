#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest


@pytest.fixture(scope="session", name="config")
def config_fixture():
    return {"api_key": "test_api_key", "workspace_id": "workspace_id"}
