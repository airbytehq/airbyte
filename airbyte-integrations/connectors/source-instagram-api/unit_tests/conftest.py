# temp file change
#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

from pytest import fixture
from source_instagram_api import SourceInstagramApi


@fixture(name="source")
def source_fixture():
    return SourceInstagramApi()


@fixture(name="config")
def config_fixture():
    return {
        "access_token": "TOKEN",
    }


@fixture(name="logger")
def logger_fixture():
    return logging.getLogger("airbyte")
