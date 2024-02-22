# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os

import pytest
from airbyte_cdk.utils.constants import ENV_REQUEST_CACHE_PATH

os.environ[ENV_REQUEST_CACHE_PATH] = ENV_REQUEST_CACHE_PATH


@pytest.fixture(autouse=True)
def patch_sleep(mocker):
    mocker.patch("time.sleep")


@pytest.fixture(autouse=True)
def disable_cache(mocker):
    mocker.patch("source_tiktok_marketing.streams.AdvertiserIds.use_cache", new_callable=mocker.PropertyMock, return_value=False)
