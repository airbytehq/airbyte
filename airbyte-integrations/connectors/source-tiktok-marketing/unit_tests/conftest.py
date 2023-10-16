import os

import pytest
from airbyte_cdk.utils.constants import ENV_REQUEST_CACHE_PATH

os.environ[ENV_REQUEST_CACHE_PATH] = ENV_REQUEST_CACHE_PATH


@pytest.fixture(autouse=True)
def patch_sleep(mocker):
    mocker.patch("time.sleep")
