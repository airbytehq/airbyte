#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pytest import fixture


@fixture
def config():
    return {"start_date": "start_date", "authenticator": None}
