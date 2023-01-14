#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest


@pytest.fixture
def config():
    return {"api_key": "key1234567890", "base_id": "app1234567890", "tables": ["Table 1", "Table 2"]}
