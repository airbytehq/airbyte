#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest


@pytest.fixture
def config():
    return {"dataset_name": "test", "format": "json", "url": "https://airbyte.com", "provider": {"storage": "HTTPS"}}
