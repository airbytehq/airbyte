#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from pytest import fixture


@fixture(name="config")
def config_fixture():
    config = {
        "access_token": "TOKEN",
        "start_date": "2022-03-20T00:00:00Z",
    }

    return config
